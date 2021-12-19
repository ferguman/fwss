from config import get_config
import asyncio
import logging

from fwss.connection import App

logging.basicConfig(level=logging.DEBUG)

async def main():

   # One and only one application instance exists for the lifetime of the application
   app = App()

   """ One can configure the system to call a custom function after the reception of each byte
       using hte echo function dectorator.
   """
   # Remote line readers.
   # TODO - make is so that line_reader signature is line_reader(reader, writer)
   #        reader wil have method: reader.readline().  Writer will have method
   #        writer.writeline().  Abstract so that it is a general reader. readchar or readline
   #        etc.
   @app.line_reader
   def line_reader(line):
      logging.info(f'######### received: {line}')

   """ One can configure the system to call a custom function after the reception of each byte
       useing the echo function dectorator.
   # Setup web socket connections to echo their incoming bytes in the application log.
   @app.echo
   def echo(byte):
      logging.info(f'########## echo byte: {chr(byte)}')
   """

   # connection is a function that takes two arguments: reader and writer.  
   # server will call connection for each new connection supplying the reader and writer for 
   # that particular connection.
   server = await asyncio.start_server(app.connection, get_config().IP_NUMBER, get_config().IP_PORT_NUMBER)

   # addr is a tuple containing the IP number and port number
   addr = server.sockets[0].getsockname()
   logging.info(f'serving on {addr}')

   async with server:
      await server.serve_forever()

asyncio.run(main())
