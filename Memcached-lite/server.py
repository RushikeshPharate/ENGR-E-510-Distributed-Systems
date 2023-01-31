import socket 
import threading
import json
import os
import signal
import sys



HEADER = 64
PORT = 4063
SERVER = socket.gethostbyname(socket.gethostname())
print(f"SERVER is: {SERVER}")
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


def handle_client(conn, addr, client_num):
    print(f"[NEW CONNECTION] {addr} connected.")
    print(f"Client: {client_num} connected.")
    try:
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
        thread = threading.Thread(target=handle_client, args=(conn, addr, threading.activeCount()))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
start()