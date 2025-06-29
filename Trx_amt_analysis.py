import os
import json
import pickle
import networkx as nx

def edge_cost(u, v, data, trx_amt):
    cost = (trx_amt * ((data.get("prop_fee", 0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) + data.get("base_fee", 0) + data.get("bias", 1)
    return cost

def calculate_fee_at_node(path, trx_amt, G, node):
    amt_needed = trx_amt
    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1]
        edge_data = G[u][v]
        base_fee = edge_data.get("base_fee", 0)
        prop_fee = amt_needed * ((edge_data.get("prop_fee", 0) / 1e6) + (edge_data.get("timelock", 0) * edge_data.get("rf", 1e-9)))
        hop_fee = base_fee + prop_fee + edge_data.get("bias", 0)
        amt_needed += hop_fee
        if u == node:
            return amt_needed
    return None

amounts = ["10", "100", "1000", "10000"]
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

                

# ------------------ LaTeX TABLE 1: Probability Table ---------------------
print(r"""\begin{table}[h!]
\centering
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\multirow{2}{*}{Amount} & \multicolumn{2}{c|}{Normal} & \multicolumn{2}{c|}{Uniform} & \multicolumn{2}{c|}{Bimodal} \\
\cline{2-7}
 & Amount & Probability & Amount & Probability & Amount & Probability  \\
\hline""")

for amt in amounts:
    for i in range(3):
        row = []
        if i == 0:
            row.append(r"\multirow{3}{*}{" + amt + "}")
        else:
            row.append("")

        for gt in ["Normal", "Uniform_Normal", "Bimodal"]:
            if i < len(all_results[amt][gt]):
                a, p = all_results[amt][gt][i]
                row.append(f"{a} & {p:.4f}")
            else:
                row.append("&")

        print(" & ".join(row) + r" \\")
    print(r"\hline")

print(r"""\end{tabular}
\caption{Top 3 Amounts by Maximum Probability for Each Graph Type}
\end{table}""")

# ------------------ LaTeX TABLE 2: Set Length Table ---------------------
print(r"""\begin{table}[h!]
\centering
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\multirow{2}{*}{Amount} & \multicolumn{2}{c|}{Normal} & \multicolumn{2}{c|}{Uniform} & \multicolumn{2}{c|}{Bimodal} \\
\cline{2-7}
 & Source & Destination &  Source & Destination & Source & Destination \\
\hline""")

for amt in amounts:
    row = [amt]
    for gt in graph_types:
        if length_stats[amt][gt]:
            stats = length_stats[amt][gt]
            row.append(str(stats['src_after']))
            row.append(str(stats['dst_after']))
        else:
            row.append("-")
            row.append("-")
    print(" & ".join(row) + r" \\")
print(r"\hline")

print(r"""\end{tabular}
\caption{Source and Destination Set Lengths After Node Frequency Filtering}
\end{table}""")