from dataclasses import dataclass
from functools import lru_cache

# This stuff is adapted from: https://leontrolski.github.io/sane-config.html
# There is a test websocket client at https://www.websocket.org/echo.html

@dataclass
class Config:
   ALLOW_NULL_SUB_PROTOCOLS: bool
   IP_NUMBER: str 
   IP_PORT_NUMBER: int
   READ_LIMIT_PER_CONNECTION: int  
   #The maximum number of bytes to read per connection per loop -> This is intended to
   # protect from having one connection stuck reading an infinite input stream and thus
   # not allowing other Tasks to run on the same thread. This protection should not be 
   # needed in pratice because the state machine that processes the input whould error out
   # after some reasonable and finite number of input bytes have been read thus terminating
   # the current loop iteration of the impacted connection.

# add a cache in case configuration is changed to pull from a file or some other out of process
# store.
@lru_cache(None)
def get_config() -> Config:
   return Config(
         ALLOW_NULL_SUB_PROTOCOLS = True,
         IP_NUMBER = '127.0.0.1',
         IP_PORT_NUMBER = 8888,
         READ_LIMIT_PER_CONNECTION = 1000
   )
