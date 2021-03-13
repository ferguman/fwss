import asyncio
from asyncio import Queue
from enum import Enum
import logging

#- from fwss.settings import READ_LIMIT_PER_CONNECTION
from config import get_config
from fwss.wsc import WebSocketConnectionStates, Wsc

class App():

   #TODO Rename the containing file as app.py

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
      self.call_backs['line_reader'] = f
      return f

   # Decorator that supplies a json reader that scans incomming text for Json
   # defined by json_definition and returns compeled json instances as they arrive.
   def json_reader(self, json_definition):
      pass

   async def ws_reader(self, reader, connection_state, writer, wsc, writer_queue):

      logging.debug('ws_reader started')

      read_stream_open = True

      while not wsc.close and connection_state['read_stream_open']:

          # wait for a connection upgrade request.
          logging.info(f'state: {wsc.state}')

          if wsc.state is WebSocketConnectionStates.WAITING_FOR_UPGRADE_REQUEST:
              # wait for a completed connection upgrade
              request = (await reader.readuntil(b'\r\n\r\n')).decode()
              wsc.process_upgrade_request(request)
              # Put an upgrade request reply into the writer queue
              # print(f'response: {wsc.response}')
              await writer_queue.put(wsc.response)
              # At this point if the upgrade request fails then close your loop because
              # the connection must be closed.
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

                # The Python streamreader returned None when - Assume that the underlying connection is closed.
                if not next_byte:
                    logging.info(f'Reader returned nothing - assume the connection closed')
                    connection_state['read_stream_open'] = False 

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
                if guard_counter >= get_config().READ_LIMIT_PER_CONNECTION:
                   break

          # We are still in the while looping waiting on a wsc.close state of true.
          if not wsc.close:
             await asyncio.sleep(1)

      logging.debug('ws_reader ended')


   async def ws_writer(self, writer, connection_state, wsc, writer_queue):

      logging.info('ws_writer started')

      # The writer has access to transport information.
      logging.info(f'transport info {writer.get_extra_info("socket")}')

      while not wsc.close and connection_state['read_stream_open']:

         if (not writer_queue.empty()):
            writer.write(await writer_queue.get())
            await writer.drain()
         
         if not wsc.close:
            await asyncio.sleep(1)

      logging.info('ws_writer ended')


   # Each new TCP connection will call connection and supply the reader and writer for that
   # connection.
   async def connection(self, reader, writer):

      # The per connection state goes here. Each connection gets its own Wsc instance.
      wsc = Wsc(self.call_backs)
      writer_queue = Queue()

      connection_state = {}
      connection_state['read_stream_open'] = True

      # Create and start the reader and writer tasks
      task1 = asyncio.create_task(self.ws_reader(reader, connection_state, writer, wsc, writer_queue))
      task2 = asyncio.create_task(self.ws_writer(writer, connection_state, wsc, writer_queue))

      # Block until both the reader and writer return.
      await task1 
      await task2 

      # close the TCP connection.
      #- writer.write_eof()
      #? writer.close()
      #? await writer.wait_closed()
