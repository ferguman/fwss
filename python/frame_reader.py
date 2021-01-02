import logging
from enum import Enum

class FrameParts(Enum):
   FIN = 1
   MASK = 2

class FrameReader():

   def __init__(self, connection):
      self.connection = connection
      self.extension_data = None
      self.application_data = None
      self.next_expected_frame_part = FrameParts.FIN
      self.close = False 
      self.final_fragment = None
      self.extension_code = None

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
         if not self.connection['is_valid_extension'](self.extension_code):
            logging.error('Invalid extension code. Will close the connection')
            self.close = True
            return

         #TODO - at this point you need to extract the opcode

         self.next_expected_frame_part = FrameParts.MASK

