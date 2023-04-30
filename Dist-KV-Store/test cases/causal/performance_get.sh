#!/bin/sh

cd ../..
python3 client_causal_set.py localhost
sleep 3

i=1
max=100
START=$(date +%s.%N)
while [ $i -lt $max ]
do
    python3 client_causal_get.py localhost
    true $(( i++ ))
done
END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF