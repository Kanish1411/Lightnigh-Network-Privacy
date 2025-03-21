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
    # src = max(l_src, key=l_src.get, default=None)
    # d = max(l_dest, key=l_dest.get, default=None)

    # if s > 0:
    #     for i in l_src:
    #         f.write(f"Probability of Source {i}: {l_src[i] / s} \n")
    #     for i in l_dest:
    #         f.write(f"Probability of Destination {i}: {l_dest[i] / s} \n")

    # f.write(f"\nMost Probable Source: {src}, Most Probable Destination: {d} \n")

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

def main():

    source = "03b1be68b8f564fe53f5456cf4bec901ba968fb72ed7291279ab0c87e0d22f1f49"  
    target = "0242a4ae0c5bef18048fbecf995094b74bfb0f7391418d71ed394784373f41e4f3" 
    path=[]
    global unused_path
    with open("paths.txt", "a+") as f:
        for trx_amt in [100000]:
            try:
                init(trx_amt)
                unused_path=[]
                path = nx.shortest_path(G, source=source, target=target, weight=lambda u, v, d: edge_cost(u, v, d, trx_amt))
                f.write(f"Shortest path for tx amount {trx_amt}: {path}\n")
                print(f"Shortest path for tx amount {trx_amt}: {path}") 
                print(calculate_total_fee(path=path,trx_amt=trx_amt,G=G))
                print(calculate_total_fee(path=path[1:],trx_amt=trx_amt,G=G))
                # draw_graph(path,trx_amt)

            except nx.NetworkXNoPath:
                f.write(f"No path found for tx amount {trx_amt}\n")
                print(f"No path found for tx amount {trx_amt}")

    # find_source_dest_pair('03b1be68b8f564fe53f5456cf4bec901ba968fb72ed7291279ab0c87e0d22f1f49', '030474c6abc3ec16c163592480865f76a3c18ef206540a3554889973fbd5be6375', '0242a4ae0c5bef18048fbecf995094b74bfb0f7391418d71ed394784373f41e4f3',trx_amt)
    print(path)

if __name__ == "__main__":
    # init()
    main()
    # test()



