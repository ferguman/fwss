from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

# This configuration code is adapted from: https://leontrolski.github.io/sane-config.html

class SecurityImplementations(Enum):
   PLAIN_TEXT_PASSCODE = 1

@dataclass
class Config:
   ALLOW_NULL_SUB_PROTOCOLS: bool
   # As an option one can implement client authentication via JWT by setting this
   # parameter to true.  The server must reply with a sub-protocol value in order to 
   # remain compliant. Use the SERVER_SUB_PROTOCOL_VALUE settings for this.
   LOOK_FOR_JWT_IN_SUBPROTOCOL: bool 
   IP_NUMBER: str 
   IP_PORT_NUMBER: int
   JWT_SECRET: str
   #TODO - implmenet the maximum payload length 
   MAXIMUM_PAYLOAD_LENGTH: int 
   #The maximum number of bytes to read per connection per loop -> This is intended to
   # protect from having one connection stuck reading an infinite input stream and thus
   # not allowing other Tasks to run on the same thread. This protection should not be 
   # needed in pratice because the state machine that processes the input whould error out
   # after some reasonable and finite number of input bytes have been read thus terminating
   # the current loop iteration of the impacted connection.
   READ_LIMIT_PER_CONNECTION: int  
   # Used for PLAIN_TEXT_PASSCODE security implementations.
   PLAIN_TEXT_PASSCODE: str
   # Choose a security implementation for your websocket server 
   # For PLAIN_TEXT_PASSCODE pass the info on the subprocotol header as:
   #    PASSPHRASEpass code, [this server's SERVER_SUB_PROTOCOL_VALUE] -> PASSPHRASEfoobar,LINE_READER
   #
   # Note that putting the passphrase in the sub protocol field list is a hack and there are constraints
   # imposed by the web socket spec. For example sub protocal fields cannot contain seperator characters such
   # as : or @
   SECURITY_IMPLEMENTATION: int
   # The value to return to clients as a sub protocol. As per the specification, if a client sends
   # a subprotocol list then one of the values must be returned. That one value goes here.  
   SERVER_SUB_PROTOCOL_VALUE: str 
   

   #TODO - Implement CORS based security. I think uyou will put a list of acceptibel orign values here, 
   # or maybe a regular expression or mabye a cors lambda.

# TODO add the config creation to main.py. In other words the user of the library should crate the config
#      values for their intended use. Alos move this config.py to the fwss folder. In other words put the 
#      definition of hte configuration paramters into the module code.
# add a cache in case configuration is changed to pull from a file or some other out of process
# store.
@lru_cache(None)
def get_config() -> Config:
   return Config(
         ALLOW_NULL_SUB_PROTOCOLS = False,
         IP_NUMBER = '127.0.0.1',
         IP_PORT_NUMBER = 8888,
         JWT_SECRET = 'TODO - implment JWT',
         LOOK_FOR_JWT_IN_SUBPROTOCOL = True, 
         MAXIMUM_PAYLOAD_LENGTH = 1000,
         PLAIN_TEXT_PASSCODE = 'foo',
         READ_LIMIT_PER_CONNECTION = 1000, 
         SECURITY_IMPLEMENTATION = SecurityImplementations.PLAIN_TEXT_PASSCODE, 
         SERVER_SUB_PROTOCOL_VALUE = 'LINE_READER'
   )
