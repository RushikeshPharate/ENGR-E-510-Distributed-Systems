from multiprocessing import Process
import xmlrpc.server
import xmlrpc.client
import os
import socket
import threading
import json
import sys
import logging
import signal

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

def handle_server(server_id, server_address, server_port, primary_server_address, primary_server_port, master_address, master_port):
    cmd = f"python3 server.py {server_id} {server_address} {server_port} {primary_server_address} {primary_server_port} {master_address} {master_port}"
    os.system(cmd)

def create_master_rpc_server(master_address, master_port):
    with xmlrpc.server.SimpleXMLRPCServer((master_address, int(master_port)), logRequests=False,allow_none=True) as server:
        def get_all_server_details():
            return server_address_details
        server.register_function(get_all_server_details, "get_all_server_details")    

        server.serve_forever()


if __name__ == '__main__':
    global server_address_details

    data = json.load(open('config.json'))

    master_address = data["MASTER_ADDRESS"]
    master_port = int(data["MASTER_PORT"])
    no_of_servers = int(data["NO_OF_SERVERS"])
    port_start_range = int(data["PORT_START_RANGE"])

    server_address = "0.0.0.0"
    server_address_details = {}
    server_port = port_start_range
    for i in range(1, no_of_servers + 1):
        server_address_details[str(i)] = [server_address, server_port]
        server_port += 1

    logger = setup_custom_logger("distributed-sequencer")
    logger.info(f"Controller Node started on {master_address}:{master_port}")
    logger.info(f"Starting {no_of_servers} servers")

    threading.Thread(target = create_master_rpc_server, args = (master_address, master_port, )).start()
    sleep(2)

    server_details = {}
   
    for i in range(1, no_of_servers + 1):
        server = Process(target=handle_server, args=(i, server_address_details[str(i)][0], server_address_details[str(i)][1], server_address_details["1"][0], server_address_details["1"][1], master_address, master_port))
        server.start()
        server_details = {}
        server_details[i] = server
