import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load CSV data into separate DataFrames
data1 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', delimiter=';')
data2 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_0.csv', delimiter=';')
data3 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_1.csv', delimiter=';')

# Concatenate DataFrames
data = pd.concat([data1, data2, data3], ignore_index=True)

print(data.columns)
# Select relevant features
features = ['TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY']

# Split data into features and target variable
X = data[features]
y = data['ORCHIDS']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


# Initialize regression models
linear_reg = LinearRegression()
random_forest_reg = RandomForestRegressor()
svr_reg = SVR()

# Train the models
linear_reg.fit(X_train, y_train)
random_forest_reg.fit(X_train, y_train)
svr_reg.fit(X_train, y_train)


# Make predictions
linear_reg_pred = linear_reg.predict(X_test)
random_forest_pred = random_forest_reg.predict(X_test)
svr_pred = svr_reg.predict(X_test)

# Evaluate model performance
linear_reg_mse = mean_squared_error(y_test, linear_reg_pred)
random_forest_mse = mean_squared_error(y_test, random_forest_pred)
svr_mse = mean_squared_error(y_test, svr_pred)

linear_reg_r2 = r2_score(y_test, linear_reg_pred)
random_forest_r2 = r2_score(y_test, random_forest_pred)
svr_r2 = r2_score(y_test, svr_pred)

print("Random Forest MSE:", random_forest_mse)

print("Random Forest R-squared:", random_forest_r2)

# Plotting Random Forest Regression predictions
plt.figure(figsize=(10, 6))
plt.scatter(y_test, random_forest_pred, color='green', label='Random Forest Predictions')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Identity line
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Random Forest Model Performance')
plt.legend()
plt.show()
