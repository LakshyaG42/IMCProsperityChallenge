import pandas as pd
from sklearn.linear_model import RandomTree
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load data from CSV file
def load_data():
    # Load CSV data into separate DataFrames
    data1 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', delimiter=';')
    data2 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_0.csv', delimiter=';')
    data3 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_1.csv', delimiter=';')

    # Concatenate DataFrames
    data = pd.concat([data1, data2, data3], ignore_index=True)
    return data

# Train a linear regression model
def train_model(data):
    X = data[['HUMIDITY']]  # Features (independent variable)
    y = data['ORCHIDS']  # Target (dependent variable)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the model
    model = RandomTree()
    model.fit(X_train, y_train)

    return model, X_test, y_test

# Evaluate the model
def evaluate_model(model, X_test, y_test):
    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return mse, r2

if __name__ == "__main__":
    data = load_data()
    
    if 'HUMIDITY' in data.columns and 'ORCHIDS' in data.columns:
        model, X_test, y_test = train_model(data)
        mse, r2 = evaluate_model(model, X_test, y_test)
        print(f'Mean Squared Error: {mse}')
        print(f'R-squared Score: {r2}')
    else:
        print('Error: Humidity or OrchidPrice column not found in the data.')
