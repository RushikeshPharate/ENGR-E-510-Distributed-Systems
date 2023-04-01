import xmlrpc.server
import xmlrpc.client
import sys


if __name__ == "__main__":

    server_address = sys.argv[1]
    server_port = int(sys.argv[2])

    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{server_port}/')
    for i in range(1, 2):
        print(f"Current ID for request {i} is : {server.get_id()} ")

    


