import socket
import select

HEADER = 10
IP = socket.gethostbyname(socket.gethostname())
PORT = 10101
ADDRESS = (IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)

sockets_list = [server_socket]
clients = {}


def encode_message(msg):
    message = msg.encode(FORMAT)
    header_msg = f"{len(message):<{HEADER}}".encode(FORMAT)

    return {'header':header_msg, 'data':message, 'message':msg}


def receive_message(client_socket):
    try:
        mes_header = client_socket.recv(HEADER)
        if not len(mes_header):
            return False
        mes_len = int(mes_header.decode(FORMAT).strip())
        mes_data = client_socket.recv(mes_len)
        mes = mes_data.decode(FORMAT)

        return {"header":mes_header, "data":mes_data, "message":mes}
    except:
        return False


def broadcast_message(sender_socket, message):
    sender = clients[sender_socket]
    print(f"{sender['message']} > everyone : {message['message']}")

    for client_socket in clients:
        if client_socket != sender_socket:
            client_socket.send(sender['header'] + sender['data'] + message['header'] + message['data'])


def send_message(sender_socket, receiver, message):
    sender = clients[sender_socket]
    mess = message['message'].split(' ', 1)[1]
    mess = encode_message(mess)

    for client_socket in clients:
        if client_socket != sender_socket:
            if clients[client_socket]['message'] == receiver:
                client_socket.send(sender['header'] + sender['data'] + mess['header'] + mess['data'])
                print(f"{sender['message']} > {receiver} : {mess['message']}")
                return
    
    broadcast_message(sender_socket, message)


def process_message(sender_socket, message):
    username = message['message'].split(' ', 1)[0]
    if username[0] == '@':
        send_message(sender_socket, username[1:], message)
    else:
        broadcast_message(sender_socket, message)


def start():
    server_socket.listen()

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()

                user = receive_message(client_socket)
                if user is False:
                    continue

                sockets_list.append(client_socket)

                clients[client_socket] = user

                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['message']}")
            
            else:
                message = receive_message(notified_socket)

                if message is False or message['message'] == DISCONNECT_MESSAGE:
                    print(f"Closed connection from {clients[notified_socket]['message']}")
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue

                process_message(notified_socket, message)
        
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


print("[STARTING SERVER] server is starting.....")
print(f"[SERVER STARTED] server started at {server_socket.getsockname()}")

start()
