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
                    continue
                if row[0].strip() == node_type:
                    continue

                try:
                    prob = float(row[2])
                    if prob > 0:
                        entropy += prob * math.log2(prob)
                except ValueError:
                    continue
        return round(-entropy, 6)
    except FileNotFoundError:
        return None

amounts = ["10", "100", "1000", "10000"]
distributions = ["Normal", "Uniform_Normal", "Bimodal"]

# Initialize results dictionary
results = {
    amt: {
        dist: {'Source': '-', 'Destination': '-'}
        for dist in distributions
    }
    for amt in amounts
}

# Compute entropy and fill results
for amt in amounts:
    for dist in distributions:
        pattern = f"probabilities_src_dst_nodes_{dist}_{amt}"
        matching_files = [f for f in os.listdir("./final_results") if f.startswith(pattern)]

        if matching_files:
            latest_file = sorted(matching_files)[0]
            full_path = os.path.join("final_results", latest_file)

            src_entropy = compute_entropy(full_path, "Source")
            dst_entropy = compute_entropy(full_path, "Destination")

            results[amt][dist]['Source'] = str(src_entropy) if src_entropy is not None else '-'
            results[amt][dist]['Destination'] = str(dst_entropy) if dst_entropy is not None else '-'

# Ensure entropy folder exists
os.makedirs("entropy", exist_ok=True)

# Write to CSV
csv_file_path = os.path.join("entropy", "entropy_after.csv")
with open(csv_file_path, mode="w", newline='') as file:
    writer = csv.writer(file)
    header = ["Amount"]
    for dist in distributions:
        header.append(f"{dist}_Source")
        header.append(f"{dist}_Destination")
    writer.writerow(header)

    for amt in amounts:
        row = [amt]
        for dist in distributions:
            row.append(results[amt][dist]['Source'])
            row.append(results[amt][dist]['Destination'])
        writer.writerow(row)

print(f"Entropy data written to '{csv_file_path}'")
