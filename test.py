import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
G = nx.DiGraph()

def edge_cost(u, v, data, trx_amt):
    cost = (trx_amt * ((data.get("prop_fee", 0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) +  data.get("base_fee", 0) + data.get("bias", 1)
    return cost
    
def init(amt=0):
    global G
    G=nx.DiGraph()
    with open("now.json", encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    base_fee=1000
    prop_fee=500
    timelock=50
    rf=1e-9
    bias=1
    for edge in data["edges"]:
        if int(edge["capacity"])>=amt:
            if edge["node1_policy"] == None:
                G.add_edge(edge["node1_pub"], edge["node2_pub"],capacity=int(edge["capacity"]),
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node1_policy"]["disabled"] == True:
                    G.add_edge(edge["node1_pub"], edge["node2_pub"], capacity=int(edge["capacity"]),
                                                                            base_fee=int(edge["node1_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node1_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node1_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
            if edge["node2_policy"] == None:
                G.add_edge(edge["node2_pub"], edge["node1_pub"],capacity=int(edge["capacity"]),
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node2_policy"]["disabled"] == True:
                    G.add_edge(edge["node2_pub"], edge["node1_pub"], capacity=int(edge["capacity"]),
                                                                            base_fee=int(edge["node2_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node2_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node2_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
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
                    s += 1

    # Finding the most probable Source & Destination
    src = max(l_src, key=l_src.get, default=None)
    d = max(l_dest, key=l_dest.get, default=None)

    if s > 0:
        for i in l_src:
            f.write(f"Probability of Source {i}: {l_src[i] / s} \n")
        for i in l_dest:
            f.write(f"Probability of Destination {i}: {l_dest[i] / s} \n")

    f.write(f"\nMost Probable Source: {src}, Most Probable Destination: {d} \n")

    # Entropy Analysis
    f.write("\nEntropy Analysis\n")
    H = 0
    s = sum(l_src.values())

    if s > 0:
        for i in l_src:
            P_A_Bi = l_src[i] / s
            H += P_A_Bi * math.log2(P_A_Bi)        
        f.write(f"\nEntropy: { -H}\n")
    return -H

def test(trx_amt=10):
    init(trx_amt)
    with open("output5.txt","+a") as f:
        d={3:[0,0,0],5:[0,0,0],10:[0,0,0]}
        for k in range(0,3):
            f.write(f"For 5 nodes (TEST {k+1}) \n")
            d[3][1]=0
            d[5][1]=0
            d[10][1]=0
            for j in d.keys():
                for i in G.nodes():
                    src = random.choice(list(G.nodes()))
                    try:
                        l=nx.shortest_path(G,source=src,target=i,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                    except:
                        continue
                    if l==[]:
                        continue
                    if len(l)==j:
                        if d[j][1]==10:
                            d[j][2]+=1
                            break
                        m=random.choice(l[1:-1])
                        ind=l.index(m)
                        H=find_source_dest_pair(l[ind-1],m,l[ind+1],trx_amt,f)
                        d[j][0]+=H
                        d[j][1]+=1
                    else:
                        continue
                    f.write(f"\n{str(d)} \n")
                    print(d)

if __name__ == "__main__":
    for i in range(10,1000,100000):
        test(i)

