import csv
import os
import json
import pickle
import networkx as nx

def edge_cost(u, v, data, trx_amt):
    cost = (trx_amt * ((data.get("prop_fee", 0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) + data.get("base_fee", 0) + data.get("bias", 1)
    return cost

def prob_after(filename,a,b):
    with open("final_results/"+filename, 'r') as f:
        data = json.load(f)

    sources = data['src_nodes']
    dest = data['dst_nodes']
    trx_amt = float(data['amount'])
    l_src={}
    l_dest={}
    
    graph="Graphs/graph_"+a+"_"+b+".pkl"
    with open(graph, "rb") as f:
        G = pickle.load(f)
    data="test/"+a+"_"+b+"/misc.json"
    with open(data, "r") as jfile:
        misc = json.load(jfile)
    prev = misc['n-1']
    n = misc['attacker']
    nxt = misc['n+1']
    print(data)
    print(trx_amt)
    s=0
    for i in sources:
        for j in dest:
            if nx.has_path(G, i, j):
                sp = nx.shortest_path(G, source=i, target=j, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if [prev, n, nxt] in [sp[k:k+3] for k in range(len(sp)-2)]:
                    l_src[i] = l_src.get(i, 0) + 1
                    l_dest[j] = l_dest.get(j, 0) + 1
                    s += 1
    src = max(l_src, key=l_src.get, default=None)
    d = max(l_dest, key=l_dest.get, default=None)
    s1 = 0
    d1 = 0
    u = 1
    v = 1
    csv_filename = f"final_results/probabilities_{filename}.csv"
    # Writing to CSV
    with open(csv_filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Type', 'Node', 'Probability'])

        if s > 0:
            for i in l_src:
                prob = l_src[i] / s
                writer.writerow(['Source', i, prob])
                f.write(f"Probability of Source {i}: {prob}\n")
                u += 1
                s1 += prob

            for i in l_dest:
                prob = l_dest[i] / s
                writer.writerow(['Destination', i, prob])
                f.write(f"Probability of Destination {i}: {prob}\n")
                v += 1
                d1 += prob

        # Write most probable and averages
        f.write(f"\nMost Probable Source: {src}, Most Probable Destination: {d}\n")
        f.write(f"\nAverage probability of source: {s1/u}\nAverage probability of destination: {d1/v}\n")

        writer.writerow([])
        writer.writerow(['Summary', '', ''])
        writer.writerow(['Most Probable Source', src, ''])
        writer.writerow(['Most Probable Destination', d, ''])
        writer.writerow(['Average Source Probability', '', s1/u])
        writer.writerow(['Average Destination Probability', '', d1/v])

for i in ["Normal", "Bimodal", "Uniform_Normal"]:
    for j in ["10", "100", "1000", "10000"]:
        f_name = f"src_dst_nodes_{i}_{j}_"  # remove the leading slash
        matching_files = [f for f in os.listdir("./final_results") if f.startswith(f_name)]
        for k in matching_files:
            prob_after(k,i,j)
