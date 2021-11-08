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
max_msg_length = 10
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
        # Receive the length of the confirmation message
        confirmation_length = conn.recv(max_msg_length).decode()
        
        # If the client closes the connection stop the thread
        if len(confirmation_length) == 0:
            break

        # Receive the confirmation itself
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
        reply = json.dumps({"received": get_confirmed_acks()}).encode()
        reply_length = pad_msg_length(max_msg_length, len(reply))
        conn.send(reply_length)
        conn.send(reply)

    # Close the connection
    conn.close()

"""
    Stores the ack and mstype value in DAB_confirmations when ack is not already in the DAB_confirmations
"""
def store_confirmation(confirmation):
    dab_id = confirmation.get("dab_id")
    message_type = confirmation.get("message_type")
    dab_msg_arrived_at = confirmation.get("dab_msg_arrived_at")

    if not dab_id in DAB_confirmations:
        DAB_confirmations[dab_id] = [message_type, dab_msg_arrived_at]

"""
    This function shows all the DAB confirmations
"""
def show_confirmations():
    dab_id_str = "|DAB_ID"
    message_type_str = "|Message type"
    dab_msg_arrived_at = "|Time DAB message arrived|"
    print(dab_id_str, message_type_str, dab_msg_arrived_at)

    for dab_id, message_type, dab_msg_arrived_at in DAB_confirmations.items():
        print(str(dab_id).ljust(len(dab_id_str)) , message_type.ljust(len(message_type_str)), dab_msg_arrived_at)

"""
    This function returns a list of acknowledgement numbers of confirmed dab messages that are received by the server.
"""
def get_confirmed_acks():
    return list(DAB_confirmations.keys())

"""
    pad the var msg_length to the padding size. 
    So that the message containing the msg_length has a fixed size of padding size.
"""
def pad_msg_length(padding_size, msg_length):
    msg_length = str(msg_length).encode()
    msg_length += b' ' * (padding_size - len(msg_length))
    return msg_length

# Start the server
print("[STARTING] server is starting...")
run()
