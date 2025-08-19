import pickle
import networkx as nx
import os
import csv

def filter_graph(graph, threshold):
    """Filter only edges based on balance/capacity condition while keeping all nodes."""
    filtered_graph = graph.__class__()  # Maintain same graph type (Graph/DiGraph)
    
    # Add all nodes unchanged
    filtered_graph.add_nodes_from(graph.nodes(data=True))

    # Filter edges based on balance/capacity
    for u, v, attrs in graph.edges(data=True):
        if ('balance' in attrs and attrs['balance'] > threshold) or \
           ('balance' not in attrs and 'capacity' in attrs and attrs['capacity'] > threshold):
            filtered_graph.add_edge(u, v, **attrs)

    return filtered_graph

def process_pickles(input_dir, output_dir, thresholds):
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "filtered_graphs_log.csv")

    with open(log_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original File", "Threshold", "Filtered File", "Nodes", "Edges"])
        
        for file in os.listdir(input_dir):
            if file.endswith(".pkl") or file.endswith(".pickle"):
                file_path = os.path.join(input_dir, file)
                with open(file_path, 'rb') as f:
                    graph = pickle.load(f)

                if not isinstance(graph, (nx.Graph, nx.DiGraph)):
                    print(f"Skipping {file}: Not a NetworkX graph")
                    continue

                for threshold in thresholds:
                    filtered_graph = filter_graph(graph, threshold)
                    filtered_file_name = f"{os.path.splitext(file)[0]}_{threshold}.pkl"
                    filtered_file_path = os.path.join(output_dir, filtered_file_name)

                    # Save filtered graph
                    with open(filtered_file_path, 'wb') as out_f:
                        pickle.dump(filtered_graph, out_f)

                    # Log info with node and edge count
                    writer.writerow([file, threshold, filtered_file_name, 
                                     filtered_graph.number_of_nodes(), filtered_graph.number_of_edges()])
                    print(f"Created: {filtered_file_name} | Nodes: {filtered_graph.number_of_nodes()}, Edges: {filtered_graph.number_of_edges()}")

if __name__ == "__main__":
    input_directory = "./new_data"          # Folder containing original pickle files
    output_directory = "./filtered_graphs" # Folder to save filtered pickle files
    thresholds = [10, 100, 1000, 10000]

    process_pickles(input_directory, output_directory, thresholds)
