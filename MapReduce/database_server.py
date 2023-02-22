import xmlrpc.server
from time import sleep
import sys
from threading import Lock
import os
import re


import json


lock = Lock()

def get_input_data():
    words = []
    for file in os.listdir("./inputFiles/"):
        if file.endswith(".txt"):
            f = open(f"./inputFiles/{file}", "r")
            for word in f.read().split():
                new_str = re.sub('[^a-zA-Z0-9\-]', '', word)
                words.append(new_str)
    return words


def set_master_split(mapper_assign_dict):
    with open("./mapperInput/mappers_assign.txt", "w") as f:
        f.write(json.dumps(mapper_assign_dict))
        f.close()
    return True


def get_mapper_input(mapper_id):
    lock.acquire()
    with open("./mapperInput/mappers_assign.txt", "r") as f:
        mapper_output = json.loads(f.read())[f"mapper {mapper_id}"]
        f.close()
    lock.release()
    return mapper_output


def set_mapper_output(mapper_dict):
    lock.acquire()
    with open("./mappersOutput/mappers_output.txt", "r") as f:
        mapper_output = json.loads(f.read())
        f.close()
    
    for reducer_id in mapper_dict:
        if reducer_id in mapper_output:
            mapper_output[reducer_id] = mapper_output[reducer_id] + mapper_dict[reducer_id]
        else:
            mapper_output[reducer_id] = mapper_dict[reducer_id]

    with open("./mappersOutput/mappers_output.txt", "w") as f:
        f.write(json.dumps(mapper_output))
        f.close()
    lock.release()
    return True


def get_reducer_input(reducer_id):
    lock.acquire()
    with open("./mappersOutput/mappers_output.txt", "r") as f:
        data = json.loads(f.read())
        f.close()
    lock.release()
    return data[reducer_id] if reducer_id in data else []


def set_reducer_output(reducer_dict):
    lock.acquire()
    with open("./output/reducers_output.txt", "r") as f:
        reducer_output = json.loads(f.read())
        f.close()
    
    for word, val in reducer_dict.items():
        if word in reducer_output:
            reducer_output[word] += val
        else:
            reducer_output[word] = val

    with open("./output/reducers_output.txt", "w") as f:
        f.write(json.dumps(reducer_output))
        f.close()
    lock.release()
    return True


def main():
    database_server  = sys.argv[1]
    database_port = sys.argv[2]

    f = open("./mapperInput/mappers_assign.txt", "w")
    f.close()

    f = open("./mappersOutput/mappers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    f = open("./output/reducers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    with xmlrpc.server.SimpleXMLRPCServer((str(database_server), int(database_port)), logRequests=False) as server:
        server.register_function(get_input_data, "get_input_data")
        server.register_function(set_master_split, "set_master_split")
        server.register_function(get_mapper_input, "get_mapper_input")
        server.register_function(set_mapper_output, "set_mapper_output")
        server.register_function(get_reducer_input, "get_reducer_input")
        server.register_function(set_reducer_output,"set_reducer_output") 
        

        def stop_database_server():
            print("Kill database request received from master")
            server.shutdown()
            sys.exit(0)
            # return True
        server.register_function(stop_database_server, "stop_database_server")
        server.serve_forever()

if __name__ == "__main__":
    main()