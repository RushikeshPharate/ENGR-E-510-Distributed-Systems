import os
import threading
from socketserver import ThreadingMixIn

import sys
import json
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCServer
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

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='[%(asctime)s.%(msecs)03d] [%(levelname)-5s] %(message)s',
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


def update_id(var, val, s_id, action, logical_clock):
    global logger
    global received_response_from_primary_set
    global server_id
    global version_clock

    with open(f"./store/{str(server_id)}.txt", "r") as f:
        data = json.loads(f.read())
        f.close()
    with open(f"./store/{str(server_id)}.txt", "w") as f:
        data[var] = val
        f.write(json.dumps(data, ensure_ascii=False))
        f.close()
    logger.info(f"{action}({var}, {val}) finished on server {server_id}")

    if var not in version_clock:
        version_clock[var] = 0
    te = version_clock[var]
    version_clock[var] = logical_clock
    logger.info(f"Updated logical clock value from {te} to {logical_clock} for variable {var} on server {server_id}")

    sleep(1)
    if int(s_id) == int(server_id):
        received_response_from_primary_set = True
    

def process_message(s_id,  action, var, val):
    global s_clients
    global logger
    global version_clock

    lock.acquire()
    num = version_clock.get(var, 0) + 1

    logger.info(f"Primary server starting an broadcast for {action}({var}, {val if action == 'SET' else ''})")

    update_id(var, val, str(s_id), action, num)
    if str(s_id) != "1":
        s_clients[str(s_id)].update_id(var, val, str(s_id), action, num)
    for s in s_clients:
        if s == str(s_id):
            continue
        s_clients[s].update_id(var, val, str(s_id), action, num)
    
    sleep(1)
    lock.release()


def insert_into_queue(s_id, action, var, val):
    global logger

    logger.info(f"Primary server received an {action}({var}, {val if action == 'SET' else ''}) message from server {s_id}")
    
    th = threading.Thread(target = process_message, args = (s_id, action, var, val))
    th.daemon = True
    th.start()
    th.join()


def send_to_primary(action, var, val=-1):
    global p_server
    
    if server_id != 1:
        p = xmlrpc.client.ServerProxy(f'http://{primary_server_address}:{primary_server_port}/')
        p.insert_into_queue(server_id, action, var, val)
    else:
        insert_into_queue(server_id, action, var, val)


def get_var(var, clock_counter):
    global logger
    global server_id
    global version_clock

    logger.info(f"Server {server_id} received GET({var}) request with logical clock value {clock_counter}")
    if var not in version_clock:
        version_clock[var] = 0
    logger.info(f"Current logical clock value for variable {var} on server {server_id} is {version_clock[var]}")

    temp = True
    while clock_counter > version_clock[var]:
        if temp:
            logger.info(f"Waiting for server {server_id}'s logical clock: {version_clock[var]} to catch up to clients logical clock: {clock_counter} for variable {var}")
            logger.info(f"Blocking execution of GET({var}) request")
            temp = False
        sleep(0.2)

    if not temp:
        logger.info(f"Finally catched up..... Server {server_id}'s logical clock: {version_clock[var]}, Get requests logical clock: {clock_counter} for variable {var}")

    with open(f"./store/{str(server_id)}.txt") as f:
        data = json.loads(f.read())
        if var in data:
            r = data[var]
        else:
            r = None
        f.close()
    logger.info(f"GET({var}) = {r} operation ends on server {server_id} with logical clock value {version_clock[var]}")
    return r, version_clock[var]


def set_var(var, val, clock_counter):
    global server_id
    global logger
    global received_response_from_primary_set
    global version_clock

    logger.info(f"Server {server_id} received SET({var}, {val}) request with logical clock value {clock_counter}")
    if var not in version_clock:
        version_clock[var] = 0
    logger.info(f"Current logical clock value for variable {var} on server {server_id} is {version_clock[var]}")

    th = threading.Thread(target = send_to_primary, args = ("SET",var, val,))
    th.daemon = True
    th.start()
    
    while True:
        sleep(0.2)
        if received_response_from_primary_set:
            received_response_from_primary_set = False
            logger.info(f"SET({var}, {val}) operation ends on server {server_id} with logical clock value {version_clock[var]}")
            return version_clock[var]



def create_rpc_server(server_id, server_address, server_port):
    server_addr = (server_address, server_port)
    server = SimpleThreadedXMLRPCServer(server_addr, logRequests=False,allow_none=True)
    server.register_function(update_id, 'update_id')
    if server_id == 1:
        server.register_function(insert_into_queue, "insert_into_queue")
    server.serve_forever()


def create_rpc_server_for_client_requests(server_id, server_address, server_port):
    global logger

    logger.info(f"SERVER {server_id} CAN HANDLE CLIENT REQUESTS ON {server_address}:{server_port}")
    
    server_addr = (server_address, server_port)
    server = SimpleThreadedXMLRPCServer(server_addr, logRequests=False,allow_none=True)
    server.register_function(set_var, 'set_var')
    server.register_function(get_var, 'get_var')
    server.serve_forever()


if __name__ == '__main__':

    global s_clients
    global logger
    global server_id
    global received_response_from_primary_set
    global version_clock

    version_clock = {}

    received_response_from_primary_set = False

    server_id = int(sys.argv[1])
    server_address = sys.argv[2]
    server_port = sys.argv[3]
    primary_server_address = sys.argv[4]
    primary_server_port = sys.argv[5]
    master_address = sys.argv[6]
    master_port = sys.argv[7]

    f = open(f"./store/{str(server_id)}.txt", "w")
    f.write(json.dumps({}))
    f.close()

    logger = setup_custom_logger("distributed-sequencer")

    # get other server details from the master
    if server_id == 1:
        logger.info(f"Server {server_id} is the primary server")
        master = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
        server_address_details = master.get_all_server_details()
        
        logger.info(f"Primary server got details of all other servers")
    try:
        threading.Thread(target = create_rpc_server, args = (server_id, server_address, int(server_port), )).start()
        sleep(2)
        threading.Thread(target = create_rpc_server_for_client_requests, args = (server_id, server_address, int(server_port) + 1000 , )).start()
        sleep(2)

        if server_id == 1:
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


