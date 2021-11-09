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
from dataclasses import dataclass, field

# general information for the server and messages with the client
max_msg_length = 10
port = 9000
ip_address = "192.168.3.2"
address = (ip_address, port)
close_message = "DISCONNECT"

# DAB_confirmations is a List that holds all the DAB_confirmations that have been received by the server using this program
DAB_confirmations = []

# This creates the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

@dataclass(order=True,)
class DAB_confirmation:
    sort_index: int
    dab_id: int 
    message_type: int
    dab_msg_arrived_at: float
    technology: str
    sender: int
    valid: bool = True

    def __post_init__(self):
        self.sort_index = self.dab_id

    def __str__(self) -> str:
        return f"DAB_ID: {self.dab_id}, Message_type: {self.message_type}, Time_DAB_message_arrived: {self.dab_msg_arrived_at}, Valid: {self.valid}"

    def reply_info_as_set():
        return (self.dab_id, self.valid)

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
        DAB_confirmations.sort()
        show_confirmations()

        # find dab_confirmation by dab_id
        dab_confirmation = find_dab_confirmation_by_sender(confirmation.get("dab_id"))

        # Send the confirmation for receiving the DAB confirmation 
        reply = json.dumps(build_reply_dict(confirmation.get("dab_id"), dab_confirmation.sender)).encode()
        reply_length = pad_msg_length(max_msg_length, len(reply))
        conn.send(reply_length)
        conn.send(reply)

    # Close the connection
    conn.close()

"""
    Stores the ack and mstype value in DAB_confirmations when ack is not already in the DAB_confirmations
"""
def store_confirmation(confirmation):
    dab_confirmation = DAB_confirmation(confirmation.get("dab_id"), confirmation.get("message_type"), confirmation.get("dab_message_arrived_at"))

    DAB_confirmations.append(dab_confirmation) if dab_confirmation.dab_id in [confirmation.dab_id for confirmation in DAB_confirmation] else return

"""
    This function shows all the DAB confirmations after it sorted the list on dab_id
"""
def show_confirmations():
   for DAB_confirmation in DAB_confirmations:
       print(DAB_confirmations)

"""
    This function returns a dict containing the information necessary and useful for the raspberry pi
    For example the DAB_ID of the message the system tries acknowledge, the messages this server received via AIS that have been send by the rpi that tries to acknowledge a DAB message
    and the messages that have become invalid.
"""
def build_reply_dict(dab_id_to_confirm, sender):
    reply = dict()
    
    # Add DAB_confirmation to this list if the dab_id is the same as dab_id_to_confirm
    dab_confirmation = find_dab_confirmation_by_sender(dab_id_to_confirm)
    reply["ack_information"] = [dab_confirmation.dab_id, dab_confirmation.valid]

    # Add DAB_confirmation to this list if the confirmation is received from sender using AIS
    reply["AIS_ack_information"] = [entry.reply_info_as_set() for entry in DAB_confirmations if entry.sender == sender and entry.technology == "AIS"]

    # Add DAB_confirmation to this list if the confirmation received from sender not using AIS is invalid
    reply["invalid_dab_confirmations"] = [entry.reply_info_as_set() for entry in DAB_confirmations if entry.sender == sender and not entry.technology == "AIS" and entry.valid == False]

    return reply

"""
    This function finds all the dab_confirmations with the dab_id dab_id.
"""
def find_dab_confirmation_by_sender(dab_id):
    results = [dab_confirmation for dab_confirmation in DAB_confirmations if dab_confirmation.dab_id = dab_id]
    return results[0]

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
