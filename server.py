'''
project: slimmer maken multiconnectivity modem
author: Frank Montenij
date: 29-10-2021
description: This code accept connections after which it receives confirmations of DAB message. 
             The code will store these messages and send back an acknowledgment to the client to inform the client that the confirmation has been received.
'''

import socket 
import threading
import json

# general information for the server and messages with the client
msg_length = 20
port = 9000
ip_address = "192.168.3.2"
address = (ip_address, port)
close_message = "DISCONNECT"

# Dictionary to store the confirmations of DAB messages received by the multiconnectivity modem
DAB_confirmations = {}

# This creates the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

"""
    This function is responsible for accepting connections from clients.
    It also starts a thread to handle the connection.
"""
def run():
    server.listen()
    print(f"Server is listening on {ip_address}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_thread, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

"""
    Here the connection with the client will be handled.
    This function handles receiving messages from the client.
"""
def client_thread(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    # Receive the confirmation message
    while True:
        confirmation_length = conn.recv(msg_length).decode()
        if confirmation_length:
            confirmation_length = int(confirmation_length)
            confirmation = conn.recv(confirmation_length).decode()

            # Extract the data from the message
            confirmation = json.loads(confirmation)

            # If the data contains the disconnect message close the connection
            if close_message in confirmation:
                print(f"[CLIENT] {close_message}!")
                break
            else: # Otherwise store the confirmation
                store_confirmation(confirmation)

            # Show the DAB messages that are confirmed
            show_confirmations()

            # Send the confirmation for receiving the DAB confirmation 
            reply = json.dumps({"received": True}).encode()
            reply_length = str(len(reply)).encode() + (b' ' * (msg_length - len(reply)))
            conn.send(reply_length)
            conn.send(reply)

    # Close the connection
    conn.close()

"""
    Stores the ack and mstype value in DAB_confirmations when ack is not already in the DAB_confirmations
"""
def store_confirmation(confirmation):
    ack = confirmation.get("ACK")
    mstype = confirmation.get("MSTYPE")

    if not ack in DAB_confirmations:
        DAB_confirmations[ack] = mstype

"""
    This function shows all the DAB confirmations
"""
def show_confirmations():
    ack_string = "Acknowledgment number "
    mstype_string = "Message type"
    print(ack_string, mstype_string)

    for ack, mstype in DAB_confirmations.items():
        print(str(ack).ljust(len(ack_string)) , mstype)

# Start the server
print("[STARTING] server is starting...")
run()
