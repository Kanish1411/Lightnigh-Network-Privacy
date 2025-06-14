import csv
import math

def compute_entropy(csv_filename):
    entropy = 0.0

    try:
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 3:
                    continue  # Skip incomplete rows

                if row[0].strip() != "Destination":
                    continue  # Only process rows where Type == "Source"

                try:
                    prob = float(row[2])
                    if prob > 0:
                        entropy += prob * math.log2(prob)
                except ValueError:
                    continue  # Skip rows with invalid probability

        return round(-entropy, 6)

    except FileNotFoundError:
        return 0.0  # If file not found, return 0

amounts = ["0", "10", "100", "1000", "10000"]
distributions = ["Normal", "Uniform_Normal", "Bimodal"]

# Collect entropy values
results = {amt: [] for amt in amounts}

for amt in amounts:
    for dist in distributions:
        filename = f"{dist}_{amt}"
        entropy = compute_entropy(filename)
        results[amt].append(entropy)

# Generate LaTeX table
print("\\begin{table}[h!]")
print("\\centering")
print("\\begin{tabular}{|c|c|c|c|}")
print("\\hline")
print("Amount & Normal & Uniform & Bimodal \\\\")
print("\\hline")
for amt in amounts:
    entropies = results[amt]
    row = f"{amt} & " + " & ".join(f"{e:.6f}" for e in entropies) + " \\\\"
    print(row)
print("\\hline")
print("\\end{tabular}")
print("\\caption{Source Entropy for different distributions and amounts}")
print("\\end{table}")
