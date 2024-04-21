import jsonpickle as pickle
import pandas as pd
from datamodel import ConversionObservation, Order

# Load the Random Forest model
model_path = "random_forest_model.pkl"  # Path to your trained Random Forest model
with open(model_path, "rb") as file:
    model = pickle.load(file)

# Method to calculate buy/sell decision based on observations and Random Forest model
def calculate_trade_decision(observations, order_depth):
    orchids_observation = observations.conversionObservations["ORCHIDS"]
    features = {
        "TRANSPORT_FEES": orchids_observation.transportFees,
        "EXPORT_TARIFF": orchids_observation.exportTariff,
        "IMPORT_TARIFF": orchids_observation.importTariff,
        "SUNLIGHT": orchids_observation.sunlight,
        "HUMIDITY": orchids_observation.humidity
    }

    # Create a DataFrame from the features for model prediction
    data = pd.DataFrame([features])

    # Make predictions using the Random Forest model
    predicted_price = model.predict(data)[0]

    # Get bid and ask prices from observations
    bid_price = orchids_observation.bidPrice
    ask_price = orchids_observation.askPrice

    # Calculate decision based on predicted price, bid, and ask prices
    if predicted_price < bid_price:
        # Place a buy order
        quantity_to_buy = 10  # Adjust this based on your strategy and position limits
        return {"ORCHIDS": Order("ORCHIDS", bid_price, quantity_to_buy)}
    elif predicted_price > ask_price:
        # Place a sell order
        quantity_to_sell = 10  # Adjust this based on your strategy and position limits
        return {"ORCHIDS": Order("ORCHIDS", ask_price, -quantity_to_sell)}
    else:
        # No trade decision
        return {}

# Example usage in your trading algorithm's run() method
def run(state):
    observations = state.observations
    order_depth = state.orderDepth

    # Calculate trade decision
    trade_orders = calculate_trade_decision(observations, order_depth)

    # Return trade orders as a dictionary
    return trade_orders

# Example usage
if __name__ == "__main__":
    # Mocking the TradingState and OrderDepth objects for testing
    class MockObservations:
        def __init__(self, conversionObservations):
            self.conversionObservations = conversionObservations

    class MockState:
        def __init__(self, observations, orderDepth):
            self.observations = observations
            self.orderDepth = orderDepth

    orchids_conversion_observation = state.observations["ORCHIDS"]

    observations = MockObservations({"ORCHIDS": orchids_conversion_observation})
    order_depth = {"ORCHIDS": {"buy_orders": {1096.5: 5}, "sell_orders": {1098.5: -2}}}
    state = MockState(observations, order_depth)

    # Calculate trade decision based on mock state
    trade_orders = calculate_trade_decision(state.observations, state.orderDepth)
    print(trade_orders)
