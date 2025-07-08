import matplotlib.pyplot as plt

# Amounts
amounts = ["10", "100", "1000", "10000"]

# Table 1: Original node counts
normal_source = [178, 1, 3, 4]
normal_dest = [15, 1, 5701, 1822]
uniform_source = [1, 45, 4367, 15]
uniform_dest = [313, 24, 1, 1884]
bimodal_source = [925, 20, 57, 4]
bimodal_dest = [6, 1, 12, 2376]

# Table 2: Filtered node counts
normal_source_f = [20, 1, 3, 3]
normal_dest_f = [3, 1, 1, 1]
uniform_source_f = [1, 44, 4367, 1]  # '-' treated as 0
uniform_dest_f = [78, 22, 1, 2]
bimodal_source_f = [920, 20, 56, 1]
bimodal_dest_f = [4, 1, 5, 892]

# Styling helper
def plot_graph(title, source, dest, source_f, dest_f):
    plt.figure(figsize=(8, 5))
    plt.plot(amounts, source, label="Source", marker="o", color="blue")
    plt.plot(amounts, dest, label="Destination", marker="o", color="red")
    plt.plot(amounts, source_f, label="Source (Filtered)", linestyle="--", marker="x", color="blue")
    plt.plot(amounts, dest_f, label="Destination (Filtered)", linestyle="--", marker="x", color="red")
    plt.title(f'{title} Graph Node Counts')
    plt.xlabel('Amount')
    plt.ylabel('Node Count')
    plt.xticks(amounts)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Create plots
plot_graph("Normal", normal_source, normal_dest, normal_source_f, normal_dest_f)
plot_graph("Uniform", uniform_source, uniform_dest, uniform_source_f, uniform_dest_f)
plot_graph("Bimodal", bimodal_source, bimodal_dest, bimodal_source_f, bimodal_dest_f)
