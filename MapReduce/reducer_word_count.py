import os
import sys
import json
import fcntl
import xmlrpc.client
from time import sleep


def reducer():
    reducer_id = sys.argv[1]
    database_server = sys.argv[2]
    database_port = sys.argv[3]
    master_address = sys.argv[4]
    master_port = sys.argv[5]

    try:
        m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
    except Exception as e:
        print("Exception occurred in connecting from reducer to master server: ", e)
        m_server.reducer_report_status(reducer_id, "FAILED")
        return

    try:
        db_server = xmlrpc.client.ServerProxy(f'http://{database_server}:{database_port}/')
    except Exception as e:
        print("Exception occurred in connecting from reducer to db server: ", e)  
        m_server.reducer_report_status(reducer_id, "FAILED")
        return   
    
    reducer_input = db_server.get_reducer_input(reducer_id)
    reducer_output = {}
    for pair in reducer_input:
        reducer_output[pair[0]] = reducer_output.get(pair[0], 0) + 1
    db_server.set_reducer_output(reducer_output)
    
    m_server.reducer_report_status(reducer_id, "DONE")
    

if __name__ == "__main__":
    reducer()