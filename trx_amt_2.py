import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from math import prod
G = nx.DiGraph()


a="test_less_v2"

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

def init(amt=0):
    global G
    G=nx.DiGraph()
    with open("now_latest.json", encoding="utf-8") as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["pub_key"])
    base_fee=1000
    prop_fee=5000
    timelock=50
    rf=1e-9
    bias=0
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
                ########## false right?????????????
                if edge["node1_policy"]["disabled"] != True:
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
                if edge["node2_policy"]["disabled"] != True:
                    G.add_edge(edge["node2_pub"], edge["node1_pub"], capacity=int(edge["capacity"]),
                                                                            base_fee=int(edge["node2_policy"]["fee_base_msat"]),
                                                                            prop_fee=int(edge["node2_policy"]["fee_rate_milli_msat"]),
                                                                            timelock=int(edge["node2_policy"]["time_lock_delta"]),
                                                                            rf=rf,
                                                                            bias=bias)

with open(a+"/data.json", "r") as j:
    data = json.load(j)

c=0
for i in data:
    if i!="actuual destination":
        c+=len(data[i])
l=[]
for i in data:
    print(i,len(data[i])/c)
    l.append([i,len(data[i])/c])

print(max(l,key=lambda x: x[1]))


with open(a+"/src.json", "r") as j:
    src = json.load(j)

with open(a+"/misc.json", "r") as j:
    misc = json.load(j)

amt={}
nodes={}
for i in data:
    init(float(i))
    p=0
    x=0
    nodes[i]=[]
    for s in src:
        for d in data[i]:
            try:
                path=nx.shortest_path(G,source=s,target=d,weight=lambda u, v, da: edge_cost(u, v, da, float(i)))
            except:
                continue
            if path!=[]:
                if ([misc['n-1'], misc["attacker"], misc["n+1"]] in [path[j:j+3] for j in range(len(path)-2)]):
                    if (round(calculate_fee_at_node(G=G,path=path,trx_amt=float(i),node=misc["attacker"]),4) == round(misc["amt"],4)):
                        p+=1
                        nodes[i].append([s,d])
                x+=1
            # print(calculate_fee_at_node(G=G,path=path,trx_amt=1000,node=misc["attacker"]))
    amt[i]=p/x
amt=sorted(amt.items(), key=lambda x:x[1])
print(amt)
amt_rev = amt[-5:][::-1]
for j in amt_rev:
    if j[1]!=0.0:
        s={}
        d={}
        for i in nodes[j[0]]:
            if i[0]==misc["source"] and i[1]==misc["dest"]:
                print("lets goooooooooooooooooooooooooooo")
            if i[0] not in s:
                s[i[0]]=1
            else:
                s[i[0]]+=1
            if i[1] not in d:
                d[i[1]]=1
            else:
                d[i[1]]+=1
        print(sorted(s.items(), key=lambda x:x[1])[-10:][::-1])
        print(sorted(d.items(), key=lambda x:x[1])[-10:][::-1])
print(len(s))