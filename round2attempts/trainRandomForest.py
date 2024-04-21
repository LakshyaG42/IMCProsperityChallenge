import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import json

# Load CSV data into separate DataFrames
data1 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', delimiter=';')
data2 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_0.csv', delimiter=';')
data3 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_1.csv', delimiter=';')

# Concatenate DataFrames
data = pd.concat([data1, data2, data3], ignore_index=True)

# Select relevant features
features = ['TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY']

# Split data into features and target variable
X = data[features]
y = data['ORCHIDS']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
random_forest_reg = RandomForestRegressor()
random_forest_reg.fit(X_train, y_train)

# Extract information from the trained model
trees = random_forest_reg.estimators_  # Get all decision trees in the forest

tree_data = []
for tree in trees:
    tree_dict = {
        'feature_indices': tree.tree_.feature.tolist(),
        'thresholds': tree.tree_.threshold.tolist(),
        'values': tree.tree_.value.tolist(),
        'children_left': tree.tree_.children_left.tolist(),
        'children_right': tree.tree_.children_right.tolist()
    }
    tree_data.append(tree_dict)

# Save the tree data to a JSON file
with open('random_forest_model.json', 'w') as f:
    json.dump(tree_data, f)

random_forest_pred = random_forest_reg.predict(X_test)
random_forest_mse = mean_squared_error(y_test, random_forest_pred)
random_forest_r2 = r2_score(y_test, random_forest_pred)
print(f"Random Forest MSE: {random_forest_mse}")
print(f"Random Forest R-squared: {random_forest_r2}")
print("Random Forest model information saved to random_forest_model.json")