# fwss - Fop Web Socket Server

import asyncio
from python.wsc import Wsc 

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

# This class controls the TCP/IP connection.
# Create a new web socket controller (wsc) for each connection.
# Pass data to the wsc
# Close the connection when the wsc so instructs
#
class Fwss(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.wsc = Wsc()

    def data_received(self, data):

        message = data.decode()
        print('Data received: {!r}'.format(message))
        self.wsc.process_data(message)

        if (self.wsc.response):
           self.transport.write(self.wsc.response)
        
        if (self.wsc.close):
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
