import socket
import threading
import sys
import errno

HEADER = 10
IP = input("Enter IP : ")
PORT = 10101
ADDRESS = (IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
is_connected = False


def encode_message(msg):
    message = msg.encode(FORMAT)
    header_msg = f"{len(message):<{HEADER}}".encode(FORMAT)
    return {'header':header_msg, 'data':message, 'message':msg}


def send_message(msg):
    msg = encode_message(msg)
    client_socket.send(msg['header'] + msg['data'])


def receive_messages():
    global is_connected
    try:
        while is_connected:
            user_head = client_socket.recv(HEADER)
            user_len = int(user_head.decode(FORMAT).strip())
            username = client_socket.recv(user_len).decode(FORMAT)

            mess_head = client_socket.recv(HEADER)
            mess_len = int(mess_head.decode(FORMAT).strip())
            message = client_socket.recv(mess_len).decode(FORMAT)

            print(f"{username} > {message}")
    
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("Reading Error", str(e))
            sys.exit()

    except Exception as e:
        print("General Error", str(e))
        sys.exit()


def write():
    global is_connected
    while is_connected:
        message = input()

        if message == DISCONNECT_MESSAGE:
            is_connected = False
        send_message(message)
    
    print('u r discconnected now')


def start():
    my_username = input("Enter username : ")

    client_socket.connect(ADDRESS)
    client_socket.setblocking(True)

    global is_connected
    is_connected = True

    send_message(my_username)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()


start()
