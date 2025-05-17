import math
import random

def bimodal_pdf(x, c, s):
    return math.exp(-x / s) + math.exp((x - c) / s)

def generate_bimodal_random(c, s, num_samples=1):
    samples = []
    max_pdf = bimodal_pdf(0, c, s)  
    while len(samples) < num_samples:
        x = random.uniform(0, c)
        y = random.uniform(0, max_pdf)
        if y <= bimodal_pdf(x, c, s):
            samples.append(x)
    return samples if num_samples > 1 else samples[0]

print(generate_bimodal_random(1000))