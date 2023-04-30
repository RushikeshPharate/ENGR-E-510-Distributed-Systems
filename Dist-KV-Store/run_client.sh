#!/bin/sh

# Linearizability
python3 client.py localhost 6486 SET x 1
python3 client.py localhost 6487 GET x

# Sequential

# python3 client.py localhost 6486 SET x 1
# python3 client.py localhost 6487 GET x

# # Eventual

# python3 client.py localhost 6486 SET x 1
# python3 client.py localhost 6487 GET x

# # Causal

# python3 client_causal.py localhost
# python3 client_causal_set.py localhost
# python3 client_causal_get.py localhost


