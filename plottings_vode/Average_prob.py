import matplotlib.pyplot as plt

# Table 2 (Original)
amounts_2 = [ '10', '100', '1000', '10000']
normal_source_2 = [ 0.0056, 1.0, 0.25, 0.25]
normal_dest_2 = [ 0.0625, 1.0, 0.0002, 0.0002]
uniform_source_2 = [ 1.0, 0.0217, 0.0002, 0.0008]
uniform_dest_2 = [ 0.0032, 0.04, 1.0, 0.0154]
bimodal_source_2 = [ 0.0011, 0.0476, 0.0172, 0.25]
bimodal_dest_2 = [0.1429, 1.0, 0.0769, 0.0002]

# Table 8 (Filtered)
amounts_8 = ['10', '100', '1000', '10000']
normal_source_8 = [0.0500, 1.0000, 0.3333, 0.3333]
normal_dest_8 = [0.3333, 1.0000, 1.0000, 0.3333]
uniform_source_8 = [1.0000, 0.0227, 0.0002, 0.0000]
uniform_dest_8 = [0.0128, 0.0455, 1.0000, 0.0000]
bimodal_source_8 = [0.0011, 0.0500, 0.0179, 1.0000]
bimodal_dest_8 = [0.2500, 1.0000, 0.2000, 0.3333]

def plot_combined_graph(amounts_full, src_full, dst_full, 
                        amounts_filt, src_filt, dst_filt, 
                        title, label):
    plt.figure(figsize=(7.5, 4))
    plt.plot(amounts_full, src_full, 'o-', color='royalblue', label=f'{label} Source (Original)')
    plt.plot(amounts_full, dst_full, 'o-', color='darkorange', label=f'{label} Destination (Original)')

    plt.plot(amounts_filt, src_filt, 's--', color='deepskyblue', label=f'{label} Source (Filtered)')
    plt.plot(amounts_filt, dst_filt, 's--', color='coral', label=f'{label} Destination (Filtered)')

    plt.title(title)
    plt.xlabel("Amount")
    plt.ylabel("Probability")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Plotting for each graph type
plot_combined_graph(amounts_2, normal_source_2, normal_dest_2,
                    amounts_8, normal_source_8, normal_dest_8,
                    "Normal Graph: Avg Probabilities", "Normal")

plot_combined_graph(amounts_2, uniform_source_2, uniform_dest_2,
                    amounts_8, uniform_source_8, uniform_dest_8,
                    "Uniform Graph: Avg Probabilities", "Uniform")

plot_combined_graph(amounts_2, bimodal_source_2, bimodal_dest_2,
                    amounts_8, bimodal_source_8, bimodal_dest_8,
                    "Bimodal Graph: Avg Probabilities", "Bimodal")
