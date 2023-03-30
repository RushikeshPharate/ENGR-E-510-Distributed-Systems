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
import logging
from collections import deque

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

def update_id(num):
    global id_variable
    global logger

    logger.info(f"Updated id from {id_variable} to {int(num)} on server {server_id}")
    id_variable = int(num)
    return True

def insert_into_queue(s_id):

    
    global id_variable
    global server_address_details
    # global p_server
    global s_clients
    global logger
    global update_queue
    

    logger.info(f"Primary server received an message from server {s_id}")
    
    temp = id_variable
    id_variable += 1 
    
    for s in s_clients:
        if s == str(s_id):
            continue
        flag = s_clients[s].update_id(str(id_variable))
    logger.info(f"Updated id from {temp} to {id_variable} on server {server_id}")
    return id_variable

def get_id():
    global p_server
    global id_variable
    global logger

    logger.info(f"Server {server_id} received get_id() request")
    if server_id != 1:
        ans = p_server.insert_into_queue(server_id)
    else:
        ans = insert_into_queue(server_id)
    
    logger.info(f"Updated id from {id_variable} to {ans} on server {server_id}")
    id_variable = ans
    return ans


def create_rpc_server(server_id, server_address, server_port):
    with xmlrpc.server.SimpleXMLRPCServer((server_address, int(server_port)), logRequests=False,allow_none=True) as server:
        
        server.register_function(update_id, "update_id")    
        
        if server_id == 1:
            server.register_function(insert_into_queue, "insert_into_queue")

        server.register_function(get_id, "get_id")


        server.serve_forever()




if __name__ == '__main__':

    global id_variable
    global server_address_details
    global p_server
    global s_clients
    global logger
    global server_id
    global update_queue

    update_queue = deque()

    id_variable = 0

    server_id = int(sys.argv[1])
    server_address = sys.argv[2]
    server_port = sys.argv[3]
    primary_server_address = sys.argv[4]
    primary_server_port = sys.argv[5]
    master_address = sys.argv[6]
    master_port = sys.argv[7]

    logger = setup_custom_logger("distributed-sequencer")

    # get other server details from master
    if server_id == 1:
        # get data
        logger.info(f"Server {server_id} is the primary server")
        master = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
        server_address_details = master.get_all_server_details()
        
        logger.info(f"Primary server got details of all other servers")
    try:
        threading.Thread(target = create_rpc_server, args = (server_id, server_address, server_port, )).start()
        sleep(3)

        # connection to primary server
        if server_id != 1:
            p_server = xmlrpc.client.ServerProxy(f'http://{primary_server_address}:{primary_server_port}/')
            logger.info(f"Server {server_id} created an connection to primary server")
        elif server_id == 1:
            # Connection from primary server to all other servers
            s_clients = {}
            for i in server_address_details:
                if i == "1":
                    continue
                s = xmlrpc.client.ServerProxy(f'http://{server_address_details[i][0]}:{server_address_details[i][1]}/')
                s_clients[i] = s
                logger.info(f"Primary Server created an connection to server {i}")
        
        logger.info(f"Server {server_id} is READY")

    except Exception as e:
        logger.error(f"Error in server {server_id}")
        print(e)


