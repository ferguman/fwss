import logging
from enum import Enum, IntEnum

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
      self.close = False 
      self.final_fragment = None
      self.extension_code = None
      self.opcode = None

      #build the opcode list 

   def process_byte(self, next_byte):

      logging.debug(f'byte: {next_byte}')

      current_byte = next_byte[0] # get the byte out of the byte string within which it is wrapped

      # 1st byte processing includes FIN, RSVX, and Opcode
      if self.next_expected_frame_part == FrameParts.FIN:

         logging.debug(f'FIN:{current_byte >> 7}')
         if (current_byte >> 7) == 1:
            self.final_fragment = True 
         else:
            self.final_fragment = False

         self.extension_code = (current_byte & 7) >> 4
         logging.debug(f'RSVX: {self.extension_code}')
         # At this point we must make sure that the extension code is one that has been negotiated.
         # See RFC 6455 page 28
         #- if not self.connection['is_valid_extension'](self.extension_code):
         if not self.wsc.is_valid_extension(self.extension_code):
            logging.error('Invalid extension code. Will close the connection')
            self.wsc.close = True
            return

         if (current_byte & 0xf) in Opcodes.__members__.values():
            self.opcode = (Opcodes) (current_byte & 0xf)
            logging.debug(f'opcode: {self.opcode}, {self.opcode == Opcodes.TEXT_FRAME}')
         else:
            logging.error(f'Unknown opcode: {current_byte & 0xf}. Will close the connection')
            self.wsc.close = True
            return

         self.next_expected_frame_part = FrameParts.MASK
         return

      if self.next_expected_frame_part is FrameParts.MASK:
         # TODO - this code assumes that it always the server.
         if current_byte & 0x80 == 0x80:
            self.mask = True
         else:
            logging.error(f'Unmasked frame received. This implementation only accepts client frames, which must be masked.')
            self.wsc.close = True
            return

         if (current_byte & 0x7f) < 126:
            self.number_of_pending_extended_payload_length_bytes = 0
            self.payload_data_length = current_byte & 0x7f
            logging.debug(f'payload length: {self.payload_data_length}')
            self.next_expected_frame_part = FrameParts.MASKING_KEY
            self.number_of_pending_masking_key_bytes = 4
         elif (current_byte & 0x7f) ==  126:
            self.number_of_pending_extended_payload_length_bytes = 2
            self.next_exptected_frame = FrameParts.EXTENDED_PAYLOAD_LENGTH
         else :
            self.number_of_pending_extended_payload_length_bytes = 8
            self.next_exptected_frame = FrameParts.EXTENDED_PAYLOAD_LENGTH

         logging.debug(f'Expecting {self.number_of_pending_extended_payload_length_bytes} extended payload length bytes')
         return

      #TODO - implement masking key read
