import numpy as np
from scipy.ndimage import gaussian_filter1d

from championship_leverage_index.core.constants import NBA_FINALS_APP_BY_SEED

if __name__ == '__main__':
    # NBA Finals appearances by seed since merger (1976-1977)
    seed_counts = np.array(NBA_FINALS_APP_BY_SEED)

    # Standard deviation for the Gaussian kernel
    sigma = 1

    # Apply Gaussian smoothing to the seed counts dataset
    smoothed_counts = gaussian_filter1d(seed_counts, sigma=sigma, mode='reflect')

    # Calculate the sum of the entire array
    total_sum = np.sum(seed_counts)

    # Display the original and smoothed seed counts
    print("Original Seed Counts:")
    print(seed_counts)
    print("\nSmoothed Seed Counts:")
    print(smoothed_counts)

    # Calculate and print the proportions of smoothed seed counts compared to the sum of the entire array
    smoothed_proportions = smoothed_counts / total_sum
    print("\nSmoothed Seed Proportions compared to the sum of the entire array:")
    print(smoothed_proportions)
