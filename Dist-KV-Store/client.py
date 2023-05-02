import xmlrpc.server
import xmlrpc.client
import sys
import time


if __name__ == "__main__":

    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    action = sys.argv[3]
    var = sys.argv[4]
    if len(sys.argv) == 6:
        val = sys.argv[5]


    if action == "SET":
        x = time.time()
        server = xmlrpc.client.ServerProxy(f'http://{server_address}:{server_port}/')
        # print(f"SET request for SET({var}, {val}) returned {server.set_var(var, val)} and took {time.time() - x} time" )
        server.set_var(var, val)
        print(f"SET request for SET({var}, {val}) returned and took {time.time() - x} time" )

    elif action == "GET":
        y = time.time()
        server = xmlrpc.client.ServerProxy(f'http://{server_address}:{server_port}/')
        print(f"GET request for variable {var} returned {server.get_var(var)}  and took {time.time() - y} time", )
    


