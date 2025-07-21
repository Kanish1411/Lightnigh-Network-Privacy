import random
import networkx as nx
import matplotlib.pyplot as plt
from init import *
import os
import csv
import csv

sources=[]
dest=[]

def find_source_dest_pair(prev, n, nxt, trx_amt, csv_filename="probabilities.csv"):
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
                u += 1
                s1 += prob

            for i in l_dest:
                prob = l_dest[i] / s
                writer.writerow(['Destination', i, prob])
                v += 1
                d1 += prob

        # Write most probable and averages

        writer.writerow([])
        writer.writerow(['Summary', '', ''])
        writer.writerow(['Most Probable Source', src, ''])
        writer.writerow(['Most Probable Destination', d, ''])
        writer.writerow(['Average Source Probability', '', s1/u])
        writer.writerow(['Average Destination Probability', '', d1/v])

    
def find_initial_probability(G,a,trx_amt,c):
        global unused_path
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
        find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt,c)


if not os.path.exists("initial_probability"):
    os.mkdir("initial_probability")
    for i in ["Normal","Uniform_Normal","Bimodal"]:
        for j in ["10","100","1000","10000"]:
            a="graph_"+i+"_"+j+".pkl"
            with open("Graphs/" + a, "rb") as f:
                    G = pickle.load(f)
            find_initial_probability(G,a,int(j),"initial_probability/"+i+"_"+j)
else:
    print(f"Folder 'initial_probability' already exists. Skipping execution.")

