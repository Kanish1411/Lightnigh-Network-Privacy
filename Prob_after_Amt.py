import os
import json
import pickle
import networkx as nx

def prob_after(filename,a,b):
    with open("final_results/"+filename, 'r') as f:
        data = json.load(f)

    sources = data['src_nodes']
    dest = data['dst_nodes']
    trx_amt = float(data['amount'])
    l_src={}
    l_dest={}
    

    print(trx_amt)
    for i in sources:
        for j in dest:
            if nx.has_path(G, i, j):
                sp = nx.shortest_path(G, source=i, target=j, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if [prev, n, nxt] in [sp[k:k+3] for k in range(len(sp)-2)]:
                    l_src[i] = l_src.get(i, 0) + 1
                    l_dest[j] = l_dest.get(j, 0) + 1
                    s += 1


for i in ["Normal", "Bimodal", "Uniform_Normal"]:
    for j in ["10", "100", "1000", "10000"]:
        f_name = f"src_dst_nodes_{i}_{j}_"  # remove the leading slash
        matching_files = [f for f in os.listdir("./final_results") if f.startswith(f_name)]
        for k in matching_files:
            prob_after(k,i,j)
