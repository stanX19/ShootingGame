import numpy as np
import matplotlib.pyplot as plt

# Function to generate random number with y = 1/x distribution
def random_1_over_x(low=1, high=100, size=1):
    # Calculate the CDF values for the specified range
    u = np.random.uniform(0, 1, size)
    return np.exp(u * np.log(high))

# Generate a sample of 10000 random numbers
samples = random_1_over_x(size=10000)

# Plot the histogram of the generated samples
plt.hist(samples, bins=100, density=True, alpha=0.6, color='g', edgecolor='black')
plt.xlabel('Value')
plt.ylabel('Probability Density')
plt.title('Histogram of Generated Samples')
plt.show()