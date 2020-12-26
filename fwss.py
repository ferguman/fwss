import asyncio
from asyncio import Queue
from enum import Enum
from python.wsc import Wsc

class WebSocketConnectionStates(Enum):
   WAITING_FOR_UPGRADE_REQUEST = 1
   UPGRADED = 2
   OPEN = 3


async def ws_reader(reader, writer, wsc, writer_queue, state):

   #TODO - implement reading of the upgrade request. leverage code in wsc.py
   print('ws_reader started')
   data = ''

   while True:

       # wait for a connection upgrade request.
       if state['conn_state'] == WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST:
           # wait for a completed connection upgrade
           request = (await reader.readuntil(b'\r\n\r\n')).decode()
           #TODO - remove this print
           print(f'request: {request}')
           wsc.process_upgrade_request(request)
           # Put an upgrade request reply into the writer queue
           # print(f'response: {wsc.response}')
           await writer_queue.put(wsc.response)
           # At this point if the upgrade request fails then close your loop becuase
           # because the connection must be closed.
           if wsc.close:
              break

       await asyncio.sleep(1)


   print('ws_reader ended')

async def ws_writer(writer, wsc, writer_queue, state):
   print('ws_writer started')
   # The writer has access to transport information.
   print(f'transport info {writer.get_extra_info("socket")}')

   # TODO - Implement this loop
   while True:

      if (not writer_queue.empty()):
         writer.write(await writer_queue.get())
         await writer.drain()
      
         if wsc.close:
             writer.close()
             break

      await asyncio.sleep(1)

   print('ws_writer ended')
      
   #    for each item in the outgoing queue
   #    await write_item
   #    if writer queue has entry
   #       if entry is wsc reponse
   #          send the response
   #          if close is needed then break 
   #

async def connection(reader, writer):

   wsc = Wsc()
   writer_queue = Queue()

   state = {}
   state['conn_state'] = WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST 

   task1 = asyncio.create_task(ws_reader(reader, writer, wsc, writer_queue, state))
   task2 = asyncio.create_task(ws_writer(writer, wsc, writer_queue, state))

   # Both task1 and task are run conncurrently.
   # TODO - The writer (task2) will have a sleepy loop that
   #        that looks for outgoing traffic such as server
   #        responses to data reads and asyncrouns events such 
   #        as incoming MQQT messages.
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
