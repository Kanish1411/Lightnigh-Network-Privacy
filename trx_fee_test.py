import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from math import prod
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


def find_source_dest_pair(prev, n, nxt, trx_amt,f=None):
    sources=[]
    dest=[]
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
    return sources,dest

def trx_amt_test(trx_amt=1000):
    init(trx_amt)
    while(1):
        src = random.choice(list(G.nodes()))
        dest = random.choice(list(G.nodes()))
        # src="025361e6c9aa972c3720cabd30903d921f3fc969e0d25b1a233f0e8ea348c3d122"
        # dest="03b72234539409e6390cf66322319cf2211f09880b015259bb66e69d47c507da05"
        if src!=dest:
            try:
                l=nx.shortest_path(G,source=src,target=dest,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                if len(l)>=3:
                    break
            except:
                pass
    print(l)
    att=random.choice(l[1:-1])
    ind=l.index(att)
    actual_amt=calculate_fee_at_node(l,trx_amt,G,att)
    print(actual_amt)
    _,dests=find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt=trx_amt)
    print(len(dests))
    new_dest={}
    lower=0
    upper=0
    # if len(dests)>100:
    #     return
    for d in dests:
        bf=[]
        pf=[]
        path=nx.shortest_path(G,source=att,target=d,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
        trx=calculate_total_fee(path,trx_amt=trx_amt,G=G)
        # print(path, trx)
        for i in range(len(path) - 1, 0, -1):
            v, u = path[i], path[i - 1] 
            edge_data = G[u][v]
            bf.append(edge_data.get("base_fee", 0))
            pf.append(edge_data.get("prop_fee", 0) / 1e6)
        b=0
        for i in range(len(bf)):
            a=1
            f=0
            ##################Update
            # for j in range(i+1,len(pf)):
            #     f=1
            #     a*=pf[j]
            if f==0:
                a=0
            b+=(bf[i]*(1+a))
        upper= trx-b
        b=0
        path=nx.shortest_path(G,source=att,target=d,weight=lambda u, v, d: edge_cost(u, v, d, upper))
        val=calculate_total_fee(path,trx_amt=upper,G=G)
        for i in bf:
            val-=i
        lower=upper-(val-upper)
        # print(upper,lower)
        # for i in range(len(bf)):
        #     inner_sum = 0
        #     for m in range(i + 1, len(bf)):
        #         product_term = prod(pf[i+1:m+1]) if m >= i + 1 else 0
        #         inner_sum += product_term
        #     total_sum += bf[i] * inner_sum
        # x_term = sum(prod(pf[:i]) for i in range(1, len(pf) + 1))
        # tl_rf=0
        # for m in range(len(tl)):
        #     tl_rf+=(tl[m]*rf[m])
        # lower=upper - (total_sum) -upper*x_term - trx_amt*tl_rf
        # print(d,upper,lower,x_term,total_sum, tl_rf)
        if upper > trx  or lower > trx:
            print(f"Out of bounds for {d}")
            break
        try:
            val=binary_search(upper,lower,actual_amt,att,d)
            if val == -1:
                break
            print(f"{d} is a possible Destination {round(val,ndigits=2)} ")
            new_dest[d]=val
        except:
            # print(f"{d} is not a possible Destination - Problem in Binary search {upper} {lower}")
            pass
    print(new_dest)
    print(len(new_dest))
    val=0
    for i in new_dest.keys():
        val+=new_dest[i]
    print(val/len(new_dest))
    
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
    
if __name__ == "__main__":
    trx_amt=1234.45
    # init(trx_amt)
    trx_amt_test(trx_amt)



