import asyncio
from asyncio import Queue
from enum import Enum
import logging

from python.settings import READ_LIMIT_PER_CONNECTION
from python.wsc import WebSocketConnectionStates, Wsc

#- class WebSocketConnectionStates(Enum):
#-    WAITING_FOR_UPGRADE_REQUEST = 1
#-    OPEN = 2                           # OPEN -> See page 25 of RFC 6455

async def ws_reader(reader, writer, wsc, writer_queue):

   logging.debug('ws_reader started')

   while not wsc.close:

       # wait for a connection upgrade request.
       logging.info(f'state: {wsc.state}')
       if wsc.state is WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST:
           # wait for a completed connection upgrade
           request = (await reader.readuntil(b'\r\n\r\n')).decode()
           wsc.process_upgrade_request(request)
           # Put an upgrade request reply into the writer queue
           # print(f'response: {wsc.response}')
           await writer_queue.put(wsc.response)
           # At this point if the upgrade request fails then close your loop becuase
           # because the connection must be closed.
           if wsc.close:
              break
           else:
              logging.info('changing state to OPEN')
              #- state['conn_state'] = WebSocketConnectionStates.OPEN
              wsc.state = WebSocketConnectionStates.OPEN

       elif wsc.state is WebSocketConnectionStates.OPEN:
          #TODO will need to read the input one byte at a time (e.g. reader.read(1)) and pass
          #     each byte off to a new function (call it FrameReader) that assembles the incoming
          #     frame.  If the incoming frame is not legal then close the connection elsewise
          #     if the frame is done then pass the frame to a new class called FrameHandler.
          # Read a byte
          guard_counter = 0
          while not reader.at_eof():

             next_byte = await reader.read(1)

             wsc.process_byte(next_byte)
             if wsc.close:
                 break
             # if at_frame_end:
             #    await writer_queue.put(process_frame(wsc.frame)
             #    if close
             #       break

             # Don't deny service to the other tasks. One could be processing a long stream such as a video, in 
             # which case the task needs to break off in order to let the Python async runtime to let other tasks
             # have a chance to run.
             guard_counter += 1
             if guard_counter >= READ_LIMIT_PER_CONNECTION:
                break

       if not wsc.close:
          await asyncio.sleep(1)

   logging.debug('ws_reader ended')

async def ws_writer(writer, wsc, writer_queue):

   print('ws_writer started')
   # The writer has access to transport information.
   print(f'transport info {writer.get_extra_info("socket")}')

   #- while True:
   while not wsc.close:

      if (not writer_queue.empty()):
         writer.write(await writer_queue.get())
         await writer.drain()
      
         """-
         if wsc.close:
             writer.close()
             break
         """

      if not wsc.close:
         await asyncio.sleep(1)

   print('ws_writer ended')
      

# Each new TCP connection will put a new instance of connection on the stack. TODO - Is python stacked base?
async def connection(reader, writer):

   """-
   # Setup call backs
   # TODO - add extension data structions and processing.
   def is_valid_extension(extension_code):
      logging.info('TODO - Implement extension validity checker')
      return True
   # TODO - Instead of having this business of a connection dictionary with call backs
   #        instead create a Message Controller that provides the messaging services
   #        such as is_valid_extension.
   connection = {}
   connection['is_valid_extension'] = is_valid_extension
   """

   wsc = Wsc()
   writer_queue = Queue()

   """-
   state = {}
   state['conn_state'] = WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST 
   """

   task1 = asyncio.create_task(ws_reader(reader, writer, wsc, writer_queue))
   task2 = asyncio.create_task(ws_writer(writer, wsc, writer_queue))

   # Both task1 and task are run conncurrently.
   # TODO - The writer (task2) will have a sleepy loop that
   #        that looks for outgoing traffic such as server
   #        responses to data reads and asyncrouns events such 
   #        as incoming MQQT messages.
   await task1 
   await task2 

   # close the TCP connection.
   writer.close()

