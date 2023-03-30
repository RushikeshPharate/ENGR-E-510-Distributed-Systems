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

    data = json.load(open('config.json'))

    global server_address_details

    master_address = data["MASTER_ADDRESS"]
    master_port = int(data["MASTER_PORT"])
    no_of_servers = int(data["NO_OF_SERVERS"])
    port_start_range = 5485


    server_address = "0.0.0.0"
    server_address_details = {}
    server_port = port_start_range
    for i in range(1, no_of_servers + 1):
        server_address_details[str(i)] = [server_address, server_port]
        server_port += 1

    logger = setup_custom_logger("distributed-sequencer")
    logger.info(f"Master Node started on {master_address}:{master_port}")
    logger.info(f"Starting {no_of_servers} servers")

    threading.Thread(target = create_master_rpc_server, args = (master_address, master_port, )).start()
    sleep(2)

    server_details = {}
   
    for i in range(1, no_of_servers + 1):
        server = Process(target=handle_server, args=(i, server_address_details[str(i)][0], server_address_details[str(i)][1], server_address_details["1"][0], server_address_details["1"][1], master_address, master_port))
        server.start()
        server_details = {}
        server_details[i] = server
        logger.info(f"Started server {i} on {server_address_details[str(i)][0]}:{server_address_details[str(i)][1]}")
        # sleep(1)

    # print("Server Details: ", server_details)



    # logger.info("Finished Task. Terminating")
    # os.kill(os.getpid(), signal.SIGKILL)
    
# approaches

# 1) Total order multicast
# 2) Leader election
# 3) Primary server --> Will have to maintain a queue for incoming messages??
# 4) Consensus based algorithms (Paxos) 

# Primary Server --> Do we have to consider system failures?? like primary/other server dies???
# how can a client request for an id on any server????? Based on a port??
# Will primary server be always fixed?? is it similar to leader election??
# All the requests are redirected to primary server, won't this create an bottleneck??


# In case of broadcasting message, if 2nd client contacts when the system is in blocking status, then it will create problems. Prof said this was okay in sequencial consistancy ???????


# primary server will maintain a queue for incoming requests from other servers --> This can be done by invoking an RPC call on primary server.



# if a server receives get_id() request, it sends it to primary
# primary sends msg's to all the other servers on with updated id
# all other servers update their id and send ack to primary
# after receving all the ack, primary sends new id to the server from which it received msg.
# the initial server sends new id to the client