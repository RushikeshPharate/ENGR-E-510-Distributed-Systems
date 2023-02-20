
import os
import sys
import json
import fcntl
import xmlrpc.client
from time import sleep


def mapper():
    mapper_id = sys.argv[1]
    database_server = sys.argv[2]
    database_port = sys.argv[3]
    master_address = sys.argv[4]
    master_port = sys.argv[5]

    # print(f"I'm mapper {mapper_id} in a seperate file, my parent process is {os.getppid()} and process id is {os.getpid()}")
    # print("###############################")
    m_server = xmlrpc.client.ServerProxy(f'http://{master_address}:{master_port}/')


    f = open("mappers.txt", 'r')
    words = json.loads(f.read())[f"mapper {mapper_id}"]
    f.close()

    mapper_output = []
    for word in words:
        mapper_output.append({word: 1})

    try:
        db_server = xmlrpc.client.ServerProxy(f'http://{database_server}:{database_port}/')
        result = db_server.set_mapper_output(mapper_output)
        # print(result)
    except Exception as e:
        print(e)
        m_server.mapper_error(mapper_id)

    res = m_server.mapper_finished(mapper_id)

    # Not able to find any method that will close this client connection
    # db_server.close()
    # m_server.close()


if __name__ == "__main__":
    mapper()





