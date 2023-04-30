import xmlrpc.server
import xmlrpc.client
import sys
import time
import random


if __name__ == "__main__":

    server_address = sys.argv[1]
    # server_port = int(sys.argv[2])

    version_clock = {}

    var, val = "x", random.randint(21, 99)
    if var not in version_clock:
        version_clock[var] = 0
    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6486"}/')
    l_clock = server.set_var(var, val, version_clock[var])
    print(f"My logical clock for variable {var} is {version_clock[var]} and version clock received from server is {l_clock}")
    print(f"Updated my version clock")
    version_clock[var] = l_clock


    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6487"}/')
    v, l_clock = server.get_var(var, version_clock[var])
    print(f"GET({var}) request returned {var}={v}")
    print(f"My logical clock for variable {var} is {version_clock[var]} and version clock received from server is {l_clock}")
    version_clock[var] = l_clock
    print(f"Updated my version clock")


    server = xmlrpc.client.ServerProxy(f'http://{server_address}:{"6494"}/')
    v, l_clock = server.get_var(var, version_clock[var])
    print(f"GET({var}) request returned {var}={v}")
    print(f"My logical clock for variable {var} is {version_clock[var]} and version clock received from server is {l_clock}")
    version_clock[var] = l_clock
    print(f"Updated my version clock")

