import os
import pickle
import networkx as nx
from initial_prob import find_initial_probability  # make sure this is importable

csv_list_file = "csv_with_1.0.txt"
graph_folder = "filtered_graphs"
output_folder = "initial_probability"

with open(csv_list_file, "r") as f:
    csv_paths = [line.strip() for line in f.readlines() if line.strip()]

for csv_path in csv_paths:
    # Extract base name like: g10_merge_filtered_1000
    csv_file = os.path.basename(csv_path)
    base_name = csv_file.replace(".csv", "")
    
    # Match back to .pkl file
    pkl_file = base_name + ".pkl"
    pkl_path = os.path.join(graph_folder, pkl_file)

    if not os.path.exists(pkl_path):
        print(f"⚠️ Skipping {base_name} (no matching .pkl file found)")
        continue

    try:
        threshold = int(base_name.split("_filtered_")[-1])
    except ValueError:
        print(f"⚠️ Skipping {base_name} (threshold not found in filename)")
        continue

    with open(pkl_path, "rb") as f:
        G = pickle.load(f)

    print(f"🔁 Re-running for: {base_name}")
    find_initial_probability(G, pkl_file, threshold, os.path.join(output_folder, base_name))

print("✅ Re-run completed.")
