import pandas as pd
import numpy as np
import jsonpickle
from typing import Dict, List
import math
import statistics
from datamodel import OrderDepth, Observation, TradingState, Order

class RandomForestRegressor:
    def __init__(self, n_estimators=100, max_depth=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.trees = []

    def fit(self, X, y):
        for _ in range(self.n_estimators):
            indices = np.random.choice(len(X), size=len(X), replace=True)
            X_bootstrap = X[indices]
            y_bootstrap = y[indices]
            tree = DecisionTreeRegressor(max_depth=self.max_depth)
            tree.fit(X_bootstrap, y_bootstrap)
            self.trees.append(tree)

    def predict(self, X):
        predictions = np.zeros(len(X))
        for tree in self.trees:
            predictions += tree.predict(X)
        return predictions / self.n_estimators

# Define the DecisionTreeRegressor class
class DecisionTreeRegressor:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self.build_tree(X, y, depth=0)

    def build_tree(self, X, y, depth):
        if depth == self.max_depth or len(set(y)) == 1:
            return statistics.mean(y)
        else:
            best_feature, best_split_value = self.find_best_split(X, y)
            left_indices = X[:, best_feature] <= best_split_value
            right_indices = X[:, best_feature] > best_split_value
            left_tree = self.build_tree(X[left_indices], y[left_indices], depth + 1)
            right_tree = self.build_tree(X[right_indices], y[right_indices], depth + 1)
            return {'feature_index': best_feature, 'split_value': best_split_value, 'left': left_tree, 'right': right_tree}

    def find_best_split(self, X, y):
        best_feature = None
        best_split_value = None
        best_mse = float('inf')
        for feature_index in range(X.shape[1]):
            unique_values = np.unique(X[:, feature_index])
            for value in unique_values:
                left_indices = X[:, feature_index] <= value
                right_indices = X[:, feature_index] > value
                if len(y[left_indices]) > 0 and len(y[right_indices]) > 0:
                    left_mean = statistics.mean(y[left_indices])
                    right_mean = statistics.mean(y[right_indices])
                    mse = self.calculate_mse(y[left_indices], left_mean) + self.calculate_mse(y[right_indices], right_mean)
                    if mse < best_mse:
                        best_mse = mse
                        best_feature = feature_index
                        best_split_value = value
        return best_feature, best_split_value

    def calculate_mse(self, y, mean):
        return sum((y - mean) ** 2) / len(y)

    def predict(self, X):
        predictions = []
        for sample in X:
            node = self.tree
            while isinstance(node, dict):
                if sample[node['feature_index']] <= node['split_value']:
                    node = node['left']
                else:
                    node = node['right']
            predictions.append(node)
        return np.array(predictions)

class Trader:  
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.trees = []
        
    def calculate_action(self, observation: Observation):
        features = {
            'TRANSPORT_FEES': observation['ORCHIDS']["transportFees"],
            'EXPORT_TARIFF': observation['ORCHIDS']["exportTariff"],
            'IMPORT_TARIFF': observation.conversionObservations['ORCHIDS']['importTariff'],
            'SUNLIGHT': observation.conversionObservations['ORCHIDS']["sunlight"],
            'HUMIDITY': observation.conversionObservations['ORCHIDS']["humidity"]
        }
        data = pd.DataFrame(features, index=[0])

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        