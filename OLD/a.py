import pickle
import networkx as nx

# Load the graph from the .pkl file
with open("filtered_graphs\g10_ignore_bimodal_exponential_filtered_10000.pkl", "rb") as f:
    G = pickle.load(f)

# Make sure it's a networkx graph
print(type(G))

for u, v, attrs in G.edges(data=True):
    print(f"Edge: {u} -- {v}")
    print(f"Attributes: {attrs}\n")