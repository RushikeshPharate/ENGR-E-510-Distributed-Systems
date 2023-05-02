import xmlrpc.server
import xmlrpc.client
import sys
import time


if __name__ == "__main__":

    server_address = sys.argv[1]
    
    var, val = "x", 51
    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6486"}/')
    server.set_var(var, val)
    print(f"SET request for SET({var}, {val}) returned " )


    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6487"}/')
    print(f"GET request for variable {var} returned {server.get_var(var)} " )
    
    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6494"}/')
    print(f"GET request for variable {var} returned {server.get_var(var)} " )

