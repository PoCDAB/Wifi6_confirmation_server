'''
project: slimmer maken multiconnectivity modem
author: Frank Montenij
date: 29-10-2021
description: This code accept connections after which it receives confirmations of DAB message. 
             The code will store these messages and send back an acknowledgment to the client to inform the client that the confirmation has been received.
             The code will also be used when testing the whole confirmation using wifi.
'''

import socket 
import threading
import json
from dataclasses import dataclass, field

# General informtion also necessary when importing server
max_msg_length = 10
close_message = "DISCONNECT"

class ClientClosedConnectionError(Exception):
    """This error is raised when the client closes the connection without the disconnect message."""

@dataclass(order=True)
class DAB_confirmation:
    """A dataclass to store the information of a DAB_confirmation."""
    sort_index: int = field(init=False, repr=False)
    dab_id: int 
    message_type: int
    dab_msg_arrived_at: float
    technology: str
    sender: int
    valid: bool = True

    # Enables to sort the object on the dab_id
    def __post_init__(self):
        self.sort_index = self.dab_id

    # A method to represent the data in the object in a readable way
    def __str__(self):
        return f"DAB_ID: {self.dab_id}, Message_type: {self.message_type}, Time_DAB_message_arrived: {self.dab_msg_arrived_at}, Sender: {self.sender}, Valid: {self.valid}"

    # Used to retrieve valuable information of this object for the reply process
    def get_reply_info(self):
        return (self.dab_id, self.valid)

"""
    This function is responsible for accepting connections from clients.
    It also starts a thread to handle the accepted connection.
"""
def run():
    server.listen()
    print(f"Server is listening on {ip_address}")
    while True:
        conn, _ = server.accept()
        thread = threading.Thread(target=client_thread, args=[conn])
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

"""
    This function handles receiving messages from the client.
    And sending back a reply message to the sender.
"""
def client_thread(conn):
    while True:
        try:
            confirmation = receive_confirmation(conn)
        except ClientClosedConnectionError:
            break

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

        send_reply(conn, confirmation.get("dab_id"), dab_confirmation.sender)

    # Close the connection
    conn.close()

"""
    Receives the confirmation message. 
"""
def receive_confirmation(conn):
        # Receive the length of the confirmation message
        confirmation_length = conn.recv(max_msg_length).decode()
        
        # If the client closes the connection stop the thread
        if len(confirmation_length) == 0:
            raise(ClientClosedConnectionError)

        # Receive the confirmation itself
        confirmation_length = int(confirmation_length)
        confirmation = conn.recv(confirmation_length).decode()

        # Return the extracted data from the message
        return json.loads(confirmation)

"""
    Send the reply with the reply dict info
"""
def send_reply(conn, dab_id, sender):
    reply = json.dumps(build_reply_dict(dab_id, sender)).encode()
    reply_length = pad_msg_length(max_msg_length, len(reply))
    conn.send(reply_length)
    conn.send(reply)

"""
    Stores the ack and mstype value in DAB_confirmations when ack is not already in the DAB_confirmations
"""
def store_confirmation(confirmation):
    new_dab_confirmation = DAB_confirmation(
        confirmation.get("dab_id"), 
        confirmation.get("message_type"), 
        confirmation.get("dab_msg_arrived_at"), 
        confirmation.get("technology"), 
        confirmation.get("sender")
    )

    if not check_if_in_DAB_confirmations(new_dab_confirmation.dab_id):
       DAB_confirmations.append(new_dab_confirmation)
    else:
        print("[SERVER] DAB_confirmation already in list") 

"""
    Checks if the dab_id is already in the DAB_confirmations
"""
def check_if_in_DAB_confirmations(dab_id):
    dab_ids = [dab_confirmation.dab_id for dab_confirmation in DAB_confirmations]

    if dab_id in dab_ids:
        return True
    else:
        return False

"""
    This function shows all the DAB confirmations after it sorted the list on dab_id
"""
def show_confirmations():
   for DAB_confirmation in DAB_confirmations:
       print(DAB_confirmation)

"""
    This function returns a dict containing the information necessary and useful for the raspberry pi
    For example the DAB_ID of the message the system tries acknowledge, the messages this server received via AIS that have been send by the rpi that tries to acknowledge a DAB message
    and the messages that have become invalid.
"""
def build_reply_dict(dab_id_to_confirm, sender):
    reply = dict()
    
    # Add DAB_confirmation to this list if the dab_id is the same as dab_id_to_confirm
    dab_confirmation = find_dab_confirmation_by_sender(dab_id_to_confirm)
    reply['ack_information'] = [dab_confirmation.dab_id, dab_confirmation.valid]

    """
    Add DAB_confirmation to this list if the confirmation is received from sender and not the same as ack_information. 
    To update the folder which files have been received. Not just the Wifi messages but all the messages. This way the AIS, LoRaWAN and LTE messages can be confirmed. 
    """
    reply['different_ack_information'] = [entry.get_reply_info() for entry in DAB_confirmations if entry.sender == sender and not dab_confirmation.dab_id == entry.dab_id]

    return reply

"""
    This function finds all the dab_confirmations with the dab_id dab_id.
"""
def find_dab_confirmation_by_sender(dab_id):
    results = [dab_confirmation for dab_confirmation in DAB_confirmations if dab_confirmation.dab_id == dab_id]
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
if __name__ == "__main__":  
    # general information for the server and messages with the client
    port = 9000
    ip_address = "192.168.3.2"
    address = (ip_address, port)

    # DAB_confirmations is a List that holds all the DAB_confirmations that have been received by the server using this program
    DAB_confirmations = []

    # This creates the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)   
    
    print("[STARTING] server is starting...")
    run()
