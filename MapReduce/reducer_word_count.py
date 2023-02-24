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
            if reducer_progress == 100:
                sleep(5)
            return reducer_progress
        server.register_function(get_reducer_progress, "get_reducer_progress")

        def stop_reducer_server():
            # print(f"Reducer PID to kill: {os.getpid()}")
            os.kill(os.getpid(), signal.SIGKILL)
        server.register_function(stop_reducer_server, "stop_reducer_server")
        server.serve_forever()


def reducer():
    global reducer_progress

    reducer_progress = 0
    reducer_id = sys.argv[1]
    master_address = sys.argv[2]
    master_port = sys.argv[3]
    reducer_address = sys.argv[4]
    reducer_port = sys.argv[5]

    try:
        threading.Thread(target = create_reducer_rpc_server, args = (reducer_address, reducer_port, )).start()
        sleep(3)
        m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')

        # if random.randint(1,5) == 2:
        #     raise Exception("For testing the Fault Tolerence")

        reducer_input = m_server.get_reducer_input(reducer_id)
        l = len(reducer_input)
        reducer_output = {}
        for i, pair in enumerate(reducer_input):
            reducer_progress = ((i + 1) / l) * 100
            reducer_output[pair[0]] = reducer_output.get(pair[0], 0) + 1
        
        m_server.set_reducer_output(reducer_output)
    
        print(f"Reducer {reducer_id} End")
    except Exception as e:
         os.kill(os.getpid(), signal.SIGKILL)
    

if __name__ == "__main__":
    reducer()