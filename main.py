import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
G = nx.DiGraph()

op="case_1"

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

# def get_outgoing_neighbors(path):
#     outgoing_edges = set()
#     for node in path[:-1]:
#         for neighbor in G.successors(node):
#             # if neighbor in path:
#             #     continue
#             outgoing_edges.add((node, neighbor))
#     return outgoing_edges

# def draw_graph(shortest_path,trx_amt):
#     plt.figure(figsize=(10, 6))
#     pos=nx.random_layout(G)
#     outgoing_edges = get_outgoing_neighbors(shortest_path)
#     nodes=[]
#     edge={}
#     for i in outgoing_edges:
#         nodes.append(i[1])
#         if i[0] in edge:
#             edge[i[0]].append(i[1])
#         else:
#             edge[i[0]]=[i[1]]

#     with open("graph.txt","a+") as f:
#         f.write(f"For transaction {trx_amt}\n")
#         sh=""
#         for i in edge:
#             f.write(f"Starting from Node : {i}\n")
#             for j in edge[i]:
#                 data=G.get_edge_data(i,j)
#                 cost=edge_cost("","", data, trx_amt)
#                 f.write(f"address {j} \ndata: {data} \ncost: {cost}\n\n")
#                 if j in shortest_path:
#                     sh=j
#             f.write(f"id-{shortest_path.index(sh)} starting from {i} shortest path chosen {sh} \n")
#             f.write("-------------------------------\n")

#     nx.draw_networkx_edges(G,pos=pos,  edgelist=list(outgoing_edges), edge_color="black", width=1, alpha=0.7)

#     nx.draw_networkx_nodes(G, pos=pos, nodelist=shortest_path, node_color="red")

#     path_edges = list(zip(shortest_path, shortest_path[1:]))
#     nx.draw_networkx_edges(G, pos=pos, edgelist=path_edges, edge_color="blue", width=2)
#     nx.draw_networkx_nodes(G, pos=pos, nodelist=nodes, node_color="black", node_size=4)
#     plt.savefig("highlighted_shortest_path.png")  

    
def init(amt=0):
    global G
    G=nx.DiGraph()
    with open("Graph_new.json", encoding="utf-8") as f:
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
                continue
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
                continue
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
                    s+=1

    # Finding the most probable Source & Destination
    src = max(l_src, key=l_src.get, default=None)
    d = max(l_dest, key=l_dest.get, default=None)
    s1=0
    d1=0
    u=0
    v=0
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
    
    # Entropy Analysis
    # f.write("\nEntropy Analysis\n")
    # H = 0
    # s = sum(l_src.values())
    # print("Entropy analysis")
    # H=0
    # print("P(Bi|A)=P(A|Bi)/sum(P(A|Bk))")
    #####################
    # for i in sources:
    #     a=list(nx.shortest_path(G,source=i,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt)))
    #     u=0
    #     for i in a:
    #         if n in i:
    #             if n !=i[-1]:
    #                 u+=1
    #     print(f"P(A|Bi)= {u/len(a)}")
    #     pabi=u/len(a)
    #     s=0
    #     for j in sources:
    #         b=list(nx.shortest_path(G,source=j,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt)))
    #         u=0
    #         for i in b:
    #             if n in i:
    #                 if n !=i[-1]:
    #                     u+=1
    #         s+=u/len(b)
    #     H+=((pabi/s)*math.log2(pabi/s))
    # print(-1*H)
    ###############
    # if s > 0:
    #     for i in l_src:
    #         P_A_Bi = l_src[i] / s[i]
    #         H += P_A_Bi * math.log2(P_A_Bi)        
    #     f.write(f"\nEntropy: { -H}\n")
    # return -H

def main():

    global unused_path
    with open(op+"/paths.txt", "a+") as f:
        for trx_amt in [10,1000,10000]:
            init(trx_amt)
            
            while(1):
                    src1 = random.choice(list(G.nodes()))
                    dest = random.choice(list(G.nodes()))
                    # src1="02ae1f0670b5c14a4c065d1f32e70feeae5027de2b9d98f9d3b6f70ca7c364bd02"
                    # dest="03d9dd7d70829542f0eb9517f0f53471b269a9716c340abf08a8e234c1c9fb6a05"
                    if src1!=dest:
                        try:
                            #testing so it can use the amount
                            l=nx.shortest_path(G,source=src1,target=dest,weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                            if len(l)>=3:
                                break
                        except:
                            pass
            att=random.choice(l[1:-1]) 
            ind=l.index(att)
            try:
                f.write("\n------------------------------------------------------for {trx_amt}")
                init(trx_amt)
                unused_path=[]
                f.write(f"Shortest path for tx amount {trx_amt}: {l}\n")
                # draw_graph(path,trx_amt)

            except nx.NetworkXNoPath:
                f.write(f"No path found for tx amount {trx_amt}\n")
                print(f"No path found for tx amount {trx_amt}")

            find_source_dest_pair(l[ind-1],att,l[ind+1],trx_amt,f)

if __name__ == "__main__":
    main()



