import asyncio
from enum import Enum

class WebSocketConnectionStates(Enum):
   WAITING_FOR_UPGRADE_REQUEST = 1
   UPGRADED = 2
   OPEN = 3



async def ws_reader(reader, writer, state):
   #TODO - implement reading of the upgrade request. leverage code in wsc.py
   print('ws_reader started')
   data = ''

   # wait for a connection upgrade request.
   if state['conn_state'] == WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST:
      #TODO - will need to put a timeout in here. No connection should be started without
      #       an immediate upgrade request
      while True:
          cl = (await reader.readline()).decode()
          data = data + cl
          if cl == '\r\n': 
             break 
      #TODO - At this point the connection upgrade has been received so integrate wsc.py to verify the connection
      #       upgrade data
      print(data)

   # Close the connection.
   writer.close()
   print('ws_reader ended')

async def ws_writer(writer, state):
   print('ws_writer started')
   # The writer has access to transport information.
   print(f'transport info {writer.get_extra_info("socket")}')
   print('ws_writer ended')

async def connection(reader, writer):

   state = {}
   state['conn_state'] = WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST 

   task1 = asyncio.create_task(ws_reader(reader, writer, state))
   task2 = asyncio.create_task(ws_writer(writer, state))

   # Both task1 and task are run conncurrently.
   # TODO - each task is envisioned to have it's own sleepy loop in order to 
   #        to allow bi-direction ws traffic.
   await task1 
   await task2 


async def main():
   server = await asyncio.start_server(connection, '127.0.0.1', 8888)

   # addr is a tuple containing the IP number and port number
   addr = server.sockets[0].getsockname()
   print(f'serving on {addr}')

   async with server:
      await server.serve_forever()

asyncio.run(main())
