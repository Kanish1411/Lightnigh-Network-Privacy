import random
import networkx as nx
import matplotlib.pyplot as plt
from init import *
import os
 
def edge_cost(u, v, data, trx_amt):
    cost = (trx_amt * ((data.get("prop_fee", 0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) +  data.get("base_fee", 0) + data.get("bias", 1)
    return cost

def calculate_total_fee(path, trx_amt, G):
    """
    Computes the total fee for the transaction by working backwards from the destination.
    """
    total_fee = 0
    amt_needed = trx_amt

    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1] 

        edge_data = G[u][v]
        base_fee = edge_data.get("base_fee", 0)
        prop_fee = amt_needed * ((edge_data.get("prop_fee", 0) / 1e6)+(edge_data.get("timelock", 0) * edge_data.get("rf", 1e-9)))

        hop_fee = base_fee + prop_fee + edge_data.get("bias", 1)
        total_fee += hop_fee
        amt_needed += hop_fee  
        print(f"for hop {u} to {v} is {hop_fee} = {base_fee} {prop_fee}")
    return total_fee

sources=[]
dest=[]

def find_source_dest_pair(prev, n, nxt, trx_amt,f):
    global sources, dest

    # Source identification
    paths = nx.shortest_path(G, target=nxt, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            sources.append(i[0])

    # Destination finding
    paths = nx.single_source_dijkstra_path(G, prev, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            dest.append(i[-1])
    s = 0
    l_src = {}
    l_dest = {}

    # Compute Source & Destination probabilities
    for i in sources:
        for j in dest:
            if nx.has_path(G, i, j):
                sp = nx.shortest_path(G, source=i, target=j, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if [prev, n, nxt] in [sp[k:k+3] for k in range(len(sp)-2)]:
                    l_src[i] = l_src.get(i, 0) + 1
                    l_dest[j] = l_dest.get(j, 0) + 1
                    s+=1

    # Finding the most probable Source & Destination
    src = max(l_src, key=l_src.get, default=None)
    d = max(l_dest, key=l_dest.get, default=None)
    s1=0
    d1=0
    u=1
    v=1
    if s > 0:
        for i in l_src:
            f.write(f"Probability of Source {i}: {l_src[i] / s} \n")
            u+=1
            s1+=(l_src[i] / s)
        for i in l_dest:
            f.write(f"Probability of Destination {i}: {l_dest[i] / s} \n")
            v+=1
            d1+=(l_dest[i] / s)

    f.write(f"\nMost Probable Source: {src}, Most Probable Destination: {d} \n")
    f.write(f"\nAverage probability of source: {s1/u}\n Average probability of Dest:{d1/v}")
    

def find_initial_probability(G,op):
    global unused_path
    with open(op+"/paths.txt", "a+") as f:
        for trx_amt in [10,1000,10000]:
            G=init_normal(trx_amt)
            while(1):
                    src1 = random.choice(list(G.nodes()))
                    dest = random.choice(list(G.nodes()))
                    if src1!=dest:
                        try:
                            l=nx.shortest_path(G,source=src1,target=dest,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                            if len(l)>=3:
                                break
                        except:
                            pass
            att=random.choice(l[1:-1]) 
            ind=l.index(att)
            try:
                f.write("\n------------------------------------------------------for {trx_amt}")
                init_normal(trx_amt)
                unused_path=[]
                f.write(f"Shortest path for tx amount {trx_amt}: {l}\n")
            except nx.NetworkXNoPath:
                f.write(f"No path found for tx amount {trx_amt}\n")
                print(f"No path found for tx amount {trx_amt}")
            find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt,f)

G=nx.DiGraph()
G=init_normal()
os.mkdir("Normal_Case2")
find_initial_probability(G,"Normal_Case2")

G=nx.DiGraph()
G=init_unif_normal()
os.mkdir("Uniform_Case2")
find_initial_probability(G,"Uniform_Case2")

G=nx.DiGraph()
G=init_Bimodal()
os.mkdir("Bimodal_Case2")
find_initial_probability(G,"Bimodal_Case2")

