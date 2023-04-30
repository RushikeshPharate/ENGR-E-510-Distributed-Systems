#!/bin/sh

# Sequential Consistency
cd ../..
python3 client.py localhost 6486 SET x 7 
sleep 1
python3 client.py localhost 6487 GET x & python3 client.py localhost 6486 SET x 3 & python3 client.py localhost 6487 SET r 5 


