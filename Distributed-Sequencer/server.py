import os
import threading

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

global lock
lock = threading.Lock()


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


def update_id(num, s_id):
    global id_variable
    global logger
    global received_response_from_primary
    global server_id

    logger.info(f"Updated id from {id_variable} to {int(num)} on server {server_id}")
    id_variable = int(num)
    if int(s_id) == int(server_id):
        received_response_from_primary = True
    return True


def process_message(s_id):
    global message_queue
    global id_variable
    global s_clients
    global logger

    lock.acquire()

    temp = id_variable
    id_variable += 1 
    
    logger.info(f"Updated id from {temp} to {id_variable} on server {server_id}")
    
    for s in s_clients:
        if s == str(s_id):
            continue
        flag = s_clients[s].update_id(str(id_variable), str(s_id))
    if str(s_id) != "1":
        f = s_clients[str(s_id)].update_id(str(id_variable), str(s_id))
    else:
        update_id(str(id_variable), str(s_id))
    
    sleep(1)
    lock.release()

    return id_variable


def insert_into_queue(s_id):

    global id_variable
    global server_address_details
    global s_clients
    global logger
    global message_queue

    logger.info(f"Primary server received an message from server {s_id}")
    
    th = threading.Thread(target = process_message, args = (s_id,))
    th.daemon = True
    th.start()
    th.join()

def send_to_primary():
    global p_server
 
    if server_id != 1:
        ans = p_server.insert_into_queue(server_id)
    else:
        ans = insert_into_queue(server_id)
    return

def get_id():
    
    lock.acquire()

    global p_server
    global id_variable
    global logger
    global received_response_from_primary

    logger.info(f"Server {server_id} received get_id() request")
    th = threading.Thread(target = send_to_primary)
    th.daemon = True
    th.start()

    lock.release()
    
    while True:
        sleep(0.5)
        if received_response_from_primary:
            received_response_from_primary = False
            return id_variable
    


def create_rpc_server(server_id, server_address, server_port):
    with xmlrpc.server.SimpleXMLRPCServer((server_address, int(server_port)), logRequests=False,allow_none=True) as server:
        
        server.register_function(update_id, "update_id")    
        
        if server_id == 1:
            server.register_function(insert_into_queue, "insert_into_queue")

        # server.register_function(get_id, "get_id")


        server.serve_forever()


def create_rpc_server_for_client_requests(server_id, server_address, server_port):
    global logger

    logger.info(f"SERVER {server_id} CAN HANDLE CLIENT REQUESTS ON {server_address}:{server_port}")
    
    with xmlrpc.server.SimpleXMLRPCServer((server_address, int(server_port)), logRequests=False,allow_none=True) as server:
        server.register_function(get_id, "get_id")
        server.serve_forever()

if __name__ == '__main__':

    global id_variable
    global server_address_details
    global p_server
    global s_clients
    global logger
    global server_id
    global message_queue
    global received_response_from_primary

    message_queue = deque()
    received_response_from_primary = False
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
        threading.Thread(target = create_rpc_server_for_client_requests, args = (server_id, server_address, int(server_port) + 1000 , )).start()
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


