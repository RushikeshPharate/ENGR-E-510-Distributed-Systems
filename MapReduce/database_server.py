import xmlrpc.server
from time import sleep
import sys
from threading import Lock
import os
import re
import signal
import json


lock = Lock()




def get_mapper_input(mapper_id, mapper_start_byte, mapper_end_byte):
    lock.acquire()
    with open("./mapperInput/combinedTextFile.txt", "r") as f:
        f.seek(int(mapper_start_byte))
        data = f.read(int(mapper_end_byte) - int(mapper_start_byte))
        f.close()
    lock.release()
    return data


def set_mapper_output(map):
    lock.acquire()
    with open("./mappersOutput/mappers_output.txt", "r") as f:
        mapper_output = json.loads(f.read())
        f.close()
    
    mapper_dict = map
    for reducer_id in mapper_dict:
        if reducer_id in mapper_output:
            mapper_output[reducer_id] = mapper_output[reducer_id] + mapper_dict[reducer_id]
        else:
            mapper_output[reducer_id] = mapper_dict[reducer_id]

    with open("./mappersOutput/mappers_output.txt", "w") as f:
        f.write(json.dumps(mapper_output, ensure_ascii=False))
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


def set_reducer_output(reduce):
    lock.acquire()
    with open("./output/reducers_output.txt", "r") as f:
        reducer_output = json.loads(f.read())
        f.close()
   
    reducer_dict = reduce
    for word, val in reducer_dict.items():
        if word in reducer_output:
            reducer_output[word] += val
        else:
            reducer_output[word] = val

    with open("./output/reducers_output.txt", "w", encoding='utf8') as f:
        # f.write(json.dumps(reducer_output), ensure_ascii=False)
        json.dump(reducer_output, f, ensure_ascii=False)
        f.close()
    lock.release()
    return True

def set_input_files_offset(files_offset):
    global input_files_offset
    input_files_offset = files_offset

def get_input_files_offset():
    return input_files_offset

def main():
    database_server  = sys.argv[1]
    database_port = sys.argv[2]

    f = open("./mappersOutput/mappers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    f = open("./output/reducers_output.txt", "w")
    f.write(json.dumps({}))
    f.close()

    with xmlrpc.server.SimpleXMLRPCServer((str(database_server), int(database_port)), logRequests=False, allow_none=True) as server:
        server.register_function(get_mapper_input, "get_mapper_input")
        server.register_function(set_mapper_output, "set_mapper_output")
        server.register_function(get_reducer_input, "get_reducer_input")
        server.register_function(set_reducer_output,"set_reducer_output") 
        server.register_function(set_input_files_offset,"set_input_files_offset")
        server.register_function(get_input_files_offset,"get_input_files_offset")
        

        def stop_database_server():
            os.kill(os.getpid(), signal.SIGKILL)
        server.register_function(stop_database_server, "stop_database_server")
        server.serve_forever()

if __name__ == "__main__":
    main()