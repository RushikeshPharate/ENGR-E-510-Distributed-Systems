# import socket
# import threading
# import os, signal

# class ThreadedServer(object):
#     def __init__(self, host, port):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         host_addr, port_number = socket.getaddrinfo(host, port)[0][4]
#         self.sock.bind((host_addr, port_number))
#         self.connection_count = 0

#     def listen(self):
#         self.sock.listen()
#         print("Hello, I am a server")
#         while True:
#             try:
#                 client, address = self.sock.accept()
#                 print(f"connection {self.connection_count} from {address}")
#                 self.connection_count += 1
#                 th = threading.Thread(target = self.listenToClient,args = (client,address, self.sock))
#                 th.daemon = True
#                 th.start()
#             except Exception as ex:
#                 self.sock.close()
#                 break
    
#     def listenToClient(self, client, address, s):
#         while True:
#             try:
#                 isExitRcvd = False
#                 data = client.recv(256).decode().replace("\n","")
#                 print(f"got message from {address}")
#                 if not data:
#                     break
#                 if data == str("hello"):
#                     client.send("world\n".encode())
#                     continue
#                 if data == str("goodbye"):
#                     client.send("farewell\n".encode()) 
#                     client.close()  
#                     break
#                 if data == str("exit"):
#                     client.send("ok\n".encode())
#                     isExitRcvd = True
#                     break
#                 data = data + "\n"
#                 client.send(data.encode())
#             except:
#                 client.close()
#                 return False
#         if isExitRcvd:
#             client.close()
#             s.shutdown(socket.SHUT_RDWR)
        
#     # def sock_stop(self):
#     #     print("inside sock_stop")
#     #     pid = os.getpid()
#     #     os.kill(pid, signal.SIGTERM)


# def chat_server(iface:str, port:int, use_udp:bool) -> None:
#     if not use_udp:
#         ThreadedServer(iface,port).listen()
#     else:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             host_addr, port_number = socket.getaddrinfo(iface, port)[0][4]
#             s.bind((host_addr, port))
#             print("Hello, I am a server")
#             while True:
#                 message, addr = s.recvfrom(256)
#                 data = message.decode().replace("\n","")
#                 print(f"got message from {addr}")
#                 if data == str("hello"):
#                     s.sendto("world\n".encode(),addr)
#                     continue
#                 if data == str("goodbye"):
#                     s.sendto("farewell\n".encode(),addr)   
#                     continue
#                 if data == str("exit"):
#                     s.sendto("ok\n".encode(),addr)
#                     break
#                 s.sendto(data.encode(),addr)
#             if data == str("exit"):
#                 s.close()

# def __name__ = '__main__':
#     try:
#         hostname = socket.gethostname()
#         host = socket.gethostbyname(hostname)
#         # Add to check if argument is there or not
#         ThreadedServer(host, int(sys.argv[1]))
#     except Exception as e:
#         print(e)




import socket 
import threading
import json
import os
import signal
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db


HEADER = 64
PORT = 4063
# SERVER = "0.0.0.0"
SERVER = socket.gethostbyname(socket.gethostname())
print(f"SERVER is: {SERVER}")
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# TYPE = sys.argv[1]

cred = credentials.Certificate("thermal-hour-367420-firebase-adminsdk-1p9ea-7e59909035.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


def handle_client(conn, addr, type, client_num):
    print(f"[NEW CONNECTION] {addr} connected.")
    print(f"Client: {client_num} connected.")
    try:
        if type == 'local':
            connected = True
            while connected:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                print(f"msg_length: {msg_length}")
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print('new message is: ', msg)
                    if msg == DISCONNECT_MESSAGE:
                        connected = False

                    elif msg == 'quit':
                        connected = False

                    elif len(msg.split()) > 1:
                        # print(f"Before json loads: {msg}")
                        new_msg = json.loads(msg)
                        print(f"After json loads: {new_msg}")
                        key_first = list(new_msg.keys())[0]
                        val_first = new_msg[key_first][0]
                        val_length_first = new_msg[key_first][1]
                        print(f"Key: {key_first}, Value: {val_first}, Length: {val_length_first}")
                        temp_dict = {}
                        with open("memcache.txt", "r") as file:
                            for line in file:
                                temp_dict = json.loads(line)
                                # print(f"temp_dict is: {temp_dict}")

                        temp_dict[key_first] = (val_first, val_length_first)
                        with open("memcache.txt", "w") as file:
                            file.write(json.dumps(temp_dict))
                        
                        print(f"[{addr}] {new_msg}")
                        conn.send("STORED".encode(FORMAT))

                    elif len(msg.split()) == 1:
                        print(f"Get raw message is: {msg}")
                        new_msg = msg.split()[0]
                        print(f"Get message is: {new_msg}")
                        with open("memcache.txt", "r") as file:
                            for line in file:
                                temp_dict = json.loads(line)
                        if new_msg in temp_dict.keys():
                            conn.send(f"{new_msg} {temp_dict[new_msg][1]}\n{temp_dict[new_msg][0]}\nEND".encode(FORMAT))
                        else:
                            conn.send("-1".encode(FORMAT))

        elif type == 'firebase':
            connected = True
            while connected:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                print(f"msg_length: {msg_length}")
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print('new message is: ', msg)
                    if msg == DISCONNECT_MESSAGE:
                        connected = False

                    elif msg == 'quit':
                        connected = False

                    elif len(msg.split()) > 1:
                        # print(f"Before json loads: {msg}")
                        new_msg = json.loads(msg)
                        print(f"After json loads: {new_msg}")
                        key_first = list(new_msg.keys())[0]
                        val_first = new_msg[key_first][0]
                        val_length_first = new_msg[key_first][1]
                        print(f"Key: {key_first}, Value: {val_first}, Length: {val_length_first}")
                        temp_dict = {}
                        with open("memcache.txt", "r") as file:
                            for line in file:
                                temp_dict = json.loads(line)
                                # print(f"temp_dict is: {temp_dict}")

                        temp_dict[key_first] = (val_first, val_length_first)
                        doc_ref = db.collection(u'KVStore').document('memcache')
                        doc_ref.set(temp_dict)

                        print(f"[{addr}] {new_msg}")
                        conn.send("STORED".encode(FORMAT))

                    elif len(msg.split()) == 1:
                        print(f"Get raw message is: {msg}")
                        new_msg = msg.split()[0]
                        print(f"Get message is: {new_msg}")
                        users_ref = db.collection(u'KVStore')
                        docs = users_ref.stream()
                        for doc in docs:
                            temp_dict = doc.to_dict()
                        if new_msg in temp_dict.keys():
                            conn.send(f"{new_msg} {temp_dict[new_msg][1]}\n{temp_dict[new_msg][0]}\nEND".encode(FORMAT))
                        else:
                            conn.send("-1".encode(FORMAT))


            # connected = False

        # conn.close()
        
        
        if not connected:
            if msg == 'quit':
                print(f"Client {client_num} disconnected!")
                pid = os.getpid()
                os.kill(pid, signal.SIGTERM)
                conn.close()
            else:
                print(f"Client {client_num} disconnected!")
                # pid = os.getpid()
                # os.kill(pid, signal.SIGKILL)
                conn.close()
    except Exception as e:
        print(f"error is: {e}")
        print(f"Client {client_num} disconnected!")
        # server.shutdown(socket.SHUT_RDWR)
        conn.close()

        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, TYPE, threading.activeCount()))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
start()