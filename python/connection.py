import asyncio
from asyncio import Queue
from enum import Enum
import logging

from python.wsc import Wsc

class WebSocketConnectionStates(Enum):
   WAITING_FOR_UPGRADE_REQUEST = 1
   #- UPGRADED = 2
   OPEN = 3                           # OPEN -> See page 25 of RFC 6455

async def ws_reader(reader, writer, wsc, writer_queue, state):

   logging.debug('ws_reader started')

   while True:

       # wait for a connection upgrade request.
       if state['conn_state'] == WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST:
           # wait for a completed connection upgrade
           request = (await reader.readuntil(b'\r\n\r\n')).decode()
           logging.debug(f'request: {request}')
           wsc.process_upgrade_request(request)
           # Put an upgrade request reply into the writer queue
           # print(f'response: {wsc.response}')
           await writer_queue.put(wsc.response)
           # At this point if the upgrade request fails then close your loop becuase
           # because the connection must be closed.
           if wsc.close:
              break
           else:
              state['conn_state'] = WebSocketConnectionStates.OPEN
       elif state['conn_state'] == WebSocketConnectionStates.OPEN:
          #TODO will need to read the input one byte at a time (e.g. reader.read(1)) and pass
          #     each byte off to a new function (call it FrameReader) that assembles the incoming
          #     frame.  If the incoming frame is not legal then close the connection elsewise
          #     if the frame is done then pass the frame to a new class called FrameHandler.
          pass

       await asyncio.sleep(1)

   logging.debug('ws_reader ended')

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

