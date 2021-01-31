A websocket server based upon the Python asyncio library

# Setup

- Get a webserver

- Clone fwss - github clone fwss - This will create a directory named fwss containing the source code for fwss 
   
   - python3.9 setup.py sdist - this will create distribution package

- Create a directory on the webserver (e.g. mkdir ~/fwss_instance_1) - this is where your fwss powered 
  web socket server code will reside.

   - Create a virtual environment - Python3.9 
   - pip install ../fwss/dist/fwss-0.1.tar.gz

- Edit main.py and setup your local environment by speciging such things as the IP address of your server.



