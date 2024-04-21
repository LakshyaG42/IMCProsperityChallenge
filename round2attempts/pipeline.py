import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
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

# Initialize a Pipeline with feature selection and Random Forest Regression
pipeline = Pipeline([
    ('feature_selection', SelectFromModel(RandomForestRegressor())),
    ('regression', RandomForestRegressor())
])

# Fit the pipeline on the training data
pipeline.fit(X_train, y_train)

# Make predictions
y_pred_test = pipeline.predict(X_test)

# Calculate MSE on test set
mse_test = mean_squared_error(y_test, y_pred_test)
print("Mean Squared Error on Test Set:", mse_test)

# Get selected features
selected_features = X_train.columns[pipeline.named_steps['feature_selection'].get_support()]
print("Selected Features:", selected_features)
