#!/bin/sh

# Linearizability
cd ../..
python3 client.py localhost 6486 SET x 7 
sleep 1
python3 client.py localhost 6486 SET x 1
python3 client.py localhost 6487 GET x & python3 client.py localhost 6486 SET x 3

