
from multiprocessing import Process
import xmlrpc.server
import os
import socket
import threading
import json
import sys
import re

from dotenv import load_dotenv
from time import sleep

# import random
# import math

def init_rpc_master_server(master_address, master_port):
    with xmlrpc.server.SimpleXMLRPCServer((master_address, int(master_port)),logRequests=False,allow_none=True) as server:
    
        def mapper_finished(mapper_id):
            # print(f"Mapper {mapper_id} finished processing")
            mapper_progress[int(mapper_id)] = "FINISHED"
            return True
        server.register_function(mapper_finished, 'mapper_finished')
        server.serve_forever()

def handle_mapper(mapper_id, database_server, database_port, master_address, master_port):
    # print(f"Mapper {mapper_id} started")
    # print(f"I'm mapper {mapper_id} in master, my parent process is {os.getppid()} and process id is {os.getpid()}")
    # print("###############################")

    # Its not possible to run this new script in the same process???
    cmd = f"python3 mapper_word_count.py {mapper_id} {database_server} {database_port} {master_address} {master_port}"
    os.system(cmd)

    
def handle_database_server(database_server, database_port):
    cmd = f"python3 database_server.py {database_server} {database_port}"
    os.system(cmd)


if __name__ == '__main__':
    load_dotenv()

    print("Master Node Started....")

    master_address = os.getenv("MASTER_ADDRESS")
    master_port = int(os.getenv("MASTER_PORT"))
    database_server = os.getenv("DATABASE_SERVER")
    database_port = int(os.getenv("DATABASE_PORT"))
    no_of_mappers = int(os.getenv("NO_OF_MAPPERS"))
    no_of_reducers = int(os.getenv("NO_OF_REDUCERS"))
    file_to_use = os.getenv("TXT_FILE_TO_USE")

    # Starting database server
    p = Process(target=handle_database_server, args=(database_server, database_port,))
    p.start()
    sleep(2)
    threading.Thread(target = init_rpc_master_server,args=(master_address, master_port)).start()
    sleep(2)

    f = open(f"{file_to_use}", "r")
    words = []
    for word in f.read().split():
        new_str = re.sub('[^a-zA-Z0-9]', '', word)
        words.append(new_str)
    f.close()

    LENGTH = len(words)
    jump = LENGTH // no_of_mappers
    start = 0
    end = jump
    mappers_assign = {}
    for i in range(no_of_mappers):
        if i == no_of_mappers - 1:
            col = words[start:]
        elif end < LENGTH:
            col = words[start:end]
            start = end
            end += jump
        else:
            col = words[start:]
        mappers_assign[f"mapper {i + 1}"] = col

    f = open("mappers.txt", "w")
    f.write(json.dumps(mappers_assign))
    f.close()
    print("Finished Assigning Words to Mappers")

    print(f"Starting {no_of_mappers} mappers...")
    global mappers_progress
    mapper_progress = {}
    for i in range(no_of_mappers):
        mapper_progress[i + 1] = "IN PROGRESS" 
        p = Process(target=handle_mapper, args=(i + 1, database_server, database_port, master_address, master_port,))
        p.start()
    
    # Barrier
    print("Barrier is Up")
    all_mappers_finished = False
    while not all_mappers_finished:
        sleep(2)
        for mapper_id in mapper_progress:
            if mapper_progress[mapper_id] != 'FINISHED':
                break
            all_mappers_finished = True

    print("All the Mappers have Finished Processing and Barrier is down")
    

    

    











# Implement Master process, who handles all these below processes

# Create new process for all mappers and reducers 
# All the mappers should get approximate same amount of data to process
# Mappers and reduces should run in parellel

# implement barrier, which will wait for all mapper to finish
# Implement Group by, which will accumulated the same keys
# implemen Hash function, so that we can assign same keys to the same reducer function

# If a mapper or reducer fails, then master will start that process again. --> fault tolerence


# should we return the mepper output to master and then store in KV store??
# what if master fails????
# Should we have fixed number of mappers and reduces?? or should it vary based in the inout size???
# how to make sure mapper process all the words without fail?? and if it fails what to do??




# Dependencies
# 1) python-dotenv