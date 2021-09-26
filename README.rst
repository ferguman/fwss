A websocket server based upon the Python asyncio library

# Setup

- Get a webserver 
It is assumed that the websocket server will be a proxy client to publicly exposed web server such as nginx.  Here is a snippet from an nginx coniguration file that demonstrates how to setup nginx to proxy web traffic to the fwss websocket server.  Note that we configure nginx to pass the upgrade Http header to fwss so that it can properly negotiate upgrading to the WebSocket protocol from a normal HTTP connection.
::

   location /wss/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    

- Clone fwss - github clone fwss - This will create a directory named fwss containing the source code for fwss 
   
   - python3.9 setup.py sdist - this will create distribution package

- Create a directory on the webserver (e.g. mkdir ~/fwss_instance_1) - this is where your fwss powered 
  web socket server code will reside.

   - Create a virtual environment - Python3.9 
   - pip install ../fwss/dist/fwss-0.1.tar.gz

- Edit config.py and setup your local environment by specifying such things as the IP address of your server.



