import json
import pickle
import networkx as nx
from lnbalance import *

def init_normal(amt=0):
    G=nx.DiGraph()
    with open("Data/Graph_new.json", encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    with open("Data/netstats.json", encoding="utf-8") as f:
        stats_data=json.load(f)
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

def init_unif_normal(amt):
    global G
    G=nx.DiGraph()
    with open("Data/Graph_new.json", encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    with open("Data/netstats.json", encoding="utf-8") as f:
        stats_data=json.load(f)
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
                    G.add_edge(edge["node1_pub"], edge["node2_pub"], capacity=int(edge["capacity"]/2),
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

def init_Bimodal(amt):
    global G
    G=nx.DiGraph()
    with open("Data/Graph_new.json", encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    with open("Data/netstats.json", encoding="utf-8") as f:
        stats_data=json.load(f)
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