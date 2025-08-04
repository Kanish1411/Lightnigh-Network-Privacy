import networkx as nx


g=nx.DiGraph()
def func(u,v,d):
    print(u,v)
    print("\n")
    return 1

g.add_node("1")
g.add_node("2")
g.add_node("3")
g.add_node("4")
g.add_node("5")
g.add_node("6")

g.add_edge("1","2",weight=10)
g.add_edge("2","3",weight=10)
g.add_edge("3","4",weight=10)
g.add_edge("1","5",weight=10)
g.add_edge("5","4",weight=10)

print(nx.shortest_path(g,source="1",target="4",weight=lambda u,v,d:func(u,v,d),method="dijkstra"))
