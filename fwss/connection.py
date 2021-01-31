import asyncio
from asyncio import Queue
from enum import Enum
import logging

from fwss.settings import READ_LIMIT_PER_CONNECTION
from fwss.wsc import WebSocketConnectionStates, Wsc

class App():

   #TODO 
   #     Rename the containing file as app.py
   #     Read the async io docks for the server object. See what they say about
   #     supplying a class as the connection attribure to the server instead of a method/function

   def __init__(self):
      self.call_backs = {}


   # supply a app decorator that will supply payload bytes as they arrive
   # one at a time.
   # See https://ains.co/blog/things-which-arent-magic-flask-part-1.html for an explanation of
   # how decorators work in Flask
   def echo(self, f):

      self.call_backs['echo'] = f

      return f

   # Decorator that supplies a line reader that returns text payload lines
   # one at a time as they arrive.
   def line_reader(self, f):
      pass

   # Decorator that supplies a json reader that scans incomming text for Json
   # defined by json_definition and returns compeled json instances as they arrive.
   def json_reader(self, json_definition):
      pass

   # Each new TCP connection will call connection and supply the reader and writer for that
   # connection.
   async def connection(self, reader, writer):

      wsc = Wsc(self.call_backs)
      writer_queue = Queue()

      #- task1 = asyncio.create_task(ws_reader(reader, writer, wsc, writer_queue))
      #- task2 = asyncio.create_task(ws_writer(writer, wsc, writer_queue))
      task1 = asyncio.create_task(self.ws_reader(reader, writer, wsc, writer_queue))
      task2 = asyncio.create_task(self.ws_writer(writer, wsc, writer_queue))

      # Both task1 and task2 are run concurrently. As long as either task has not returned
      # then this connection function invocation will not return.
      await task1 
      await task2 

      # close the TCP connection.
      writer.close()

   async def ws_reader(self, reader, writer, wsc, writer_queue):

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

   async def ws_writer(self, writer, wsc, writer_queue):

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
