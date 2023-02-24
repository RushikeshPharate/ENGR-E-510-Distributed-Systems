
import os
import sys
import json
import xmlrpc.client
import xmlrpc.server
from time import sleep
import threading
import signal
import random
import re


def create_mapper_rpc_server(mapper_address, mapper_port):
    with xmlrpc.server.SimpleXMLRPCServer((mapper_address, int(mapper_port)),logRequests=False,allow_none=True) as server:
        
        def get_mapper_progress():
            if mapper_progress == 100:
                sleep(3)
            return mapper_progress
        server.register_function(get_mapper_progress, "get_mapper_progress")

        def stop_mapper_server():
            # print(f"Mapper PID to kill: {os.getpid()}")
            os.kill(os.getpid(), signal.SIGKILL)
        server.register_function(stop_mapper_server, "stop_mapper_server")
        server.serve_forever()


def get_reducer_id(str_input, no_of_reducers):
    hash_value = 0
    for char in str_input:
        hash_value = (hash_value * 31 + ord(char)) % int(no_of_reducers)
    return str(hash_value + 1)


def mapper():
    global mapper_progress

    mapper_progress = 0
    mapper_id = sys.argv[1]
    master_address = sys.argv[2]
    master_port = sys.argv[3]
    no_of_reducers = sys.argv[4]
    mapper_address = sys.argv[5]
    mapper_port = sys.argv[6]
    mapper_start_byte = sys.argv[7]
    mapper_end_byte = sys.argv[8]
    
    try:
        threading.Thread(target = create_mapper_rpc_server, args = (mapper_address, mapper_port, )).start()
        sleep(3)
        
        m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
        
        # if random.randint(1,4) == 2:
        #     raise Exception("For testing the Fault Tolerence"
        import pdb
        pdb.set_trace()
        print("ASD")
        input_files_offset = m_server.get_input_files_offset()
        print(input_files_offset)
        
        data = m_server.get_mapper_input(mapper_id, mapper_start_byte, mapper_end_byte)
        print(data)
        
        # words = data.split()
        # l = len(words)
        # mapper_output = {}
        # for i, word in enumerate(words):
        #     mapper_progress = ((i + 1) / l) * 100
        #     new_str = re.sub('[^a-zA-Z0-9]', '', word)
        #     reducer_id = get_reducer_id(new_str, no_of_reducers)
        #     if reducer_id not in mapper_output:
        #         mapper_output[reducer_id] = []
        #     mapper_output[reducer_id].append((word,1))
        # # print(f"Mapper {mapper_id} output: {mapper_output}")
        # result = m_server.set_mapper_output(mapper_output)
        # # print(f"Mapper {mapper_id} End")
        
    except Exception as e:
        os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    mapper()


