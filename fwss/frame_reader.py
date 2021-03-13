import logging
from enum import Enum, IntEnum
from sys import exc_info

# Frame reader is a state machine that accepts an incoming frame on a sequential stream
# of bytes and extracts the various frame parts. 
# Frame reader can close the connection at any time by setting the close property of 
# its wsc reference.

class FrameParts(Enum):
   FIN = 1
   MASK = 2
   MASKING_KEY = 3
   EXTENDED_PAYLOAD_LENGTH = 4
   PAYLOAD_DATA = 5

class Opcodes(IntEnum):
   CONTINUATION_FRAME = 0x0
   TEXT_FRAME = 0x1
   BINARY = 0x2
   CONNECTION_CLOSE = 0x8
   PING = 0x9
   PONG = 0xA

class FrameReader():

   def __init__(self, wsc):
      self.wsc = wsc 
      self.extension_data = None
      self.application_data = None
      self.next_expected_frame_part = FrameParts.FIN
      self.final_fragment = None
      self.extension_code = None
      self.opcode = None
      self.mask = False
      self.masking_key = None 
      self.payload_byte_index = 0


   def parse_first_frame_byte(self, current_byte):

      logging.debug(f'FIN:{current_byte >> 7}')
      if (current_byte >> 7) == 1:
         self.final_fragment = True 
      else:
         self.final_fragment = False

      self.extension_code = (current_byte & 7) >> 4
      logging.debug(f'RSVX: {self.extension_code}')
      # At this point we must make sure that the extension code is one that has been negotiated.
      # See RFC 6455 page 28
      if not self.wsc.is_valid_extension(self.extension_code):
         logging.error('Invalid extension code. Will close the connection')
         self.wsc.close = True
         return

      if (current_byte & 0xf) in Opcodes.__members__.values():
         self.opcode = (Opcodes) (current_byte & 0xf)
         logging.debug(f'opcode: {Opcodes(current_byte & 0xf).name}')
      else:
         logging.error(f'Unknown opcode: {current_byte & 0xf}. Will close the connection')
         self.wsc.close = True
         return

      self.next_expected_frame_part = FrameParts.MASK
      return

   def parse_mask_bit_and_payload_length(self, current_byte):

      # TODO - this code assumes that it always the server recieving bytes from a client and thus
      #        the connection is closed if an unmasked payload is received.
      if current_byte & 0x80 == 0x80:
         self.mask = True
         logging.debug('payload is masked')
         self.number_of_pending_masking_key_bytes = 4
      else:
         self.number_of_pending_masking_key_bytes = 0
         logging.error(f'Unmasked frame received. This implementation only accepts client frames, which must be masked.')
         self.wsc.close = True
         return

      if (current_byte & 0x7f) < 126:
         self.number_of_pending_extended_payload_length_bytes = 0
         self.payload_data_length = current_byte & 0x7f
         logging.debug(f'payload length: {self.payload_data_length}')
         if self.mask:
            self.next_expected_frame_part = FrameParts.MASKING_KEY
         else:
            self.next_expected_frame_part = PAYLOAD_DATA
         self.number_of_pending_masking_key_bytes = 4
      elif (current_byte & 0x7f) ==  126:
         self.number_of_pending_extended_payload_length_bytes = 2
         self.payload_data_length = 0 
         self.next_expected_frame_part = FrameParts.EXTENDED_PAYLOAD_LENGTH
      else :
         self.number_of_pending_extended_payload_length_bytes = 8
         self.payload_data_length = 0 
         self.next_expected_frame_part = FrameParts.EXTENDED_PAYLOAD_LENGTH

      logging.debug(f'Expecting {self.number_of_pending_extended_payload_length_bytes} extended payload length bytes')
      return

   def parse_extended_payload_length_byte(self, current_byte):

      self.payload_data_length = self.payload_data_length * 0x100 + current_byte
      self.number_of_pending_extended_payload_length_bytes -= 1
      if self.number_of_pending_extended_payload_length_bytes <= 0:
         if self.mask:
            self.next_expected_frame_part == FrameParts.MASKING_KEY
         else:
            self.next_expected_frame_part = FrameParts.PAYLOAD_DATA
      return


   def parse_masking_key_byte(self, next_byte):

      if self.masking_key:
         # Store the masking key as a byte string of ultimate length 4.
         self.masking_key = self.masking_key + next_byte
      else:
         self.masking_key = next_byte
      self.number_of_pending_masking_key_bytes -= 1
      if self.number_of_pending_masking_key_bytes <= 0:
         logging.debug(f'masking key: {self.masking_key}') 
         self.next_expected_frame_part = FrameParts.PAYLOAD_DATA

      return

   def parse_payload_byte(self, current_byte):

      if self.mask:
         unmasked_byte = self.masking_key[self.payload_byte_index % 4] ^ current_byte 
      else:
         unmasked_byte = current_byte

      self.payload_byte_index += 1
      if self.payload_byte_index >= self.payload_data_length:

         # End of frame - start looking for the start of another frame.
         self.final_fragment = None
         self.extension_code = None
         self.opcode = None
         self.mask = False
         self.masking_key = None 
         self.payload_byte_index = 0
         self.next_expected_frame_part = FrameParts.FIN

         #- logging.debug(f'payload: {self.wsc.payload}')

      return unmasked_byte

   def process_byte(self, next_byte):

      try:
         # TODO rename next_byte to incoming_byte_as_byte_string.
         # TODO rename current_byte to incoming_byte_as_int
         #+ logging.debug(f'byte: {next_byte}')
         current_byte = next_byte[0] # get the byte out of the byte string within which it is wrapped

         # 1st byte processing includes FIN, RSVX, and Opcode
         if self.next_expected_frame_part == FrameParts.FIN:
            return self.parse_first_frame_byte(current_byte)

         # Process the Mask bit and the 7 bit payload length and size indicator.
         if self.next_expected_frame_part is FrameParts.MASK:
            return self.parse_mask_bit_and_payload_length(current_byte)

         # TODO - Need to test extended payloads.
         # Capture the extended payload length (if present) one byte a time.
         if self.next_expected_frame_part == FrameParts.EXTENDED_PAYLOAD_LENGTH:
            return self.parse_extended_payload_length_byte(current_byte)

         # Capture the masking key. Masking key if present is 4 bytes long. Clients must
         # mask payload data they is sent from client.
         if self.next_expected_frame_part == FrameParts.MASKING_KEY:
            return self.parse_masking_key_byte(next_byte)

         # Read payload data one byte at a time as it comes in on the stream.
         if self.next_expected_frame_part == FrameParts.PAYLOAD_DATA:
            return self.parse_payload_byte(current_byte)

      #TODO - need to figure out what happens here. any code that gets here is an error. the wsc should be
      #       telling this reader what state to go to or maybe teh read just goes to the start frame state 
      #       and is happy just and only to do that over and over.

      except:
         # close the connection.
         logging.error(f'exception in process_byte: {exc_info()[0]}, {exc_info()[1]}')
         self.wsc.close = True
