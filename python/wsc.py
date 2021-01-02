# wsc -> Web Socket Controller

import logging

from python.frame_reader import FrameReader
from python.upgrade import Upgrade

class Wsc():

   def __init__(self, connection): 

      self.upgrade = Upgrade()
      self.frame_reader = FrameReader(connection)
      self.close = False 
      self.response = None

   def process_upgrade_request(self, request):
      # Scan the client request and if the request is valid then values will be
      # set in self.server_opening_handshake. The scanning process is halted at the first error found.
      # If no values are set in self.server_opening_handshake then the 501 Not Implemented response
      # should be returned.
      
      #- self.read_client_upgrade_request(request)
      self.upgrade.read_client_upgrade_request(request)

      logging.debug(f'abort: {self.upgrade.server_opening_handshake["abort"]}')
      logging.debug(f'http status code: {self.upgrade.server_opening_handshake["http_status_code"]}')
      logging.debug(f'headers: {self.upgrade.server_opening_handshake["headers"]}')

      # Scan the values in self.server_opening_handshake and create the appropriate HTTP response. 
      #- self.make_response()  
      self.upgrade.make_response()  
      self.close = self.upgrade.close
      self.response = self.upgrade.response
      # At this point if we need to negotiate the upgrade we leave self.upgrade in place otherwise
      # we set it to None. You get one upgrade per session.

   def process_byte(self, next_byte):
      # log a byte
      self.frame_reader.process_byte(next_byte)
      self.close = self.frame_reader.close

