
import socket
import json
import random
import sys

HEADER = 64
PORT = 4063
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = str(sys.argv[1])
# ADDR = ("10.128.0.5", PORT)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# client.connect((SERVER, PORT))
client.connect((SERVER, PORT))

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

connected = True
while connected:
    inp = input("Enter 'set' to store data or 'get' to retrieve data: \n")
    # inputs = ['set cricket 4', 'get cricket']
    # inp = random.choice(inputs)
    # inp = 'quit'
    # print(f"input is: {inp}")
    split_val = inp.split()
    kv_pair = {}
    if split_val[0] == 'get':
        send(split_val[1])
    elif split_val[0] == 'set':

        bytes_len = int(split_val[2])
        # val = 'bat'
        val = input()
        final_val = val[0:bytes_len]
        kv_pair[split_val[1]] = (final_val, bytes_len)
        send(json.dumps(kv_pair))
    elif split_val[0] == 'quit':
        print('Quitting')
        send(inp)
        break
        # connected = False
    else:
        print("Invalid input! Only 'get', 'set' or 'quit' as the first word is accepted")
    send(DISCONNECT_MESSAGE)
    break