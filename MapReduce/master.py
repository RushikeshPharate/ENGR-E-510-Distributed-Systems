
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
import signal

from dotenv import load_dotenv
from time import sleep, time


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


def divide_input(no_of_mappers):

    f_combined = open("./mapperInput/combinedTextFile.txt", "a+")
    for file in os.listdir("./inputFiles/"):
        if file.endswith(".txt"):
            f = open(f"./inputFiles/{file}", "r")
            f_combined.write('\n')
            f_combined.write(f.read())
            f.close()
    f_combined.close()
    
    with open("./mapperInput/combinedTextFile.txt", 'r') as fp:
        total_lines = len(fp.readlines())
        fp.close()
    
    logger.info(f"Total {total_lines} lines to process")
    lines_per_mapper = total_lines // no_of_mappers
    start = 0
    end = lines_per_mapper
    mapper_assign = {}
    for i in range(no_of_mappers):
        if i == no_of_mappers - 1:
            mapper_assign[i + 1] = [start, total_lines]
        elif end < total_lines:
            mapper_assign[i + 1] = [start, end]
            start = end
            end += lines_per_mapper
        else:
            mapper_assign[i + 1] = [start, total_lines] 
        logger.info(f"Mapper {i + 1} will process {mapper_assign[i + 1][1] - mapper_assign[i + 1][0]} lines")
    return mapper_assign


def split_input(no_of_mappers):
    input_files_offset = {}
    f_combined = open("./mapperInput/combinedTextFile.txt", "a+")
    offset_start = 0
    for file in os.listdir("./inputFiles/"):
        if file.endswith(".txt"):
            f = open(f"./inputFiles/{file}", "r")
            f_combined.write(f.read())
            offset_end = f_combined.tell()
            input_files_offset[file] = [offset_start, offset_end]
            offset_start = offset_end
            f.close()
    f_combined.close()

    f_combined = open("./mapperInput/combinedTextFile.txt", "r")
    logger.info(f"Total {offset_end} bytes to read")
    bytes_per_mapper = offset_end // no_of_mappers
    start = 0
    
    f_combined.seek(bytes_per_mapper)
    while f_combined.read(1) not in ["\n", "", " "]:
        f_combined.seek(f_combined.tell())
    end = f_combined.tell()

    mapper_assign = {}
    for i in range(no_of_mappers):
        if i == no_of_mappers - 1:
            mapper_assign[i + 1] = [start, offset_end]
        elif end < offset_end:
            mapper_assign[i + 1] = [start, end]
            start = end

            f_combined.seek(end + bytes_per_mapper)
            while f_combined.read(1) not in ["\n", "", " "]:
                f_combined.seek(f_combined.tell())
            end = f_combined.tell()
            # end += bytes_per_mapper
        else:
            mapper_assign[i + 1] = [start, offset_end]
        logger.info(f"Mapper {i + 1} will process {mapper_assign[i + 1][1] - mapper_assign[i + 1][0]} bytes")
    return mapper_assign, input_files_offset


def mapper_progress_checker(mapper_id, p, mapper_address, mapper_port):
    start_time = time()
    mapper_server = xmlrpc.client.ServerProxy(f'http://{mapper_address}:{mapper_port}/') 
    prog = 0
    temp1 = -1
    temp2 = -2
    temp3 = -3
    while prog != 100:
        try:
            prog = int(mapper_server.get_mapper_progress())
        except Exception as e:
            logger.error(f"Mapper {mapper_id} is not responding - [Connection Refused]")
            logger.info(f"Terminating mapper {mapper_id}")
            p.kill()
            # p.close()
            sleep(2)
            mapper_status[mapper_id] = "FAILED"
            return
        temp3 = temp2
        temp2 = temp1
        temp1 = prog
        if prog != 0 and temp1 == temp2 == temp3:
            logger.error(f"Mapper {mapper_id} is not processing - [No Progress]")
            logger.info(f"Terminating mapper {mapper_id}")
            try:
                mapper_server.stop_mapper_server()
            except:
                pass 
            p.kill()
            # p.close()
            sleep(2)
            mapper_status[mapper_id] = "FAILED"
            return
        elif prog == 0:
            curr_time = time()
            if curr_time - start_time > 180:
                logger.error(f"Mapper {mapper_id} is not processing - [30 sec Time Limit Exceeded")
                logger.info(f"Terminating mapper {mapper_id}")
                try:
                    mapper_server.stop_mapper_server()
                except:
                    pass
                p.kill()
                # p.close()
                sleep(2)
                mapper_status[mapper_id] = "FAILED"
                return

        sleep(1)
        logger.info(f"Mapper {mapper_id} progress: {prog}%")
    logger.info(f"Mapper {mapper_id} finished processing")
    try:
        mapper_server.stop_mapper_server()
    except:
        pass
    mapper_status[mapper_id] = "DONE"
    mapper_set.remove(mapper_id)
    p.terminate()
    # p.kill()
    # p.close()
    return


def reducer_progress_checker(reducer_id, p, reducer_address, reducer_port):
    start_time = time()
    reducer_server = xmlrpc.client.ServerProxy(f'http://{reducer_address}:{reducer_port}/') 
    prog = 0
    temp1 = -1
    temp2 = -2
    temp3 = -3
    while prog != 100:
        try:
            prog = int(reducer_server.get_reducer_progress())
        except Exception as e:
            logger.error(f"Reducer {reducer_id} is not responding - [Connection Refused]")
            logger.info(f"Terminating reducer {reducer_id}")
            p.kill()
            # p.close()
            sleep(2)
            reducer_status[reducer_id] = "FAILED"
            return
        temp3 = temp2
        temp2 = temp1
        temp1 = prog
        if prog != 0 and temp1 == temp2 == temp3:
            logger.error(f"Reducer {reducer_id} is not processing - [No Progress]")
            logger.info(f"Terminating reducer {reducer_id}")
            try:
                reducer_server.stop_reducer_server()
            except:
                pass
            p.kill()
            # p.close()
            sleep(2)
            reducer_status[reducer_id] = "FAILED"
            return
        elif prog == 0:
            curr_time = time()
            if curr_time - start_time > 180:
                logger.error(f"Reducer {reducer_id} is not processing - [30 sec Time Limit Exceeded]")
                logger.info(f"Terminating reducer {reducer_id}")
                try:
                    reducer_server.stop_reducer_server()
                except:
                    pass
                p.kill()
                # p.close()
                sleep(2)
                reducer_status[reducer_id] = "FAILED"
                return

        sleep(1)
        logger.info(f"Reducer {reducer_id} progress: {prog}%")

    logger.info(f"Reducer {reducer_id} finished processing")
    
    try:
        reducer_server.stop_reducer_server()
    except:
        pass
    reducer_status[reducer_id] = "DONE"
    reducer_set.remove(reducer_id)
    p.terminate()
    # p.kill()
    # p.close()
    return


def handle_database_server(master_address, master_port):
    cmd = f"python3 database_server.py {master_address} {master_port}"
    os.system(cmd)


def handle_mapper(mapper_id, master_address, master_port, no_of_reducers, mapper_address, mapper_port, mapper_to_use, mapper_start_byte, mapper_end_byte):
    # print(f"I'm mapper {mapper_id} in master, my parent process is {os.getppid()} and process id is {os.getpid()}"

    # Its not possible to run this new script in the same process???
    cmd = f"python3 {mapper_to_use} {mapper_id} {master_address} {master_port} {no_of_reducers} {mapper_address} {mapper_port} {mapper_start_byte} {mapper_end_byte}"
    os.system(cmd)

    
def handle_reducer(reducer_id, master_address, master_port, reducer_address, reducer_port, reducer_to_use):
    cmd = f"python3 {reducer_to_use} {reducer_id} {master_address} {master_port} {reducer_address} {reducer_port}"
    os.system(cmd)


if __name__ == '__main__':

    master_start = time()

    global logger
    global mappers_progress
    global mapper_status
    global mapper_set
    global reducer_progress
    global reducer_status
    global reducer_set

    data = json.load(open('userInput.json'))

    master_address = data["MASTER_ADDRESS"]
    master_port = int(data["MASTER_PORT"])
    # database_server = data["DATABASE_SERVER"]
    database_server = data["MASTER_ADDRESS"]
    # database_port = int(data["DATABASE_PORT"])
    database_port = int(data["MASTER_PORT"])
    no_of_mappers = int(data["NO_OF_MAPPERS"])
    no_of_reducers = int(data["NO_OF_REDUCERS"])
    mapper_details = data["MAPPER_DETAILS"]
    reducer_details = data["REDUCER_DETAILS"]
    mapper_to_use = data["MAPPER_TO_USE"]
    reducer_to_use = data["REDUCER_TO_USE"]

    logger = setup_custom_logger("mapreduce")
    logger.info(f"Master Node started on {master_address}:{master_port}")

    # Starting database server
    database_process = Process(target=handle_database_server, args=(master_address, master_port,))
    database_process.start()
    logger.info(f"Process for handling data operations started")
    sleep(2)

    db_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
    # # logger.info("Connected to database server")
    
    f = open("./mapperInput/combinedTextFile.txt", "w")
    f.close()

    mapper_assign, input_files_offset = split_input(no_of_mappers)
    # print(input_files_offset)
    # print(mapper_assign)
    db_server.set_input_files_offset(input_files_offset)
    # logger.info(f"Starting {no_of_mappers} mappers")
     
    mapper_progress = {}
    mapper_status = {}
    mapper_set = set()
    for i in range(no_of_mappers):
        p = Process(target=handle_mapper, args=(i + 1, master_address, master_port, no_of_reducers, mapper_details[i][0], mapper_details[i][1], mapper_to_use, mapper_assign[i + 1][0], mapper_assign[i + 1][1]))
        p.start()
        mapper_progress[i + 1] = p 
        mapper_status[i + 1] = "PROCESSING"
        mapper_set.add(i + 1)
        logger.info(f"Mapper {i + 1} is up")

    sleep(3)

    # # Mapper Barrier
    # logger.info("Barrier is UP")
    # for mapper_id in mapper_progress:
    #     threading.Thread(target = mapper_progress_checker, args = (mapper_id, mapper_progress[mapper_id], mapper_details[mapper_id - 1][0], mapper_details[mapper_id - 1][1])).start()
    
    # sleep(2)

    all_mappers_finished = False
    while not all_mappers_finished:
        sleep(4)
        for mapper_id in mapper_status:
            if mapper_status[mapper_id] == "PROCESSING":
                continue
            if mapper_status[mapper_id] == "FAILED":
                logger.info(f"Starting mapper {mapper_id} again on {mapper_details[mapper_id - 1][0]}:{mapper_details[mapper_id - 1][1]}")
                p = Process(target=handle_mapper, args=(mapper_id, master_address, master_port, no_of_reducers, mapper_details[mapper_id - 1][0], mapper_details[mapper_id - 1][1], mapper_to_use, mapper_assign[i + 1][0], mapper_assign[i + 1][1]))
                p.start()
                sleep(2)
                threading.Thread(target = mapper_progress_checker, args = (mapper_id, mapper_progress[mapper_id], mapper_details[mapper_id - 1][0], mapper_details[mapper_id - 1][1])).start()
                sleep(2)
                # logger.info(f"MAPPER {mapper_id} IS STARTED AGAIN")
                mapper_progress[mapper_id] = p
                mapper_status[mapper_id] = "PROCESSING"
                break
            if not mapper_set:
                all_mappers_finished = True
    sleep(3)
    # print(mapper_status)
    logger.info("All the Mappers have Finished Processing and Barrier is down")

    logger.info(f"Starting {no_of_reducers} reducers")
    reducer_progress = {}
    reducer_status = {}
    reducer_set = set()
    for i in range(no_of_reducers):
        p = Process(target=handle_reducer, args=(i + 1, master_address, master_port, reducer_details[i][0], reducer_details[i][1], reducer_to_use))
        p.start()
        reducer_progress[i + 1] = p
        reducer_status[i + 1] = "PROCESSING"
        reducer_set.add(i + 1)
        logger.info(f"Reducer {i + 1} is up")
    
    sleep(3)

    for reducer_id in reducer_progress:
        threading.Thread(target = reducer_progress_checker, args = (reducer_id, reducer_progress[reducer_id], reducer_details[reducer_id - 1][0], reducer_details[reducer_id - 1][1])).start()

    sleep(2)

    # Reducer Barrier
    all_reducers_finished = False
    while not all_reducers_finished:
        sleep(4)
        for reducer_id in reducer_status:
            if reducer_status[reducer_id] == "PROCESSING":
                continue
            if reducer_status[reducer_id] == "FAILED":
                logger.info(f"Starting reducer {reducer_id} again on {reducer_details[reducer_id - 1][0]}:{reducer_details[reducer_id - 1][1]}")
                p = Process(target=handle_reducer, args=(reducer_id, master_address, master_port, reducer_details[reducer_id - 1][0], reducer_details[reducer_id - 1][1],reducer_to_use))
                p.start()
                sleep(2)
                threading.Thread(target = reducer_progress_checker, args = (reducer_id, reducer_progress[reducer_id], reducer_details[reducer_id - 1][0], reducer_details[reducer_id - 1][1])).start()
                sleep(2)
                reducer_progress[reducer_id] = p
                reducer_status[reducer_id] = "PROCESSING"
                break
            if not reducer_set:
                all_reducers_finished = True

    sleep(3)
    logger.info("All the Reducers have Finished Processing")

    try:
        db_server.stop_database_server()
    except:
        pass
    logger.info(f"Database processes terminated")
    logger.info(f"Run took: {time() - master_start} seconds")
    logger.info("Finished Task. Terminating")
    os.kill(os.getpid(), signal.SIGKILL)




# Implement Master process, who handles all these below processes

# Create new process for all mappers and reducers 
# All the mappers should get approximate same amount of data to process
# Mappers and reduces should run in parellel

# implement barrier, which will wait for all mapper to finish
# Implement Group by, which will accumulated the same keys
# implement Hash function, so that we can assign same keys to the same reducer function


# should we return the mepper output to master and then store in KV store??
# what if master fails????


# known issues
# Dividing input into bytes results in some broken words -> Consider a word starts at byte 10 and end ends in 20 and we are using 2 mappers
# mapper 1 is responsible for first 12 bytes and remaining bytes will be processed by mapper 2. This will result in the words spliting in two.
