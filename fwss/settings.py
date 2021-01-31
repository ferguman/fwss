# There is a test websockt client at https://www.websocket.org/echo.html

ALLOW_NULL_SUB_PROTOCOLS = True   

READ_LIMIT_PER_CONNECTION = 1000  #The maximum number of bytes to read per connection per loop -> This is intended to 
                                  # protect from having one connection stuck reading an infinite input stream and thus
                                  # not allowing other Tasks to run on the same thread. This protection should not be 
                                  # needed in pratice because the state machine that processes the input whould error out
                                  # after some reasonable and finite number of input bytes have been read thus terminating
                                  # the current loop iteration of the impacted connection.

