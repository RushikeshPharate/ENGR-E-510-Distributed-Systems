import socket
import threading
import os, signal



def chat_client(host:str, port:int, use_udp:bool) -> None:
    if not use_udp:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Hello, I am a client")
            host_addr, port_number = socket.getaddrinfo(host, port)[0][4]
            s.connect((host_addr, port_number))
            while True:
                try:
                    inp = input()
                    if inp == "":
                        continue
                    s.send(inp.encode())
                    data = s.recv(256).decode().replace("\n","")
                    print(data)
                    if inp in ["goodbye", "exit"]:
                        break
                except KeyboardInterrupt:
                    s.close()
            s.close()
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            print("Hello, I am a client")
            host_addr, port_number = socket.getaddrinfo(host, port)[0][4]
            while True:
                try:
                    inp = input()
                    if inp == "":
                        continue
                    s.sendto(inp.encode(),(host_addr,port_number))
                    msg, server = s.recvfrom(256)
                    data = msg.decode().replace("\n","")
                    print(data)
                    if inp in ["goodbye", "exit"]:
                        break
                except KeyboardInterrupt:
                    s.close()
            s.close()   