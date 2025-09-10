import pandas as pd
import numpy as np

# Generate synthetic pincode to lat/lon mapping for pincodes in the dataset
# For simplicity, generate random lat/lon within India approximate bounds

num_pincodes = 10000  # Number of unique pincodes to generate

# Generate pincodes as 6-digit numbers starting from 100000
pincodes = np.arange(100000, 100000 + num_pincodes)

# Latitude approx range for India: 6.5 to 35.5
latitudes = np.random.uniform(6.5, 35.5, num_pincodes)

# Longitude approx range for India: 68.0 to 97.5
longitudes = np.random.uniform(68.0, 97.5, num_pincodes)

df = pd.DataFrame({
    'pincode': pincodes,
    'latitude': latitudes,
    'longitude': longitudes
})

df.to_csv('pincode_latlon.csv', index=False)
print("Generated pincode_latlon.csv with synthetic lat/lon data.")
