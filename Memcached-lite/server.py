import socket
import threading
import os, signal

class ThreadedServer(object):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_addr, port_number = socket.getaddrinfo(host, port)[0][4]
        self.sock.bind((host_addr, port_number))
        self.connection_count = 0

    def listen(self):
        self.sock.listen()
        print("Hello, I am a server")
        while True:
            try:
                client, address = self.sock.accept()
                print(f"connection {self.connection_count} from {address}")
                self.connection_count += 1
                th = threading.Thread(target = self.listenToClient,args = (client,address, self.sock))
                th.daemon = True
                th.start()
            except Exception as ex:
                self.sock.close()
                break
    
    def listenToClient(self, client, address, s):
        while True:
            try:
                isExitRcvd = False
                data = client.recv(256).decode().replace("\n","")
                print(f"got message from {address}")
                if not data:
                    break
                if data == str("hello"):
                    client.send("world\n".encode())
                    continue
                if data == str("goodbye"):
                    client.send("farewell\n".encode()) 
                    client.close()  
                    break
                if data == str("exit"):
                    client.send("ok\n".encode())
                    isExitRcvd = True
                    break
                data = data + "\n"
                client.send(data.encode())
            except:
                client.close()
                return False
        if isExitRcvd:
            client.close()
            s.shutdown(socket.SHUT_RDWR)
        
    # def sock_stop(self):
    #     print("inside sock_stop")
    #     pid = os.getpid()
    #     os.kill(pid, signal.SIGTERM)


def chat_server(iface:str, port:int, use_udp:bool) -> None:
    if not use_udp:
        ThreadedServer(iface,port).listen()
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            host_addr, port_number = socket.getaddrinfo(iface, port)[0][4]
            s.bind((host_addr, port))
            print("Hello, I am a server")
            while True:
                message, addr = s.recvfrom(256)
                data = message.decode().replace("\n","")
                print(f"got message from {addr}")
                if data == str("hello"):
                    s.sendto("world\n".encode(),addr)
                    continue
                if data == str("goodbye"):
                    s.sendto("farewell\n".encode(),addr)   
                    continue
                if data == str("exit"):
                    s.sendto("ok\n".encode(),addr)
                    break
                s.sendto(data.encode(),addr)
            if data == str("exit"):
                s.close()
