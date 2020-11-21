class ws_parser():

   def is_valid_connection_request(self, data):
      
      # Create an array containing each line of the request.
      # however this will result in 
      self.request_lines = []
      # Note that after the split there should be two blank lines at the end.
      # Arbitrarily cap it at 100 lines.
      self.request_lines = data.split('\r\n', 101)

      # TODO - Log an error if 101 lines were found. Test using 3 line max length

      print("{} lines found in the request".format(len(self.request_lines)))
      print(['{}'.format(var) for var in self.request_lines])

      # return 'GET /wss/ HTTP/1.1\r\n' == request
      print('\r\n')
      return False
