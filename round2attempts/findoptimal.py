import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load CSV data into separate DataFrames
data1 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', delimiter=';')
data2 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_0.csv', delimiter=';')
data3 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_1.csv', delimiter=';')

# Concatenate DataFrames
data = pd.concat([data1, data2, data3], ignore_index=True)

# Select relevant features
features = ['TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY']

X = data[features]
y = data['ORCHIDS']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Regressor
random_forest_reg = RandomForestRegressor()

# Train the Random Forest model
random_forest_reg.fit(X_train, y_train)

# Get feature importances
feature_importances = random_forest_reg.feature_importances_

# Print feature importances
for feature, importance in zip(features, feature_importances):
    print(f"{feature}: {importance}")

# Make predictions
y_pred_test = random_forest_reg.predict(X_test)

# Calculate MSE on test set
mse_test = mean_squared_error(y_test, y_pred_test)
print("Mean Squared Error on Test Set:", mse_test)
