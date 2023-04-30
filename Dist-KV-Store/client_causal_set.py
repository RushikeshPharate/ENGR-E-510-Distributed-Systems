import xmlrpc.server
import xmlrpc.client
import sys
import time
import random


if __name__ == "__main__":

    server_address = sys.argv[1]

    version_clock = {}

    # vars = ["x", "x", "x"]
    # var, val = vars[random.randint(0,2)],random.randint(21, 99)
    var, val = "x", 21
    if var not in version_clock:
        version_clock[var] = 0
    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6486"}/')
    l_clock = server.set_var(var, val, version_clock[var])
    # print(f"My logical clock for variable {var} is {version_clock[var]} and version clock received from server is {l_clock}")
    # print(f"Updated my version clock")
    version_clock[var] = l_clock
