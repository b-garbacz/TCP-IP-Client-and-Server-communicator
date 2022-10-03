import socket
import json
import threading as t
############################Socket-Object###########################################
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

############################Socket-Parameters#######################################
host = socket.gethostname()
port = 5050
server_socket.bind((host, port))
server_socket.listen(10)

############################Variables and Containers################################
format = "utf-8"
buffer = 4096
username = "Server"
clients_db = []
Empty_message = {"username": "Server", "message": "The Server has been turned on"}
saved_messages = [Empty_message]
####################################################################################

def add_client(client_socket, address, username):
    """
    This function adds a user to the database that has connected to the server
    """
    new_client = {"client_socket": client_socket,
                  "address": address,
                  "username": username
                  }
    clients_db.append(new_client)


def recv_message(client_socket):
    """
    This function is to receive messages from the client. The message
    is decoded loaded from JSON, and returned
    """
    message = client_socket.recv(buffer)
    saved_messages.append(json.loads(message.decode(format)))

    return message


def packet_json(json_username, json_message):
    """
    This function prepares the username and message to the dictionaty for JSON format
    """
    packet = {"username": json_username,
              "message": json_message}
    return packet


def send_to_all_users(message):  # jeden do wszystkich
    """
    This function transfers a message to all recipients simultaneously
    """
    for client_socket in clients_db:
        cs = client_socket.get("client_socket")
        cs.send(message)


def send_static_broadcast_message(message):
    """
    This function transfers a message to all recipients simultaneously, but only static message given by parameter
    """
    message = json.dumps(packet_json(username, message))
    send_to_all_users(message.encode())


def handle_message(client_socket):
    """
    This function handle handle messaging from one user to all by the server(broadcast)
    """
    while True:
        try:
            message = recv_message(client_socket)
            send_to_all_users(message)
        except ConnectionResetError:
            for user_info in clients_db:
                if user_info.get("client_socket") == client_socket:
                    client_address = user_info.get("address")
                    client_username = user_info.get("username")
                    clients_db.remove(user_info)
                    client_socket.close()
                    send_static_broadcast_message(f"User {client_username}@{client_address[0]} has left the chat")

            break


def list_of_server_users():
    "This function generates actial list of connected users "
    buffor_usernames = ""
    for user_info in clients_db:
        usrname = user_info.get("username")
        address = user_info.get("address")
        buffor_usernames += str(usrname) + "@" + str(address[0])+ ", "
    buffor_usernames = " List of users: " + buffor_usernames[:-1]
    return buffor_usernames


def send_usernames(client_socket):
    """
    this function sends actual list of connected users to new connected user
    """
    message_usr_list = list_of_server_users()
    message_usr_list = json.dumps(packet_json(username, message_usr_list))
    client_socket.send(message_usr_list.encode(format))


def send_history_of_chat(client_socket):
    """
    :param client_socket:
    :return:
    """
    for index in range(len(saved_messages)):
        x1 = saved_messages[index].get("username")
        x2 = saved_messages[index].get("message")
        print(x1,x2)
        message = json.dumps(packet_json(x1, x2))
        client_socket.send(message.encode(format))



def main_loop():
    while True:
        client_socket, address = server_socket.accept()
        name = client_socket.recv(buffer).decode(format)
        add_client(client_socket, address, name)

        send_history_of_chat(client_socket)

        handle_process = t.Thread(target=handle_message, args=(client_socket,))
        handle_process.start()

        send_static_broadcast_message(f"User {name}@{address[0]} has joined the chat")
        send_usernames(client_socket)




main_loop()
# python server.py
# python client.py
