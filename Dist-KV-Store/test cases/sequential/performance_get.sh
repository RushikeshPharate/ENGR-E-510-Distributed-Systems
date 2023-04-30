#!/bin/sh

cd ../..
python3 client.py localhost 6486 SET x 2
sleep 3

i=1
max=100
START=$(date +%s.%N)
while [ $i -lt $max ]
do
    python3 client.py localhost 6486 GET x  
    true $(( i++ ))
done
END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF