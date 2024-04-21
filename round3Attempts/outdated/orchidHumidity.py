import pandas as pd

# Load data from CSV file
def load_data():
    # Load CSV data into separate DataFrames
    data1 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_-1.csv', delimiter=';')
    data2 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_0.csv', delimiter=';')
    data3 = pd.read_csv('round-2-island-data-bottle/prices_round_2_day_1.csv', delimiter=';')

    # Concatenate DataFrames
    data = pd.concat([data1, data2, data3], ignore_index=True)
    return data

# Calculate correlation coefficient between humidity and orchid price
def calculate_correlation(data):
    correlation = data['HUMIDITY'].corr(data['ORCHIDS'])
    return correlation

if __name__ == "__main__":
    data = load_data()
    
    if 'HUMIDITY' in data.columns and 'ORCHIDS' in data.columns:
        correlation = calculate_correlation(data)
        print(f'Correlation between Humidity and Orchid Price: {correlation}')
    else:
        print('Error: Humidity or OrchidPrice column not found in the data.')
