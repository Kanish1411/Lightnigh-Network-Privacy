import os
import pandas as pd

# Folder containing the CSV files
folder = "initial_probability"

# Prepare a list for storing the results
data = []

# Loop through all CSV files in the folder
for filename in os.listdir(folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(folder, filename)
        
        # Read the CSV
        df = pd.read_csv(filepath, header=None)
        
        # Extract values by matching labels
        avg_src_prob = df.loc[df[0] == "Average Source Probability", 2].values[0]
        avg_dst_prob = df.loc[df[0] == "Average Destination Probability", 2].values[0]
        
        most_prob_src = df.loc[df[0] == "Most Probable Source", 1].values[0]
        most_prob_dst = df.loc[df[0] == "Most Probable Destination", 1].values[0]
        
        # Store in our list
        data.append({
            "file": filename,
            "avg_source_probability": avg_src_prob,
            "avg_destination_probability": avg_dst_prob,
            "most_probable_source": most_prob_src,
            "most_probable_destination": most_prob_dst
        })

# Convert the list to a DataFrame
result_df = pd.DataFrame(data)

# Save to CSV if needed
result_df.to_csv("summary_table.csv", index=False)

# Show the table
print(result_df)
