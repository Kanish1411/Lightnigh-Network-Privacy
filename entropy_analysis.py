import csv
import math
import os

def compute_entropy(csv_filename, node_type):
    entropy = 0.0
    try:
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 3:
                    continue  # Skip incomplete rows
                if row[0].strip() != node_type:
                    continue  # Only process specified node type

                try:
                    prob = float(row[2])
                    if prob > 0:
                        entropy += prob * math.log2(prob)
                except ValueError:
                    continue  # Skip rows with invalid probability
        return round(-entropy, 6)
    except FileNotFoundError:
        return None  # Return None if file is missing

amounts = ["10", "100", "1000", "10000"]
distributions = ["Normal", "Uniform_Normal", "Bimodal"]

# Initialize nested dictionary to store entropy values
results = {
    amt: {
        dist: {'Source': '-', 'Destination': '-'}
        for dist in distributions
    }
    for amt in amounts
}

# Search and compute entropy
for amt in amounts:
    for dist in distributions:
        pattern = f"probabilities_src_dst_nodes_{dist}_{amt}_"
        matching_files = [f for f in os.listdir("./final_results") if f.startswith(pattern)]

        if matching_files:
            latest_file = sorted(matching_files)[-1]  # Take the last file if multiples
            full_path = os.path.join("final_results", latest_file)

            src_entropy = compute_entropy(full_path, "Source")
            dst_entropy = compute_entropy(full_path, "Destination")

            results[amt][dist]['Source'] = str(src_entropy) if src_entropy is not None else '-'
            results[amt][dist]['Destination'] = str(dst_entropy) if dst_entropy is not None else '-'

# Print LaTeX table
print("\\begin{table}[h!]")
print("\\centering")
print("\\begin{tabular}{|c|c|c|c|c|c|c|}")
print("\\hline")
print("\\multirow{2}{*}{Amount} & \\multicolumn{2}{c|}{Normal} & \\multicolumn{2}{c|}{Uniform} & \\multicolumn{2}{c|}{Bimodal} \\\\")
print("\\cline{2-7}")
print(" & Source & Destination & Source & Destination & Source & Destination \\\\")
print("\\hline")

for amt in amounts:
    row = f"{amt}"
    for dist in distributions:
        row += " & " + str(results[amt][dist]['Source']) + " & " + str(results[amt][dist]['Destination'])
    row += " \\\\"
    print(row)

print("\\hline")
print("\\end{tabular}")
print("\\caption{Source and Destination Entropy for different distributions and amounts}")
print("\\end{table}")
