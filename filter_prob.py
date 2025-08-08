import os
import csv

input_folder = "initial_probability"
output_file = "csv_with_1.0.txt"

matching_files = []

# Traverse through all files in the folder
for root, _, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            with open(file_path, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 3 and row[0] in ["Average Source Probability", "Average Destination Probability"]:
                        try:
                            value = float(row[2])
                            if value == 1.0:
                                matching_files.append(file_path)
                                break  # Stop checking this file once a match is found
                        except ValueError:
                            continue

# Write matching filenames to txt
with open(output_file, "w") as txtfile:
    for filename in matching_files:
        txtfile.write(filename + "\n")

print(f"✅ Done! Found {len(matching_files)} CSV files with value 1.0. Saved to {output_file}")
