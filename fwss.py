import asyncio
import logging

from fwss.connection import App 

logging.basicConfig(level=logging.DEBUG)

async def main():

   # One and only one application instance exists for the lifetime of the application
   app = App()

   # Setup all web socket connections to echo their incoming bytes in the application log.
   # Rename echo to something like app.on_byte()
   @app.echo
   def echo(byte):
      logging.info(f'echo byte: {chr(byte)}')

   # connection is a function that takes two arguments: reader and writer.  
   # server will call connection for each new connection supplying the reader and writer for 
   # that particular connection.
   server = await asyncio.start_server(app.connection, '127.0.0.1', 8888)

   # addr is a tuple containing the IP number and port number
   addr = server.sockets[0].getsockname()
   logging.info(f'serving on {addr}')

   async with server:
      await server.serve_forever()

asyncio.run(main())
