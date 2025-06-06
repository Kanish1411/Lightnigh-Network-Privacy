import pandas as pd

def csv_ext(a):
    print(a)
    df = pd.read_csv(a)

    # Filter by Type
    source_df = df[df["Type"] == "Source"]
    destination_df = df[df["Type"] == "Destination"]

    # Print counts
    print("Source count:", len(source_df))
    print("Destination count:", len(destination_df))

    # Print max probability
    print("Max probability in Source:", round(source_df["Probability"].max(),4))
    print("Max probability in Destination:", round(destination_df["Probability"].max(),4))

for i in ["Bimodal"]:
    for j in ["0","10","100","1000","10000"]:
        a=i+"_"+j
        csv_ext(a)
