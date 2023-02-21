import xmlrpc.server
from time import sleep
import sys
from threading import Lock

import json


lock = Lock()


def set_mapper_output(mapper_dict):
    lock.acquire()
    with open("mappers_output.txt", "r") as f:
        mapper_output = json.loads(f.read())
        f.close()
    
    for reducer_id in mapper_dict:
        if reducer_id in mapper_output:
            mapper_output[reducer_id] = mapper_output[reducer_id] + mapper_dict[reducer_id]
        else:
            mapper_output[reducer_id] = mapper_dict[reducer_id]

    with open("mappers_output.txt", "w") as f:
        f.write(json.dumps(mapper_output))
        f.close()
    lock.release()
    return True

def get_reducer_input(reducer_id):
    lock.acquire()
    with open("mappers_output.txt", "r") as f:
        data = json.loads(f.read())
        f.close()
    lock.release()
    return data[reducer_id] if reducer_id in data else []

def set_reducer_output(reducer_dict):
    lock.acquire()
    with open("reducers_output.txt", "r") as f:
        reducer_output = json.loads(f.read())
        f.close()
    
    for word, val in reducer_dict.items():
        if word in reducer_output:
            reducer_output[word] += val
        else:
            reducer_output[word] = val

    with open("reducers_output.txt", "w") as f:
        f.write(json.dumps(reducer_output))
        f.close()
    lock.release()
    return True


def main():
    print("Database Server Started")
    database_server  = sys.argv[1]
    database_port = sys.argv[2]

    f = open("mappers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    f = open("reducers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    with xmlrpc.server.SimpleXMLRPCServer((str(database_server), int(database_port)), logRequests=False) as server:
        server.register_function(set_mapper_output, "set_mapper_output")
        server.register_function(get_reducer_input, "get_reducer_input")
        server.register_function(set_reducer_output,"set_reducer_output") 


        def stop_database_server():
            server.shutdown()
            return True
        server.register_function(stop_database_server, "stop_database_server")
        server.serve_forever()

if __name__ == "__main__":
    main()