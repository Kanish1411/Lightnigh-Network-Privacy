import pickle
import networkx as nx
import os

def analyze_graph_pickle(file_path):
    # Load the pickle file
    with open(file_path, 'rb') as f:
        graph = pickle.load(f)
    
    # Ensure it is a NetworkX graph
    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        raise TypeError(f"The object in {file_path} is not a NetworkX graph.")

    # Basic insights
    print(f"Graph Insights for: {file_path}")
    print(f"Type of Graph: {type(graph).__name__}")
    print(f"Number of Nodes: {graph.number_of_nodes()}")
    print(f"Number of Edges: {graph.number_of_edges()}")
    print(f"Is Directed: {graph.is_directed()}")
    print(f"Graph Density: {nx.density(graph):.4f}")
    print("-" * 50)
    # Edge attributes
    print("\nEdge Attributes (first 10 edges):")
    edges_with_attrs = list(graph.edges(data=True))
    if edges_with_attrs:
        for u, v, attrs in edges_with_attrs[:10]:
            if attrs:
                print(f"Edge ({u}, {v}): {attrs}")
            else:
                print(f"Edge ({u}, {v}): No attributes")
    else:
        print("No edges or edge attributes found.")
 

if __name__ == "__main__":
    # for file in os.listdir(directory):
    #     if file.endswith(".pkl") or file.endswith(".pickle"):
    #         # analyze_graph_pickle(os.path.join(directory, file))
    analyze_graph_pickle("filtered_graphs\g10_ignore_bimodal_exponential_filtered_73627.pkl")  # Example file for testing
