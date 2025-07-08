import matplotlib.pyplot as plt

# Table 4: Original Entropy (before experiment)
amounts_4 = [ "10", "100", "1000", "10000"]
normal_4 = [ 7.176115, 0.0, 1.584963, 11.203950]
uniform_4 = [ 0.0, 5.421043, 12.029850, 10.639436]
bimodal_4 = [ 9.770597, 4.300559, 5.687008, 10.789788]

# Table 10: After Experiment
amounts_10 = ["10", "100", "1000", "10000"]
normal_10 = [4.27214, 0.0, 1.584963, 0.528321]
uniform_10 = [0.0, 5.456569, 12.092427, 9.483287]  # None for missing value
bimodal_10 = [9.844487, 4.321928, 5.723346, 9.811887]  # -0.0 = 0.0

# Plotting
plt.figure(figsize=(10, 6))

# Table 4 lines
plt.plot(amounts_4, normal_4, 'o-', label='Normal (Before)', color='blue')
plt.plot(amounts_4, uniform_4, 'o-', label='Uniform (Before)', color='green')
plt.plot(amounts_4, bimodal_4, 'o-', label='Bimodal (Before)', color='red')

# Table 10 lines
plt.plot(amounts_10, normal_10, 's--', label='Normal (After)', color='blue')
plt.plot(amounts_10, uniform_10, 's--', label='Uniform (After)', color='green')
plt.plot(amounts_10, bimodal_10, 's--', label='Bimodal (After)', color='red')

# Labels and legend
plt.xlabel('Transaction Amount')
plt.ylabel('Entropy')
plt.title('Comparison of Source Entropy Before and After Experiment')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
