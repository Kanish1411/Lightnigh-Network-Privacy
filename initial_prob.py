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

import csv

def find_source_dest_pair(prev, n, nxt, trx_amt, f, csv_filename="probabilities.csv"):
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
    s1 = 0
    d1 = 0
    u = 1
    v = 1

    # Writing to CSV
    with open(csv_filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
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

    

def find_initial_probability(G,a,trx_amt,op,c):
    global unused_path
    with open(op+"/paths"+str(trx_amt)+".txt", "a+") as f:
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
        with open("Data.csv", mode='a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source', 'Destination', 'Attacker',"Graph"])
                writer.writerow([src1,dest,att,a]) 
        find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt,f,c)


for i in ["Normal","Uniform_Normal"]:
    os.mkdir(i)
    for j in ["0","10","100","1000","10000"]:
        a="graph_"+i+"_"+j+".pkl"
        with open("Graphs/" + a, "rb") as f:
                 G = pickle.load(f)
        find_initial_probability(G,a,int(j),i,i+"_"+j)
