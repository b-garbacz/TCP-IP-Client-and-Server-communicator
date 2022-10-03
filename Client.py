import socket
import json
import threading as t
import re

############################Socket-Object###########################################
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
############################Socket-Parameters#######################################
port = 5050
host = socket.gethostname()
############################Variables and Containers################################
encoding_format = "utf-8"
buffer = 4096


def send_username(username):
    """
    This funcion sends the username provided by the client to the server
    """
    client_socket.send(username.encode(encoding_format))


def packet_json(json_username, json_message):
    """
    This function prepares the username and message to the dictionaty for JSON format
    """
    packet = {"username": json_username,
              "message": json_message, }
    return packet


def send_message():
    """
    This  function works on a thread and it used to send messages to server.
    Message before sending the message is encoded and formatted to JSON
    """
    while True:
        message = input()
        message = json.dumps(packet_json(username, message))
        client_socket.send(message.encode(encoding_format))


def recv_message():
    """
    This function is to receive messages from the server. Before displaying, the message
    is decoded and loaded from JSON
    """
    message = client_socket.recv(buffer)
    message = json.loads(message.decode(encoding_format))

    username_recv = message.get("username")
    msg_recv = message.get("message")

    print(f"\n{username_recv}->{msg_recv} ")


def listen():
    """
    This function lisntes while client is waiting for messages from the server
    """
    while True:
        try:
            recv_message()
        except ConnectionResetError:
            print("\nServer connection interrupted...")
            client_socket.close()
            break


def username_validation():
    """
    Simple username validation
    """
    print("\nUsername might contain the following:",
          "\n*lowercase letters",
          "\n*capital letters",
          "\n*numbers",
          "\n*special signs(only _ and -) "
          "\n*username must consist letters!(one letter is required)"
          "\n*minimim 3 to 16 characters"

          )

    while True:
        x = input("\nEnter your username: ")
        if re.match(r"^[A-Za-z][A-Za-z0-9_-]{2,16}$", x):
            return x
        else:
            continue



##############################Main########################################
##########################################################################

username = username_validation()
client_socket.connect((host, port))

listening_process = t.Thread(target=listen)
listening_process.start()

senging_process = t.Thread(target=send_message)
senging_process.start()

send_username(username)

# python client.py
