import numpy as np
from sklearn.ensemble import RandomForestRegressor

from championship_leverage_index.core.constants import NBA_SEEDS, NBA_FINALS_APP_BY_SEED_GAUSSIAN_SMOOTHED

if __name__ == '__main__':
    # Historical championship wins by seed
    # Seeds range from 1 to 8
    seeds = np.array(NBA_SEEDS)
    championship_wins = np.array(NBA_FINALS_APP_BY_SEED_GAUSSIAN_SMOOTHED)

    # Reshape the data for regression
    X = seeds.reshape(-1, 1)
    y = championship_wins.reshape(-1, 1)

    random_forest_model = RandomForestRegressor(n_estimators=1000, max_depth=5)

    random_forest_model.fit(X, y.ravel())  # ravel y to convert it to a 1D array

    # Predict championship percentages for each seed
    championship_percentages = random_forest_model.predict(X)

    # Ensure percentages sum to 100
    total_percentage = np.sum(championship_percentages)

    final_percentages = (championship_percentages / total_percentage) * 100

    print("Championship Percentages for Each Seed:")
    for seed, percentage in zip(seeds, final_percentages):
        print(f"Seed {seed}: {percentage:.1f}%")


