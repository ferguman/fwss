# Setup

1. Get a web server 

   It is assumed that the fwss websocket server will be proxied by a publicly exposed web server such as nginx.  Here is a snippet from an nginx coniguration file that demonstrates how to setup nginx to proxy web traffic to the fwss websocket server.  Note that we configure nginx to pass the upgrade Http header to fwss so that it can properly negotiate upgrading to the WebSocket protocol from a normal HTTP connection.
```
     location /wss/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
     }
```


2. Clone fwss

   The following commands are illustrative of downloading the fwss from github and create a distribution package.  The distribution package will create a file archive that can be loaded to your server environment.
   ```
   cd ~
   github clone fwss  
   python3.9 setup.py sdist
   ```
   
   The above commands are explained one by one below:
   
   ```cd ~``` -> Connect to the home directory on the machine that you will be downloading the fwss source code to.
   
   ```github clone fwss``` -> This command will create a directory named fwss and download the code from github to this directory.

   ```python3 setup.py sdist``` -> This command will run setup.py which will create a distribution package which is an archive file containing the source code for fwss along with all the necessary libraries. Note that any python version later than 3.6 should work.  Type ```python3 --version``` on your system to see what version of Python 3 is installed. 
   
3. Install on your web server
   - Create a directory on the webserver (e.g. mkdir ~/fwss_instance_1) - this is where your fwss powered  web socket server code will reside.
   - Create a virtual environment - Python3.9 
   - pip install ../fwss/dist/fwss-0.1.tar.gz

4. Configure fwss

   Edit config.py and setup your local environment by specifying such things as the IP address of your server.
