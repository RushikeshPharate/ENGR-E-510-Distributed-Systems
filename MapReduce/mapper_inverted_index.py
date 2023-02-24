
import os
import sys
import json
import xmlrpc.client
import xmlrpc.server
from time import sleep, time
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

def get_file_name_and_word_index(start_byte, file_offset):
    for file, start_end_range in file_offset.items():
        if start_byte in range(start_end_range[0], start_end_range[1]):
            return file, start_byte - start_end_range[0]


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

        input_files_offset = m_server.get_input_files_offset()
        # print(f"input file offset: {input_files_offset}")

        data = m_server.get_mapper_input(mapper_id, mapper_start_byte, mapper_end_byte)
        mapper_output = {}
        word_match_dict  = {}
        for match in re.finditer(r'\S+', data):
            index, word = match.start(), match.group()
            # print(f"Mapper {mapper_id} index: {index}, {word}")
            mapper_progress = ((index + 1) / (int(mapper_end_byte) - int(mapper_start_byte))) * 100
            file_name, file_index = get_file_name_and_word_index(int(mapper_start_byte) + index, input_files_offset)
            # print(f"Mapper {mapper_id} file return : {file_name} , {file_index}")
            if word not in word_match_dict:
                word_match_dict[word] = []
            word_match_dict[word].append([file_name, file_index])

        # print(f"Mapper {mapper_id} Word match dict : {word_match_dict}")
        for word in word_match_dict:
            reducer_id = get_reducer_id(word, no_of_reducers)
            if reducer_id not in mapper_output:
                mapper_output[reducer_id] = []
            mapper_output[reducer_id].append({word: word_match_dict[word]})
        
        # start = time()
        result = m_server.set_mapper_output(mapper_output)
        # print(f"Time taken to post in DB by Mapper {mapper_id} is : {time() - start}")
        # print(f"Mapper {mapper_id} output: {mapper_output}")
        # print(mapper_progress)
        mapper_progress = 100
        # print(f"Mapper {mapper_id} End")

    except Exception as e:
        print(e)
        os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    mapper()


