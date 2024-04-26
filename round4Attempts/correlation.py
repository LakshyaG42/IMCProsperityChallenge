import pandas as pd
import matplotlib.pyplot as plt

# Read trades data CSV
# Load CSV data into separate DataFrames
data1 = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_1.csv', delimiter=';')
data2 = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_2.csv', delimiter=';')
data3 = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_3.csv', delimiter=';')
# Concatenate DataFrames
daily_data = pd.concat([data1, data2, data3], ignore_index=True)

# Merge data based on timestamp or day column
merged_data = pd.merge(trades_data, daily_data, on='timestamp')

# Clean data (handle missing values, convert data types)
# For example, assuming 'price' columns are numeric, convert them to float
merged_data['mid_price'] = merged_data['mid_price'].astype(float)

# Calculate returns for Coconuts and Coconut Coupons
merged_data['coconut_returns'] = merged_data[merged_data['product'] == 'COCONUT']['mid_price'].pct_change()
merged_data['coconut_coupon_returns'] = merged_data[merged_data['product'] == 'COCONUT_COUPON']['mid_price'].pct_change()

# Compute correlation
correlation = merged_data['coconut_returns'].corr(merged_data['coconut_coupon_returns'])

# Visualize correlation
plt.scatter(merged_data['coconut_returns'], merged_data['coconut_coupon_returns'])
plt.xlabel('Coconut Returns')
plt.ylabel('Coconut Coupon Returns')
plt.title('Coconut vs Coconut Coupon Returns Correlation')
plt.show()

print(f'Correlation coefficient between Coconuts and Coconut Coupons: {correlation}')