import json
import pickle
import networkx as nx
from lnbalance import *
import os
import sys

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

def init_normal(amt,graph_file, netstats_file):
    G=nx.DiGraph()
    with open(graph_file, encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])

    with open(netstats_file, encoding="utf-8") as f:
        stats_data = json.load(f)
    base_fee=stats_data["latest"]["avg_base_fee_mtokens"]
    prop_fee=stats_data["latest"]["avg_fee_rate"]
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
    try:
        with open(f"Graphs/graph_Normal_{amt}.pkl", "wb") as f:
            pickle.dump(G, f)
    except:
        pass
    return G

def init_unif_normal(amt,graph_file, netstats_file):
    global G
    G=nx.DiGraph()
    with open(graph_file, encoding="utf-8") as f:
        data = json.load(f)
        print("graph file loaded")
    for node in data["nodes"]:
        G.add_node(node["pub_key"])

    with open(netstats_file, encoding="utf-8") as f:
        stats_data = json.load(f)
    print("eoroperp")
    base_fee=stats_data["latest"]["avg_base_fee_mtokens"]
    prop_fee=stats_data["latest"]["avg_fee_rate"]
    timelock=50
    rf=1e-9
    bias=1
    for edge in data["edges"]:
        if int(edge["capacity"])>=amt:
            if edge["node1_policy"] == None:
                G.add_edge(edge["node1_pub"], edge["node2_pub"],capacity=int(edge["capacity"])/2,
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node1_policy"]["disabled"] == True:
                    G.add_edge(edge["node1_pub"], edge["node2_pub"], capacity=int(edge["capacity"])/2,
                                                                            base_fee=int(edge["node1_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node1_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node1_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
            if edge["node2_policy"] == None:
                G.add_edge(edge["node2_pub"], edge["node1_pub"],capacity=int(edge["capacity"])/2,
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node2_policy"]["disabled"] == True:
                    G.add_edge(edge["node2_pub"], edge["node1_pub"], capacity=int(edge["capacity"])/2,
                                                                            base_fee=int(edge["node2_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node2_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node2_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
   
    try:
         with open(f"Graphs/graph_Uniform_Normal_{amt}.pkl", "wb") as f:
            pickle.dump(G, f)
    except:
        pass
    return G

def init_Bimodal(amt,graph_file, netstats_file):
    global G
    G=nx.DiGraph()
    with open(graph_file, encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    with open(netstats_file, encoding="utf-8") as f:
        stats_data = json.load(f)

    base_fee=stats_data["latest"]["avg_base_fee_mtokens"]
    prop_fee=stats_data["latest"]["avg_fee_rate"]
    timelock=50
    rf=1e-9
    bias=1
    c1=0
    c2=0
    for edge in data["edges"]:
        if int(edge["capacity"])>=amt:
            c1=random_bimodal(int(edge["capacity"]))
            c2=int(edge["capacity"])-c1
            print(c1,c2)
            if edge["node1_policy"] == None:
                G.add_edge(edge["node1_pub"], edge["node2_pub"],capacity=c1,
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node1_policy"]["disabled"] == True:
                    G.add_edge(edge["node1_pub"], edge["node2_pub"], capacity=c1,
                                                                            base_fee=int(edge["node1_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node1_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node1_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
            if edge["node2_policy"] == None:
                G.add_edge(edge["node2_pub"], edge["node1_pub"],capacity=c2,
                                                                            base_fee=base_fee,
                                                                            prop_fee=prop_fee,
                                                                            timelock=timelock,
                                                                            rf=rf,
                                                                            bias=bias)
            else:
                if edge["node2_policy"]["disabled"] == True:
                    G.add_edge(edge["node2_pub"], edge["node1_pub"], capacity=c2,
                                                                            base_fee=int(edge["node2_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node2_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node2_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)
    try:
        with open(f"Graphs/graph_Bimodal_{amt}.pkl", "wb") as f:
            pickle.dump(G, f)
    except:
        pass
    return G

if len(sys.argv) < 2:
    print("Usage: python3 script.py <graph_file> [netstats_file]")
    sys.exit(1)

graph_file = sys.argv[1]
netstats_file = sys.argv[2] if len(sys.argv) > 2 else "Data/netstats.json"
output_folder = "Graphs"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    for amt in [10, 100, 1000, 10000]:
        print("aaa")
        init_unif_normal(amt, graph_file, netstats_file)
else:
    print(f"Folder '{output_folder}' already exists. Skipping execution.")
