import os
import json
import pickle
import networkx as nx
from cost_functions import *

amounts = [ "10000"]
graph_types = ["Normal", "Uniform_Normal", "Bimodal"]

all_results = {amt: {gt: [] for gt in graph_types} for amt in amounts}
length_stats = {amt: {gt: {} for gt in graph_types} for amt in amounts}

for i in graph_types:
    for j in amounts:
        G_path = f"Graphs/graph_{i}_{j}.pkl"

        try:
            with open(G_path, "rb") as f:
                G = pickle.load(f)
        except FileNotFoundError:
            continue

        folder = f"test/{i}_{j}"
        try:
            with open(folder + "/data.json", "r") as jfile:
                data = json.load(jfile)
            with open(folder + "/src.json", "r") as jfile:
                src = json.load(jfile)
            with open(folder + "/misc.json", "r") as jfile:
                misc = json.load(jfile)
        except Exception as e:
            print("An error occurred:", e)
            continue

        amt_prob = {}
        nodes = {}
        for amt_val in data:
            if amt_val == "actuual destination":
                continue
            p, x = 0, 0
            nodes[amt_val] = []
            for s in src:
                for d in data[amt_val]:
                    try:
                        path = nx.shortest_path(G, source=s, target=d, weight=lambda u, v, da: edge_cost(u, v, da, float(amt_val)))
                    except:
                        continue
                    if path != []:
                        if [misc['n-1'], misc["attacker"], misc["n+1"]] in [path[k:k+3] for k in range(len(path)-2)]:
                            if round(calculate_fee_at_node(path, float(amt_val), G, misc["attacker"]), 4) == round(misc["amt"], 4):
                                p += 1
                                nodes[amt_val].append([s, d])
                        x += 1
            amt_prob[amt_val] = p / x if x != 0 else 0

        # Store top 3 probabilities
        top3 = sorted(amt_prob.items(), key=lambda x: x[1], reverse=True)[:3]
        all_results[j][i] = top3
        print(all_results)

        # --- Source/Destination Set Length Analysis ---
        amt_sorted = sorted(amt_prob.items(), key=lambda x: x[1])
        amt_rev = amt_sorted[-5:][::-1]
        for k in amt_rev:
            if k[1] != 0.0:
                s = {}
                d = {}
                for pair in nodes[k[0]]:
                    if pair[0] not in s:
                        s[pair[0]] = 1
                    else:
                        s[pair[0]] += 1
                    if pair[1] not in d:
                        d[pair[1]] = 1
                    else:
                        d[pair[1]] += 1

                src_after_len = len(sorted(s.items(), key=lambda x: x[1])[::-1])
                dst_after_len = len(sorted(d.items(), key=lambda x: x[1])[::-1])

                print("source set length (After) ", src_after_len)
                print("Destination set length (After) ", dst_after_len)
                print("___")
                os.makedirs("final_results", exist_ok=True)
                filename = f"final_results/src_dst_nodes_{i}_{j}_{k[0]}.json"

                # Extract only the keys (node addresses)
                result_data = {
                    "amount": k[0],
                    "probability": k[1],
                    "src_nodes": list(s.keys()),
                    "dst_nodes": list(d.keys())
                }
                with open(filename, "w") as outfile:
                    json.dump(result_data, outfile, indent=4)
                # Store in length_stats for LaTeX table
                length_stats[j][i] = {
                    "src_after": src_after_len,
                    "dst_after": dst_after_len
                }


# ------------------ CSV Export ---------------------

# --- Create output directory ---
os.makedirs("final_results_csv", exist_ok=True)

# ------------------ CSV 1: Top 3 Probabilities ---------------------
prob_csv_path = "final_results_csv/top3_probabilities.csv"
with open(prob_csv_path, mode="w", newline='') as file:
    writer = csv.writer(file)
    header = ["Amount", "Graph Type", "Rank", "Top Amount", "Probability"]
    writer.writerow(header)
    for amt in amounts:
        for gt in graph_types:
            top3 = all_results[amt][gt]
            for rank, (a, p) in enumerate(top3, start=1):
                writer.writerow([amt, gt, rank, a, f"{p:.4f}"])
print(f"Top 3 probabilities saved to '{prob_csv_path}'")

# ------------------ CSV 2: Source/Destination Set Lengths ---------------------
length_csv_path = "final_results_csv/src_dst_lengths.csv"
with open(length_csv_path, mode="w", newline='') as file:
    writer = csv.writer(file)
    header = ["Amount", "Graph Type", "Source Set Length", "Destination Set Length"]
    writer.writerow(header)
    for amt in amounts:
        for gt in graph_types:
            if length_stats[amt][gt]:
                stats = length_stats[amt][gt]
                writer.writerow([amt, gt, stats['src_after'], stats['dst_after']])
            else:
                writer.writerow([amt, gt, "-", "-"])
print(f"Source/Destination set lengths saved to '{length_csv_path}'")
