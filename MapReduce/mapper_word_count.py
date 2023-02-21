
import os
import sys
import json
import fcntl
import xmlrpc.client
from time import sleep



def get_reducer_id(str_input, no_of_reducers):
    hash_value = 0
    for char in str_input:
        hash_value = (hash_value * 31 + ord(char)) % int(no_of_reducers)
    return str(hash_value + 1)


def mapper():
    mapper_id = sys.argv[1]
    database_server = sys.argv[2]
    database_port = sys.argv[3]
    master_address = sys.argv[4]
    master_port = sys.argv[5]
    no_of_reducers = sys.argv[6]

    # print(f"I'm mapper {mapper_id} in a seperate file, my parent process is {os.getppid()} and process id is {os.getpid()}")
    # print("###############################")
    try:
        m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')
    except Exception as e:
        print("Exception occurred in connecting from mapper to master server: ", e)
        m_server.mapper_report_status(mapper_id, "FAILED")
        return

    f = open("mappers.txt", 'r')
    words = json.loads(f.read())[f"mapper {mapper_id}"]
    f.close()

    mapper_output = {}
    for word in words:
        reducer_id = get_reducer_id(word, no_of_reducers)
        if reducer_id not in mapper_output:
            mapper_output[reducer_id] = []
        mapper_output[reducer_id].append((word,1))

    try:
        db_server = xmlrpc.client.ServerProxy(f'http://{database_server}:{database_port}/')
        result = db_server.set_mapper_output(mapper_output)
    except Exception as e:
        print("Exception occurred in connecting from mapper to db server: ", e)
        m_server.mapper_report_status(mapper_id, "FAILED")
        return

    m_server.mapper_report_status(mapper_id, "DONE")

    # Not able to find any method that will close this client connection
    # db_server.close()
    # m_server.close()

if __name__ == "__main__":
    mapper()





