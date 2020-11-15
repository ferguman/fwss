import asyncio

# TODO - Create an MQTT client.
# Maintain a list of subscribers and the topic that they want to subsribe  on
# or publish on.
# | subscriber                         | topic                      | pub   | sub   | credentials | 
# | the echo server that is subscribed | the topic e.g. /fs1/events | queue | queue | credentials |
#
# Will need to listen for incoming and outgoing commands
# Cmds -> 
#    sub(topic, credentials) -> can do, queue
#    pub(topic credentials ) -> can do, queue

class Fwss(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.state = 'CONNECTING'

    def data_received(self, data):

        message = data.decode()
        print('Data received: {!r}'.format(message))
        print('State: {}'.format(self.state))

        if (self.state == 'CONNECTING'):
           if ('GET /wss/ HTTP/1.1\r\n' == message[0:20]):
              # send the websocket upgrade successful response.
              print('foobar')
              response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
              print('response: {!r}'.format(response))
              self.transport.write(response)
              print('Close the client socket')
              self.transport.close()
           else:
              response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
              print('response: {!r}'.format(response))
              self.transport.write(response)
              print('Close the client socket')
              self.transport.close()
        else:
           # it's a datagram or a bogus message
           #Send a failure response
           response = b'HTTP/1.1 501 Not Implemented\r\n\r\n'
           print('response: {!r}'.format(response))
           self.transport.write(response)
           print('Close the client socket')
           self.transport.close()

loop = asyncio.get_event_loop()

# Each client connection will create a new protocol instance
coro = loop.create_server(Fwss, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
