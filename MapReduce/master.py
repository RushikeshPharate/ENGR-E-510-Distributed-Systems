
from multiprocessing import Process
import xmlrpc.server
import xmlrpc.client
import os
import socket
import threading
import json
import sys
# import re
import logging

from dotenv import load_dotenv
from time import sleep



def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-5s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

# def mapper_progress_checker():





def init_rpc_master_server(master_address, master_port):
    global server
    with xmlrpc.server.SimpleXMLRPCServer((master_address, int(master_port)),logRequests=False,allow_none=True) as server:
    
        def mapper_report_status(mapper_id, status):
            mapper_progress[int(mapper_id)] = status
        server.register_function(mapper_report_status, 'mapper_report_status')

        def reducer_report_status(reducer_id, status):
            reducer_progress[int(reducer_id)] = status
        server.register_function(reducer_report_status, 'reducer_report_status')

        server.serve_forever()


def handle_database_server(database_server, database_port):
    cmd = f"python3 database_server.py {database_server} {database_port}"
    os.system(cmd)


def handle_mapper(mapper_id, database_server, database_port, master_address, master_port, no_of_reducers):
    # print(f"I'm mapper {mapper_id} in master, my parent process is {os.getppid()} and process id is {os.getpid()}"

    # Its not possible to run this new script in the same process???
    cmd = f"python3 mapper_word_count.py {mapper_id} {database_server} {database_port} {master_address} {master_port} {no_of_reducers}"
    os.system(cmd)

    
def handle_reducer(reducer_id, database_server, database_port, master_address, master_port):
    cmd = f"python3 reducer_word_count.py {reducer_id} {database_server} {database_port} {master_address} {master_port}"
    os.system(cmd)


if __name__ == '__main__':
    load_dotenv()
    global logger
    global mappers_progress
    global reducer_progress

    master_address = os.getenv("MASTER_ADDRESS")
    master_port = int(os.getenv("MASTER_PORT"))
    database_server = os.getenv("DATABASE_SERVER")
    database_port = int(os.getenv("DATABASE_PORT"))
    no_of_mappers = int(os.getenv("NO_OF_MAPPERS"))
    no_of_reducers = int(os.getenv("NO_OF_REDUCERS"))
    # file_to_use = os.getenv("TXT_FILE_TO_USE")

    logger = setup_custom_logger("mapreduce")
    logger.info(f"Master Node started on {master_address}:{master_port}")

    # Starting database server
    p = Process(target=handle_database_server, args=(database_server, database_port,))
    p.start()
    logger.info(f"Database Server started on {database_server}:{database_port}")
    sleep(2)
    threading.Thread(target = init_rpc_master_server,args=(master_address, master_port)).start()
    sleep(2)

    db_server = xmlrpc.client.ServerProxy(f'http://{database_server}:{database_port}/')
    logger.info("Connected to database server")
    words = db_server.get_input_data()
    logger.info("Got input data from database server")
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
    res = db_server.set_master_split(mappers_assign)
    sleep(2)
    logger.info(f"Divided input into chunk of {jump} words and assigned it to {no_of_mappers} mappers")

    logger.info(f"Starting {no_of_mappers} mappers")
    
    mapper_progress = {}
    for i in range(no_of_mappers):
        mapper_progress[i + 1] = "PROCESSING" 
        p = Process(target=handle_mapper, args=(i + 1, database_server, database_port, master_address, master_port, no_of_reducers,))
        p.start()
        logger.info(f"Mapper {i + 1} is up")
    
    # Mapper Barrier
    logger.info("Barrier is UP")
    all_mappers_finished = False
    while not all_mappers_finished:
        sleep(1)
        for mapper_id in mapper_progress:
            logger.info(f"Mapper {mapper_id} status is: {mapper_progress[mapper_id]}")
        for mapper_id in mapper_progress:
            if mapper_progress[mapper_id] == "FAILED":
                p = Process(target=handle_mapper, args=(mapper_id, database_server, database_port, master_address, master_port, no_of_reducers,))
                p.start()
                break
            if mapper_progress[mapper_id] != "DONE":
                break
            all_mappers_finished = True

    logger.info("All the Mappers have Finished Processing and Barrier is down")

    logger.info(f"Starting {no_of_reducers} reducers")
    reducer_progress = {}
    for i in range(no_of_reducers):
        reducer_progress[i + 1] = "PROCESSING" 
        p = Process(target=handle_reducer, args=(i + 1, database_server, database_port, master_address, master_port,))
        p.start()
        logger.info(f"Reducer {i + 1} is up")
    
    # Reducer Barrier
    all_reducers_finished = False
    while not all_reducers_finished:
        sleep(1)
        for reducer_id in reducer_progress:
            logger.info(f"Reducer {reducer_id} status is: {reducer_progress[reducer_id]}")
        for reducer_id in mapper_progress:
            if reducer_progress[reducer_id] == "FAILED":
                p = Process(target=handle_reducer, args=(reducer_id, database_server, database_port, master_address, master_port,))
                p.start()
                break
            if reducer_progress[reducer_id] != 'DONE':
                break
            all_reducers_finished = True

    logger.info("All the Reducers have Finished Processing")
    
    db_server.stop_database_server()
    logger.info("Stopped Database Server")
    server.shutdown()
    logger.info("Finished Task. Terminating")

    
    # sys.exit(0)
    

    




    

    

    












# Implement Master process, who handles all these below processes

# Create new process for all mappers and reducers 
# All the mappers should get approximate same amount of data to process
# Mappers and reduces should run in parellel

# implement barrier, which will wait for all mapper to finish
# Implement Group by, which will accumulated the same keys
# implemen Hash function, so that we can assign same keys to the same reducer function

# If a mapper or reducer fails, then master will start that process again. --> fault tolerence


# should I consider upper and lower case words as 2 seperate??
# check our group by implementation

# should we return the mepper output to master and then store in KV store??
# what if master fails????
# Should we have fixed number of mappers and reduces?? or should it vary based in the inout size???
# how to make sure mapper process all the words without fail?? and if it fails what to do??




# Dependencies
# 1) python-dotenv