import csv
import math
import os

def compute_entropy(csv_filename, target_type):
    entropy = 0.0
    try:
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 3:
                    continue  # Skip incomplete rows

                if row[0].strip() != target_type:
                    continue  # Only process matching type rows

                try:
                    prob = float(row[2])
                    if prob > 0:
                        entropy += prob * math.log2(prob)
                except ValueError:
                    continue  # Skip invalid probabilities

        return round(-entropy, 6)

    except FileNotFoundError:
        return 0.0  # If file not found, return 0

def generate_entropy_csv(target_type):
    amounts = ["10", "100", "1000", "10000"]
    distributions = ["Normal", "Uniform_Normal", "Bimodal"]

    # Prepare CSV data
    csv_rows = [["Amount"] + distributions]
    for amt in amounts:
        row = [amt]
        for dist in distributions:
            filename = f"initial_probability/{dist}_{amt}"
            entropy = compute_entropy(filename, target_type)
            row.append(entropy)
        csv_rows.append(row)

    # Ensure output folder exists
    output_dir = "entropy"
    os.makedirs(output_dir, exist_ok=True)

    # Write to CSV file
    output_file = os.path.join(output_dir, f"{target_type.lower()}_entropy.csv")
    with open(output_file, mode="w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)

    print(f"Entropy for {target_type} saved to '{output_file}'")

# Generate both source and destination entropy CSVs
generate_entropy_csv("Source")
generate_entropy_csv("Destination")

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

amounts = [ "0","10","100","1000","10000"]
distributions = ["Normal", "Uniform_Normal", "Bimodal"]

# Collect entropy values
results = {amt: [] for amt in amounts}

for amt in amounts:
    for dist in distributions:
        filename = f"initial_probability/{dist}_{amt}"
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
