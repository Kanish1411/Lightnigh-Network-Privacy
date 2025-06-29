import os
import csv
from collections import defaultdict

# Configuration
amounts = ["10", "100", "1000", "10000"]
graph_types = ["Normal", "Uniform_Normal", "Bimodal"]
data_dir = "final_results"

# Store results
avg_table = defaultdict(lambda: defaultdict(lambda: {"Source": 0, "Destination": 0}))
max_table = defaultdict(lambda: defaultdict(lambda: {"Source": 0, "Destination": 0}))

# Parse each file
for gtype in graph_types:
    for amt in amounts:
        fname = f"probabilities_src_dst_nodes_{gtype}_{amt}_"
        matching_files = [f for f in os.listdir(data_dir) if f.startswith(fname)]
        if not matching_files:  # No matching files found
            print(f"Missing: {fname}")
            continue
        # Use the first matching file
        fname = matching_files[-1]  # Get the last modified file
        # Construct the full path
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            print(f"Missing: {fname}")
            continue

        source_probs = []
        dest_probs = []

        with open(path, newline='') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) < 3:
                    continue
                kind, node, prob = row[0].strip(), row[1].strip(), row[2].strip()
                try:
                    p = float(prob)
                except ValueError:
                    continue
                if kind == "Source":
                    source_probs.append(p)
                elif kind == "Destination":
                    dest_probs.append(p)

        # Save stats
        if source_probs:
            avg_table[amt][gtype]["Source"] = sum(source_probs) / len(source_probs) # type: ignore
            max_table[amt][gtype]["Source"] = max(source_probs)
        if dest_probs:
            avg_table[amt][gtype]["Destination"] = sum(dest_probs) / len(dest_probs) # type: ignore
            max_table[amt][gtype]["Destination"] = max(dest_probs)

# LaTeX helper
def generate_latex(title, data_dict, caption):
    print("\\begin{table}[h!]")
    print("\\centering")
    print("\\begin{tabular}{|c|c|c|c|c|c|c|}")
    print("\\hline")
    print("\\multirow{2}{*}{Amount} & \\multicolumn{2}{c|}{Normal} & \\multicolumn{2}{c|}{Uniform} & \\multicolumn{2}{c|}{Bimodal} \\\\")
    print("\\cline{2-7}")
    print(" & Source & Destination &  Source & Destination & Source & Destination \\\\")
    print("\\hline")

    for amt in amounts:
        row = [amt]
        for gtype in graph_types:
            s = data_dict[amt][gtype]["Source"]
            d = data_dict[amt][gtype]["Destination"]
            row.append(f"{s:.4f}")
            row.append(f"{d:.4f}")
        print(" & ".join(row) + " \\\\")

    print("\\hline")
    print("\\end{tabular}")
    print(f"\\caption{{{caption}}}")
    print("\\end{table}")
    print()

# Generate tables
generate_latex("Average Probabilities", avg_table, "Average Probability of the nodes in the set")
generate_latex("Maximum Probabilities", max_table, "Maximum Probability of the nodes in the set")
