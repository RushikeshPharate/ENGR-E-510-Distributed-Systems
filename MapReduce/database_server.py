import xmlrpc.server
from time import sleep
import sys
from threading import Lock

import json


lock = Lock()


# Define the function to be called remotely
def add_numbers(x, y):
    return x + y

def set_mapper_output(dict_list):
    lock.acquire()
    with open("mappers_output.txt", "r") as f:
        data = json.loads(f.read())
        f.close()
    
    data += dict_list
    with open("mappers_output.txt", "w") as f:
        f.write(json.dumps(data))
        f.close()
    lock.release()
    return True


def main():
    print("Database Server Started")
    database_server  = sys.argv[1]
    database_port = sys.argv[2]

    f = open("mappers_output.txt", "w")
    f.write(json.dumps([]))
    f.close()

    with xmlrpc.server.SimpleXMLRPCServer((str(database_server), int(database_port)), logRequests=False) as server:
        server.register_function(add_numbers, 'add')
        server.register_function(set_mapper_output, "set_mapper_output")

        def stop_server():
            server.shutdown()
            return True
        server.register_function(stop_server, "stop_server")
        server.serve_forever()

if __name__ == "__main__":
    main()