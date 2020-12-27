import asyncio
#- from asyncio import Queue
#- from enum import Enum
import logging
from python.connection import connection

logging.basicConfig(level=logging.DEBUG)

async def main():
   server = await asyncio.start_server(connection, '127.0.0.1', 8888)

   # addr is a tuple containing the IP number and port number
   addr = server.sockets[0].getsockname()
   logging.info(f'serving on {addr}')

   async with server:
      await server.serve_forever()

asyncio.run(main())
