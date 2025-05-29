import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
G = nx.DiGraph()

def edge_cost(u, v, data, trx_amt):
    return ((trx_amt * ((data.get("prop_fee", 0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) +  data.get("base_fee", 0) + data.get("bias", 1))
    

def find_source_dest_pair(prev, n, nxt,trx_amt, f):
    sources=[]
    dest=[]
    # Source identification
    paths = nx.shortest_path(G, target=nxt,weight=lambda u, v, d: edge_cost(u, v,d,trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            sources.append(i[0])

    # Destination finding
    paths = nx.single_source_dijkstra_path(G, source=prev,weight=lambda u, v, d: edge_cost(u, v,d,trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            dest.append(i[-1])
    l_src = {}

    # Compute Source & Destination probabilities
    for i in sources:
        for j in dest:
            if nx.has_path(G, i, j):
                sp = nx.shortest_path(G, source=i, target=j,weight=lambda u, v, d: edge_cost(u, v,d,trx_amt))
                if [prev, n, nxt] in [sp[k:k+3] for k in range(len(sp)-2)]:
                    l_src[i] = l_src.get(i, 0) + 1

    # Entropy Analysis
    
    H = 0
    s=sum(l_src.values())
    for i in l_src:
        if s > 0:
            P_A_Bi = l_src[i] / s
            H += P_A_Bi * math.log2(P_A_Bi)
        f.write(f"Entropy: { -H}\n")
    return -H

def test(G,trx_amt=10):
    d={0:[0,0]}
    for j in d.keys():
            with open(f"output{j}.txt","+a") as f:
                f.write(f"for trx_amt = {trx_amt} \n\n")
                print(f"for trx_amt = {trx_amt}")
                f.write(f"For {j} nodes \n") 
                for i in G.nodes():
                    src = random.choice(list(G.nodes()))
                    try:
                        l=nx.shortest_path(G,source=src,target=i,weight=lambda u, v, d: edge_cost(u, v,d,trx_amt))
                    except:
                        continue
                    if l==[]:
                        continue
                    if d[j][1]==int(len(G.nodes())*0.01):
                        f.write(f"{str(d)} \n")
                        d[j][0]=0
                        d[j][1]=0
                        break
                    m=random.choice(l[1:-1])
                    ind=l.index(m)
                    H=find_source_dest_pair(l[ind-1],m,l[ind+1],trx_amt,f)
                    d[j][0]+=H
                    d[j][1]+=1
                    f.write(f"{str(d)}\n")
                    print(d)

if __name__ == "__main__":
    for i in [1000,10000]:
        test(i)
