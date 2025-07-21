
import csv

import csv
import json
import pickle
import networkx as nx
import os

G = nx.DiGraph()


def edge_cost(u, v, data, trx_amt):
    cost = (trx_amt * ((data.get("prop_fee",0) / 1e6) + (data.get("timelock", 0) * data.get("rf", 1e-9)))) +  data.get("base_fee", 0) + data.get("bias", 1)
    return cost

def calculate_total_fee(path, trx_amt, G):
    total_fee = 0
    amt_needed = trx_amt
    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1] 
        edge_data = G[u][v]
        base_fee = edge_data.get("base_fee", 0)
        prop_fee = amt_needed * ((edge_data.get("prop_fee", 0) / 1e6)+(edge_data.get("timelock", 0) * edge_data.get("rf", 1e-9)))
        hop_fee = base_fee + prop_fee + edge_data.get("bias", 0)
        total_fee += hop_fee
        amt_needed += hop_fee  
        # print(f"for hop {u} to {v} is {hop_fee} = {base_fee} {prop_fee} = {amt_needed}")
    return amt_needed

def calculate_fee_at_node(path, trx_amt, G,node):
    total_fee = 0
    amt_needed = trx_amt
    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1] 
        edge_data = G[u][v]
        base_fee = edge_data.get("base_fee", 0)
        prop_fee = amt_needed * ((edge_data.get("prop_fee", 0) / 1e6)+(edge_data.get("timelock", 0) * edge_data.get("rf", 1e-9)))
        hop_fee = base_fee + prop_fee + edge_data.get("bias", 0)
        total_fee += hop_fee
        amt_needed += hop_fee  
        if u==node:
            return amt_needed
    return 


def find_source_dest_pair(prev, n, nxt,trx_amt):
    sources=[]
    dest=[]
    # Source identification
    paths = nx.shortest_path(G, target=nxt,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            sources.append(i[0])
    # Destination finding
    paths = nx.single_source_dijkstra_path(G, prev,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt)) 
    paths = nx.single_source_dijkstra_path(G, prev,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt)) 
    for i in paths.values():
        if [prev, n, nxt] in [i[j:j+3] for j in range(len(i)-2)]:
            dest.append(i[-1])
    return sources,dest

def trx_amt_test(trx_amt,G,file,rows):
def trx_amt_test(trx_amt,G,file,rows):
    while(1):
        src1 = rows[0]["Source"]
        dest =  rows[0]["Destination"]
        src1 = rows[0]["Source"]
        dest =  rows[0]["Destination"]
        if src1!=dest:
            try:
                l=nx.shortest_path(G,source=src1,target=dest,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if len(l)>=3:
                    break
            except:
                break
    att=rows[0]["Attacker"]
    actual_amt=calculate_fee_at_node(l,trx_amt,G,att)
                break
    att=rows[0]["Attacker"]
    actual_amt=calculate_fee_at_node(l,trx_amt,G,att)
    ind=l.index(att)
    src,dests=find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt)
    new_dest={}
    lower=0
    upper=0
    for d in dests:
        bf=[]
        pf=[]
        path=nx.shortest_path(G,source=att,target=d,weight=lambda u, v, d: edge_cost(u, v, d, actual_amt))
        for i in range(len(path) - 1, 0, -1):
            v, u = path[i], path[i - 1] 
            edge_data = G[u][v]
            bf.append(edge_data.get("base_fee", 0))
            pf.append(edge_data.get("prop_fee", 0) / 1e6)
        n=len(bf)
        term1=0
        for i in range(n):
            z=1
            f=0
            for k in range(i+1,n):
                z*=pf[k]
                f=1
            if f!=1:
                z=0
            term1+=bf[i]*z
            z=1
            f=0
            for m in range(i,n):
                for k in range(i+1,m):
                    z*=pf[k]
                    f=1
            if f!=1:
                z=0
            term1+=bf[i]*z
            term1+=bf[i]

        upper = actual_amt - term1
        if upper<0:
            continue
        path=nx.shortest_path(G,source=att,target=d,weight=lambda u, v, d: edge_cost(u, v, d, upper))
        val=calculate_total_fee(path,trx_amt=upper,G=G)
        for i in bf:
            val-=i
        lower=upper-(val-upper)
        if lower <0:
            continue
        if upper > actual_amt  or lower > actual_amt:
            print(f"Out of bounds for {d}")
            break
        
        try:
            val=binary_search(upper,lower,actual_amt,att,d)
            if val == -1 or val==0:
                break
            print(f"{d} is a possible Destination {round(val,ndigits=2)} ")
            if round(val,ndigits=2) not in new_dest:
                new_dest[round(val,ndigits=2)]=[]
            new_dest[round(val,ndigits=2)].append(d)
        except:
            continue
    val=0

    os.mkdir(file)
    with open(file+"/data.json", "a") as j:

    os.mkdir(file)
    with open(file+"/data.json", "a") as j:
        json.dump(new_dest, j)
    with open(file+"/src.json", "a") as j:
    with open(file+"/src.json", "a") as j:
        json.dump(src, j)
    misc={}
    misc["source"]=src1
    misc["attacker"]=att
    misc["n-1"]=l[ind-1]
    misc["n+1"]=l[ind+1]
    misc["amt"]=actual_amt
    misc["dest"]=dest

    with open(file+"/misc.json", "a") as j:
    with open(file+"/misc.json", "a") as j:
        json.dump(misc, j)
    
def binary_search(h,l,val,src,dest):
    m=(h+l)/2
    c=calculate_total_fee(trx_amt=m,G=G,path=nx.shortest_path(G,source=src,target=dest,weight=lambda u, v, d: edge_cost(u, v, d, m)))
    if c>val:
        return binary_search(m,l,val,src,dest)
    if c<val:
        return binary_search(h,m,val,src,dest)
    if c==val:
        return m
    if l==h:
        return -1

with open("Data.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    rows_by_graph = {}

    for row in reader:
        graph_file = row["Graph"]
        if graph_file not in rows_by_graph:
            rows_by_graph[graph_file] = []
        rows_by_graph[graph_file].append(row)

# Your original loop
os.makedirs("Transaction_amt_test", exist_ok=True)  # Ensure the directory exists
for i in ["Normal", "Uniform_Normal", "Bimodal"]:
    for j in ["10","100","1000","10000"]: 
        graph_filename = f"graph_{i}_{j}.pkl"
        graph_path = os.path.join("Graphs", graph_filename)

        print(f"Processing: {graph_filename}")

        if os.path.exists(graph_path):
            with open(graph_path, "rb") as f:
                G = pickle.load(f)

            trx_amt = int(j)
            key = graph_filename

            if key in rows_by_graph:
                matched_rows = rows_by_graph[key]
                trx_amt_test(trx_amt=trx_amt, G=G, file=f"test/{i}_{j}", rows=matched_rows)
            else:
                print(f"No matching data rows found for: {key}")
        else:
            print(f"Graph file not found: {graph_path}")

