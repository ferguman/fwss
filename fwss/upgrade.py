from base64 import b64decode, b64encode
from enum import Enum
from hashlib import sha1
from http import HTTPStatus
import logging

# from fwss.settings import ALLOW_NULL_SUB_PROTOCOLS
from config import get_config
from fwss.utility import log_print


class Upgrade():

   def __init__(self): 

      # Client opening handshake
      self.opening_handshake_headers = None

      # Server opening handshake -> These data structures are populated while parsing the
      # the opening handshake from the client.
      # abort              boolean
      # http_status_code   HTTPStatus
      # headers            dictionary of headers 
      self.server_opening_handshake = {}
      self.server_opening_handshake['abort'] = True
      self.server_opening_handshake['headers'] = {}
      self.server_opening_handshake['http_status_code'] = None 

   def is_valid_get_request(self, data):

      first_line_parts = data.split(' ', 4)

      if (len(first_line_parts) != 3):
         print('First line of request must consist of 3 space delimited parts')
         return False
      
      if (first_line_parts[0] != 'GET'): 
          print('Must be a GET request')
          return False

      # https://www.websocket.org/echo.html uses ?encoding=text
      # TODO figure out what is up with /encoding=text
      if (not (first_line_parts[1] == '/wss/' or first_line_parts[1] == '/wss/?encoding=text')):
          #TODO - add ability to conifgure one or more legal resources and
          #       updated the code to check against that list
          logging.warning('This server only supports the /wss/ resource')
          self.server_opening_handshake['http_status_code'] = HTTPStatus.NOT_FOUND
          self.server_opening_handshake['abort'] = True
          return False

      if (first_line_parts[2] != 'HTTP/1.1'):
         print('This server only supports HTTP/1.1')
         return False

      return True


   #TODO:  Make the max number of headers and max line length configuration items, so that users can tune them if necessary.
   def extract_headers(self, lines:"array of request lines") -> dict:
      self.opening_handshake_headers = None 
      headers = {}
      line_count = 0
      for line in lines:

          # Don't accept a lot of headers
          if line_count > 30:
             print('This implementation does not accept more than 30 headers. Change the code if necessary to accept more.')
             return False 
          # Don't accept hugely long lines
          if len(line) > 4000:
             print('This implementation does not accept lines longer than 4000. Change the code if necessary to accept more.')
             return False 

          line_parts = line.strip().split(':', maxsplit=1 )
          if (len(line_parts) != 2):
             print('illegal header {}... -> must be 2 parts when split on :'.format(log_print(line)))
             return False 

          # Store same named header rows in an array within the dictionary
          key = line_parts[0].strip().lower() 
          if key in headers:
             if isinstance(headers[key],list):
                headers[key].append(line_parts[1].strip())
             else:
                header_list = []
                header_list.append(headers[key])
                header_list.append(line_parts[1].strip())
                headers[key] = header_list
          else:
              headers[key] = line_parts[1].strip()

          line_count = line_count + 1

      self.opening_handshake_headers = headers 
      return True 

   def read_client_opening_handshake(self):
      # Root through the header dictionary and see if you can put together a valid Web Socket opening handshake.

      print(self.opening_handshake_headers)
      if not 'host' in self.opening_handshake_headers:
         logging.warning('No host header found')
         
      #TODO - make the allowed host white list a configuration item
      if not self.opening_handshake_headers['host'] == '127.0.0.1:8888':
          logging.warning('The only allowed hosts are: 127.0.0.1:8888')
          return False
      
      if not ('upgrade' in self.opening_handshake_headers and self.opening_handshake_headers['upgrade'].lower() == 'websocket'):
          logging.warning('One and only one upgrade host header with a value of websocket was not found') 
          return False
      
      if not ('connection' in self.opening_handshake_headers and self.opening_handshake_headers['connection'].lower() == 'upgrade'):
          logging.warning('One and only one connection host header with a value of upgrade was not found') 
          return False

      if ('sec-websocket-key' in self.opening_handshake_headers and isinstance(self.opening_handshake_headers['sec-websocket-key'], str)):
          try:
             self.sec_websocket_key_decoded = b64decode(self.opening_handshake_headers['sec-websocket-key'], validate=True)
             if len(self.sec_websocket_key_decoded) == 16:
                pass
             else:
                logging.warning('sec-websocket-key ({} bytes long) must be 16 bytes long.'.format(len(self.sec_websocket_key_decoded)))
                return False
          except Exception as ex:
             logging.warning('{}'.format(ex))
             logging.warning('sec-websocket-key header value: {} cannot be b64 decoded.'.format(log_print(self.opening_handshake_headers['sec-websocket-key']))) 
             return False
      else:
          logging.warning('One and only one sec-websocket-key host header was not found') 
          return False

      if not ('sec-websocket-version' in self.opening_handshake_headers):
          logging.warning('No sec-websocket-version header found.')
          return False
         
      if ('origin' in self.opening_handshake_headers):
          logging.info('orgin header {} found'.format(log_print(self.opening_handshake_headers['origin'])))
          # TODO - Implement origin enforcement here

      return True 

   def make_server_opening_handshake(self):

      # This server only understands version 13 of the websocket protocol
      if not (self.opening_handshake_headers['sec-websocket-version'] == '13'):
         logging.warning('sec-websocket-version host header version was not 13') 
         self.server_opening_handshake['http_status_code'] = HTTPStatus.UPGRADE_REQUIRED
         self.server_opening_handshake['headers']['Sec-WebSocket-Version'] = '13'
         self.server_opening_handshake['abort'] = True
         return False

      #TODO: Add the sub-protocol negotiation here.
      # See RFC 6455 page(s): 18, 23, 58
      # Map the null header field to the console.urbanspacefarms.com application
      # The sub-protocol list may be sent on one header field as a comma seperated list or it may
      # be sent as multiple sub-protocoal headers. 
      # This implementation does not accept a mixture of the above.
      # 	
      if not 'sec-websocket-protocol' in self.opening_handshake_headers:
         if get_config().ALLOW_NULL_SUB_PROTOCOLS:
             # Do not return a sub-protocol header to the client. This signals the acceptance of a connection with no sub-protocol specified.
             pass 
         else:
            logging.error('No sub-protocal header was detected. fwss is configured to require the Sec-WebSocket-Protocol header in the client handshake.') 
            return False
      # else
      #    if one header field present
      #       foreach sub-filed (comma seperated)
      #          if sub filed values are less than configuration max length, not blank, and contain only characters in rage U+0021 to U+007E then
      #             add sub filed to ordered list of sub protocols
      #          else
      #             log an error -> sub-protocol is too long, or is blank, or contains illegal characters
      #             return False
      #   else
      #      foreach sub protocol header
      #         if header value is less than configuration max length, not blank, does not contain a comma, and contain only characters in rage U+0021 to U+007E then
      #            add sub field to ordered list of sub-protocols
      #         else
      #            log an error -> sub-protocol is too long, or is blank, or contains illegal characters, or there is a header field list and seperate headers
      #                            which this implemenatation does not allow.
      #            return False
      #  At this point we have non-empty protocol list
      #  debug log the list of of sub-protocols contained in the handshake
      #   foreaach protocol - iterate them in order from first to last - See RFC 6455 page 18 paragraph 10. 
      #   if sub-protocoal is acceptabel to this instance
      #      set server handshake header value this sub-protocol value
      #         return True
      #

      #TODO: Add the extenstion processing here. For now leave the extension header out of hte response but in the future
      #      add processing to look at the client extensions that are requested and from the client's list parrot back
      #      the extensions that are supported by this server.
      
      self.server_opening_handshake['headers']['Connection'] = 'Upgrade'
      self.server_opening_handshake['headers']['Upgrade'] = 'websocket'

      # TODO - need a way to test this algorthim
      accept_nonce = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
      presha1 = self.opening_handshake_headers['sec-websocket-key'].encode('utf-8') + accept_nonce
      #- logging.debug(f'pre-sha1: {presha1}')
      sha1_ = sha1(presha1).digest()
      #- logging.debug(f'sha1: {sha1_}')
      # decode() converts the bytes object to a string encoded as utf-8 data.
      self.server_opening_handshake['headers']['Sec-WebSocket-Accept'] = b64encode(sha1_).decode('utf-8')

      self.server_opening_handshake['http_status_code'] = HTTPStatus.SWITCHING_PROTOCOLS

      return True


   def read_client_upgrade_request(self, data):
      
      # Create an array containing each line of the request.
      # Note that after the split there should be two blank lines at the end.
      # Arbitrarily cap it at 100 lines.
      self.request_lines = data.split('\r\n', 101)

      # TODO - Logo an error if there is too much data in the request.
      # TODO - Log an error if there are not two blank lines at the end of the input

      if not self.is_valid_get_request(self.request_lines[0]):
         logging.info('Not a valid upgrade request')
         return False

      # Parse the header fields into a dictionary.
      if not self.extract_headers(self.request_lines[1:-2]):
         logging.info('Cannot extract headers')
         return False
      
      # At this point we have verifid the get request and we have all the headers in a dictionary.
      # TODO - Add the security checks here. Start with a flat file holding encrypted usernames and encrytped passwords. 
      #        Actually security should be imposed before any processing is done so move this stuff to
      #        to be sooner in the process.


      # The Web Socket specification allows for HTTP level authentication however the Javascript API (see:
      # https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) does not appear to support setting authenticationg
      # data as part of the connection process. 
      # See https://stackoverflow.com/questions/4361173/http-headers-in-websockets-client-api for more information.
      # 
      #
      # TODO - Cookies would work fine I think assuming the client is logged onto a website that has set a cookie 
      #        ahead of time and such cookie can be inspected by the websocket server.
      # 
      # TODO - A JWT passed via a bearer header would also work.
      #
      if not self.read_client_opening_handshake():
         logging.info('Not a valid opening handshake')
         return False

      # At this point we have a reasonable client handshake. We may still abort the connection but
      # we will go ahead and build the server's handshake and during that build if need be an abort will
      # be indicated. Note an abort may have a response and always closes the TCP/IP connection.
      if not self.make_server_opening_handshake():
         return False 

      self.server_opening_handshake['abort'] = False
      return True 

   def make_response(self):

      if 'abort' in self.server_opening_handshake and self.server_opening_handshake['abort'] == False:
         self.close = False
         logging.debug('Leave client socket open')
      else:
         self.close = True
         logging.debug('Close the client socket')

      if 'http_status_code' in self.server_opening_handshake:
         self.response = 'HTTP/1.1 {} {}\r\n'.format(self.server_opening_handshake['http_status_code'].value,
                                                     self.server_opening_handshake['http_status_code'].phrase).encode('utf-8')
      else:
         self.response = b'HTTP/1.1 501 Not Implemented\r\n'
 
      if 'headers' in self.server_opening_handshake:
         for key, value in self.server_opening_handshake['headers'].items():
             if isinstance(value, list):
                for header_value in value:
                   self.response = self.response + '{}: {}\r\n'.format(key, header_value).encode('utf-8')
             else:
                self.response = self.response + '{}: {}\r\n'.format(key, value).encode('utf-8')

      self.response = self.response + b'\r\n'

      logging.info('response: {!r}'.format(self.response))
