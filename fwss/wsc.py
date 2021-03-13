# wsc -> Web Socket Controller
# See https://www.websocket.org/echo.html for a tool to do websocket connections

from enum import Enum
import logging

from fwss.frame_reader import FrameReader
from fwss.upgrade import Upgrade

# The Javascript API has the following connection state constants defined: 
# CONNECTING, OPEN, CLOSING, CLOSED
# Consider renamed WATING_FOR_UPGRADE_REQUEST to CLOSED.
#
class WebSocketConnectionStates(Enum):
   WAITING_FOR_UPGRADE_REQUEST = 1
   OPEN = 2                           # OPEN -> See page 25 of RFC 6455

class Wsc():

   def __init__(self, call_backs): 

      self.state = WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST 
      self.upgrade = Upgrade()
      self.frame_reader = FrameReader(self)
      self.close = False 
      self.response = None
      self.payload = None
      self.current_line = '' 

      self.websocket_callbacks = call_backs

   def append_to_payload(self, byte_to_append):
      if self.payload:
         self.payload.append(byte_to_append) 
      else:
         self.payload = bytearray(chr(byte_to_append), 'utf-8')

   def process_upgrade_request(self, request):
      # Scan the client request and if the request is valid then values will be
      # set in self.server_opening_handshake. The scanning process is halted at the first error found.
      
      self.upgrade.read_client_upgrade_request(request)

      logging.debug(f'abort: {self.upgrade.server_opening_handshake["abort"]}')
      logging.debug(f'http status code: {self.upgrade.server_opening_handshake["http_status_code"]}')
      logging.debug(f'headers: {self.upgrade.server_opening_handshake["headers"]}')

      # Enforce security
      # TODO refactor upgrade class to contin the folowwing method. Then
      # implement the PLAIN_TEXT_PASSCODE security sub-protocol. 
      self.upgrade.enforce_security()

      # The Upgrade object contains the results of processing the upgrade request in including the server response.
      self.upgrade.make_response()  
      self.close = self.upgrade.close
      self.response = self.upgrade.response
      # At this point if we need to negotiate the upgrade we leave self.upgrade in place otherwise
      # we set it to None. You get one upgrade per session.

   def process_byte(self, next_byte):
      # log a byte
      # TODO - put a state machine here that looks for start and ends of frames and hanldes the FIN bit
      #        it alos needs to pass frame data to the awaiting clients.
      #

      # Send the current byte to the frame reader. If the frame reader sees that it is a payload
      # byte then it will return it other wise it will return nothing.
      #+ logging.debug(f'next_byte: {next_byte}')
      payload_byte = self.frame_reader.process_byte(next_byte)

      #- if payload_byte and self.websocket_callbacks['echo']:
      if payload_byte and 'echo' in self.websocket_callbacks:
         self.websocket_callbacks['echo'](payload_byte)

      if payload_byte and 'line_reader' in self.websocket_callbacks:
         # Look for the \n character.
         if payload_byte == 0x0a:
            self.websocket_callbacks['line_reader'](self.current_line)
            self.current_line = '' 
         else:
            self.current_line = self.current_line + chr(payload_byte)

   def is_valid_extension(self, extension_code):
      logging.info('TODO - Implement extension validity checker')
      return True
