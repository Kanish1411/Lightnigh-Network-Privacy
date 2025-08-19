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

def generate_combined_entropy_csv():
    amounts = ["10", "100", "1000", "10000"]
    types = ["Source", "Destination"]
    fn=os.listdir("initial_probability")

    # Create header
    header = ["Amount"]
    for f in fn:
        for typ in types:
            header.append(f"{f.split(".")[0]}_{typ}")

    # Prepare CSV rows
    csv_rows = [header]
    for amt in amounts:
        row = [amt]
        for f in fn:
            for typ in types:
                filename = f"initial_probability/{f}"
                entropy = compute_entropy(filename, typ)
                row.append(entropy)
        csv_rows.append(row)

    # Ensure output directory exists
    output_dir = "entropy"
    os.makedirs(output_dir, exist_ok=True)

    # Write to single CSV
    output_file = os.path.join(output_dir, "combined_entropy_before.csv")
    with open(output_file, mode="w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)

    print(f"Combined entropy saved to '{output_file}'")

# Generate the CSV
generate_combined_entropy_csv()
