import random
import networkx as nx
import os
import csv
import pickle
from cost_functions import *


def find_source_dest_pair(prev, n, nxt, trx_amt, csv_filename="probabilities.csv"):
    sources = []
    dest = []

    # Source identification
    paths = nx.shortest_path(G, target=nxt, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j + 3] for j in range(len(i) - 2)]:
            sources.append(i[0])

    # Destination finding
    paths = nx.single_source_dijkstra_path(G, prev, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j + 3] for j in range(len(i) - 2)]:
            dest.append(i[-1])

    s = 0
    l_src = {}
    l_dest = {}

    # Compute Source & Destination probabilities
    for i in sources:
        for j in dest:
            if nx.has_path(G, i, j):
                sp = nx.shortest_path(G, source=i, target=j, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if [prev, n, nxt] in [sp[k:k + 3] for k in range(len(sp) - 2)]:
                    l_src[i] = l_src.get(i, 0) + 1
                    l_dest[j] = l_dest.get(j, 0) + 1
                    s += 1

    if s == 0:
        print(f"⚠️ Skipping {csv_filename} (no valid source-destination probabilities found)")
        return False

    src = max(l_src, key=l_src.get, default=None)
    d = max(l_dest, key=l_dest.get, default=None)
    s1 = 0
    d1 = 0
    u = 0
    v = 0

    with open(csv_filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Node', 'Probability'])

        for i in l_src:
            prob = l_src[i] / s
            writer.writerow(['Source', i, prob])
            s1 += prob
            u += 1

        for i in l_dest:
            prob = l_dest[i] / s
            writer.writerow(['Destination', i, prob])
            d1 += prob
            v += 1

        avg_src = s1 / u if u != 0 else 0
        avg_dest = d1 / v if v != 0 else 0

        writer.writerow([])
        writer.writerow(['Summary', '', ''])
        writer.writerow(['Most Probable Source', src, ''])
        writer.writerow(['Most Probable Destination', d, ''])
        writer.writerow(['Average Source Probability', '', avg_src])
        writer.writerow(['Average Destination Probability', '', avg_dest])

    # If either average is 1.0, return False (indicates need to retry)
    if avg_src == 1.0 or avg_dest == 1.0:
        print(f"⚠️ Discarding {csv_filename} due to average probability of 1.0 (SRC: {avg_src}, DEST: {avg_dest})")
        return False

    return True

    
def find_initial_probability(G, a, trx_amt, c, max_attempts=100):
    for _ in range(max_attempts):
        src1 = random.choice(list(G.nodes()))
        dest1 = random.choice(list(G.nodes()))
        if src1 != dest1:
            try:
                path = nx.shortest_path(G, source=src1, target=dest1, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if len(path) >= 3:
                    att = random.choice(path[1:-1])
                    ind = path.index(att)

                    temp_csv = c + "_temp.csv"
                    result = find_source_dest_pair(path[ind-1], att, path[ind+1], trx_amt, temp_csv)

                    # If result is False, retry
                    if not result:
                        if os.path.exists(temp_csv):
                            os.remove(temp_csv)
                        continue

                    # ✅ Write final info to Data.csv
                    with open("Data.csv", mode='a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Source', 'Destination', 'Attacker', "Graph"])
                        writer.writerow([src1, dest1, att, a])

                    os.rename(temp_csv, c + ".csv")
                    return  # ✅ Done

            except Exception as e:
                continue

    print(f"⚠️ Skipping {c} (no valid probabilities found after {max_attempts} attempts)")


if not os.path.exists("initial_probability"):
    os.mkdir("initial_probability")

    # Iterate over all files in filtered_graphs directory
    for file in os.listdir("filtered_graphs"):
        if file.endswith(".pkl") and file.startswith("g10_"):
            G=nx.DiGraph()
            file_path = os.path.join("filtered_graphs", file)

            # Extract threshold from filename (part after "_filtered_")
            try:
                threshold = int(file.split("_filtered_")[-1].split(".")[0])
            except ValueError:
                print(f"Skipping file {file}: Could not extract threshold.")
                continue

            # Load the graph
            with open(file_path, "rb") as f:
                G = pickle.load(f)

            # Output folder inside initial_probability
            output_folder = os.path.join("initial_probability", file.replace(".pkl", ""))

            # Call the function
            find_initial_probability(G, file, threshold, output_folder)

else:
    print(f"Folder 'initial_probability' already exists. Skipping execution.")

