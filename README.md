# Wifi6_confirmation_server

## Requirements
For this repository you need a device that runs on linux. It can be a server but also a laptop, desktop, Raspberry Pi running on linux.

## Setups

### Setup Server
The Setup described below is for when this program is not being setup on the CFNS-server. If you are setting it up on that server start at step 6.
1. Open [server.py](server.py).
2. Scroll to the bottom of the file.
3. Make sure the ip_address is either public and the port is forwarded or the socket with the public ip_address and the specified port is translated to the private ip_adress.
4. Make sure nothing else runs on the specified port.
5. Save [server.py](server.py).
6. Run the following command:
````text
python3 server.py
````
7. You have succesfully setup the server.
