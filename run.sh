#!/bin/bash

graph_file="$1"
netstats_file="${2:-Data/netstats.json}"

pip install -r req.txt

if [ -z "$graph_file" ]; then
    echo "No file provided. Using default 'input'.";
    exit 1;
fi
echo "sikdfops"
python init.py "$graph_file" "$netstats_file"
if [ $? -ne 0 ]; then
    echo "Error running init.py";
    exit 1;
fi
echo "Initialization complete. Output saved in 'Graphs' directory."


python initial_prob.py 

python entropy_before.py

python Transaction.py

python Trx_amt_analysis.py

python Prob_after_Amt.py

python entropy_analysis.py