import os
import sys
import json
import xmlrpc.client
import xmlrpc.server
from time import sleep
import threading
import signal
import random

def create_reducer_rpc_server(reducer_address, reducer_port):
    with xmlrpc.server.SimpleXMLRPCServer((reducer_address, int(reducer_port)),logRequests=False,allow_none=True) as server:
        def get_reducer_progress():
            return reducer_progress
        server.register_function(get_reducer_progress, "get_reducer_progress")

        def stop_reducer_server():
            server.shutdown()
            return True
        server.register_function(stop_reducer_server, "stop_reducer_server")
        server.serve_forever()


def reducer():
    global reducer_progress

    reducer_progress = 0
    reducer_id = sys.argv[1]
    database_server = sys.argv[2]
    database_port = sys.argv[3]
    master_address = sys.argv[4]
    master_port = sys.argv[5]
    reducer_address = sys.argv[6]
    reducer_port = sys.argv[7]

    try:
        threading.Thread(target = create_reducer_rpc_server, args = (reducer_address, reducer_port, )).start()

        m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
    
        db_server = xmlrpc.client.ServerProxy(f'http://{database_server}:{database_port}/')
        
        if random.randint(1,5) == 2:
            raise Exception("For testing the Fault Tolerence")

        reducer_input = db_server.get_reducer_input(reducer_id)
        l = len(reducer_input)
        reducer_output = {}
        for i, pair in enumerate(reducer_input):
            reducer_progress = ((i + 1) / l) * 100
            reducer_output[pair[0]] = reducer_output.get(pair[0], 0) + 1
        db_server.set_reducer_output(reducer_output)
        # print(f"Reducer {reducer_id} End")
    except Exception as e:
         os.kill(os.getpid(), signal.SIGKILL)
    

if __name__ == "__main__":
    reducer()