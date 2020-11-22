# wsc -> Web Socket Controller
from enum import Enum

class Wsc():

   states = Enum('states', 'WAITING_FOR_UPGRADE_REQUEST UPGRADED') 

   def __init__(self): 
      self.state = Wsc.states.WAITING_FOR_UPGRADE_REQUEST 

   def is_valid_get_request(self, data):

      first_line_parts = data.split(' ', 4)

      if (len(first_line_parts) != 3):
         print('First line of request must consist of 3 space delimited parts')
         return False
      
      if (first_line_parts[0] != 'GET'): 
          print('Must be a GET request')
          return False

      if (first_line_parts[1] != '/wss/'):
          #TODO - add ability to conifgure one or more legal resources and
          #       updated the code to check against that list
          print('This server only supports the /wss/ resource name')
          return False

      if (first_line_parts[2] != 'HTTP/1.1'):
         print('This server only supports HTTP/1.1')
         return False

   def is_valid_connection_request(self, data):
      
      # Create an array containing each line of the request.
      # Note that after the split there should be two blank lines at the end.
      # Arbitrarily cap it at 100 lines.
      self.request_lines = data.split('\r\n', 101)

      # TODO - Log an error if 101 lines were found. Test using 3 line max length
      # TODO - Logo an error if there is too much data in the request.
      # TOTO - Log an error if there are not two blank lines at the end of the input

      #- print("{} lines found in the request".format(len(self.request_lines)))
      #- print(['{}'.format(var) for var in self.request_lines])
      #- print('\r\n')

      if(not self.is_valid_get_request(self.request_lines[0])):
         return False

      # TODO parse the header fields into a dictionary at this point. 
      

      return False

   def process_data(self, message):

        print('State: {}'.format(self.state))

        if (self.state == Wsc.states.WAITING_FOR_UPGRADE_REQUEST):
           if self.is_valid_connection_request(message):
              # send the websocket upgrade successful response.
              self.response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
              print('response: {!r}'.format(self.response))
              #- self.transport.write(response)
              print('Close the client socket')
              self.close = True
              #- self.transport.close()
           else:
              self.response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
              print('response: {!r}'.format(self.response))
              #- self.transport.write(response)
              print('Close the client socket')
              self.close = True
              #- self.transport.close()
        else:
           # TODO - Implement the other states 
           #Send a failure response
           self.response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
           print('response: {!r}'.format(self.response))
           #- self.transport.write(response)
           print('Close the client socket')
           self.close = True
           #- self.transport.close()
