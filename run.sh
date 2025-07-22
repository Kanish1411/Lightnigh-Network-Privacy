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


# Run remaining scripts
python initial_prob.py || { echo "Failed: initial_prob.py"; 
                        read -p "Continue? (y/n): " choice; 
                          [ "$choice" != "y" ] && exit 1; }
python entropy_before.py || { echo "Failed: entropy_before.py"; 
                            read -p "Continue? (y/n): " choice; 
                              [ "$choice" != "y" ] && exit 1; }
python Transaction.py || { echo "Failed: Transaction.py"; 
                        read -p "Continue? (y/n): " choice; 
                        [ "$choice" != "y" ] && exit 1; }
python Trx_amt_analysis.py || { echo "Failed: Trx_amt_analysis.py"; 
                                read -p "Continue? (y/n): " choice; 
                                [ "$choice" != "y" ] && exit 1; }
python Prob_after_Amt.py || { echo "Failed: Prob_after_Amt.py"; 
                            read -p "Continue? (y/n): " choice; 
                            [ "$choice" != "y" ] && exit 1; }
python entropy_analysis.py || { echo "Failed: entropy_analysis.py"; 
                                read -p "Continue? (y/n): " choice; 
                                [ "$choice" != "y" ] && exit 1; }

echo "All steps completed."