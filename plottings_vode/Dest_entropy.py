import matplotlib.pyplot as plt

# Table 5: Destination Entropy (Before Experiment)
amounts_5 = [ "10", "100", "1000", "10000"]
normal_5 = [ 2.271973, 0.0, 12.475252, 12.332684]
uniform_5 = [ 8.290019, 4.572688, 0.0, 5.866716]
bimodal_5 = [ 2.040622, 0.0, 3.580163, 12.257639]

# Table 11: Destination Entropy (After Experiment)
amounts_11 = ["10", "100", "1000", "10000"]
normal_11 = [1.333708, 0.0, 0.0, 1.584963]
uniform_11 = [6.285402, 4.445615, 0.0, None]  # None for missing value
bimodal_11 = [1.62055, 0.0, 2.304591, 1.584963]

# Plotting
plt.figure(figsize=(10, 6))

# Table 5 (Before) lines
plt.plot(amounts_5, normal_5, 'o-', label='Normal (Before)', color='blue')
plt.plot(amounts_5, uniform_5, 'o-', label='Uniform (Before)', color='green')
plt.plot(amounts_5, bimodal_5, 'o-', label='Bimodal (Before)', color='red')

# Table 11 (After) lines
amounts_11_num = ["10", "100", "1000", "10000"]  # align with x-axis
plt.plot(amounts_11_num, normal_11, 's--', label='Normal (After)', color='blue')
plt.plot(amounts_11_num, uniform_11, 's--', label='Uniform (After)', color='green')
plt.plot(amounts_11_num, bimodal_11, 's--', label='Bimodal (After)', color='red')

# Labels and legend
plt.xlabel('Transaction Amount')
plt.ylabel('Entropy')
plt.title('Comparison of Destination Entropy Before and After Experiment')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
