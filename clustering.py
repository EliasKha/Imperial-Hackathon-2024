import pandas as pd
import numpy as np
from scipy.stats import linregress
import quantstats as qs
from skopt import gp_minimize
from skopt.space import Real

class Strategy:
    def __init__(self, data_path, train_size=.8, r_squared_threshold=0.8):
        self.df = pd.read_csv(data_path).drop(['strat_9', 'strat_14', 'strat_5', 'strat_4','strat_1','strat_13','strat_17','Unnamed: 0'], axis=1).fillna(0)
        self.results = {}
        self.selected_columns = []
        self.strat_slope_map = {}
        self.train_size = train_size
        self.r_squared_threshold = r_squared_threshold
        self.train_df, self.test_df = self.split_train_test()

        self.scaled_strat_slope_map = self.select_columns_with_high_r_squared()
        self.adjusted_weights_dict = self.bayesian_optimization_adjust_weights()

    def split_train_test(self):
        split_index = int(len(self.df) * self.train_size)
        train_df = self.df.iloc[:split_index]
        test_df = self.df.iloc[split_index:]
        return train_df, test_df

    def select_columns_with_high_r_squared(self):
        for column in self.train_df.columns:
            x = np.arange(len(self.train_df))
            y = self.train_df[column].cumsum()
            slope, intercept, r_value, p_value, std_err = linregress(x, y)

            self.results[column] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'std_err': std_err
            }

            if r_value**2 > self.r_squared_threshold and p_value < 0.05:
                self.selected_columns.append(column)

        for column in self.selected_columns:
            slope_over_std = self.results[column]['slope'] / self.results[column]['std_err']
            self.strat_slope_map[column] = slope_over_std

        total_sum = sum(self.strat_slope_map.values())
        scaled_strat_slope_map = {strat: slope / total_sum for strat, slope in self.strat_slope_map.items()}

        return scaled_strat_slope_map

    def bayesian_optimization_adjust_weights(self):
        def objective_function(weights):
            weights /= np.sum(np.abs(weights))  
            adjusted_weights = {list(self.scaled_strat_slope_map.keys())[i]: weights[i] for i in range(len(weights))}
            
            returns = np.dot(weights, self.test_df[list(self.scaled_strat_slope_map.keys())].values.T)
            sharpe_ratio = qs.stats.sharpe(pd.Series(returns))
            return -sharpe_ratio  

        search_space = [Real(-0.01, 0.01) for _ in range(len(self.scaled_strat_slope_map))]

        optimization_result = gp_minimize(objective_function, search_space, n_calls=50, random_state=42)

        best_weights = optimization_result.x
        best_weights /= np.sum(np.abs(best_weights)) 
        
        adjusted_weights_dict = {list(self.scaled_strat_slope_map.keys())[i]: best_weights[i] for i in range(len(best_weights))}
        
        return adjusted_weights_dict

    def calculate_sharpe_ratio(self):
        strat_names = list(self.scaled_strat_slope_map.keys())
        adjusted_weights = np.array(list(self.adjusted_weights_dict.values()))
        
        returns = np.dot(adjusted_weights, self.test_df[strat_names].values.T)
        sharpe_ratio = qs.stats.sharpe(pd.Series(returns))

        return sharpe_ratio

    def generate_team_info_from_scaled_weights(self, scaled_weights, team_name, passcode):
        strat_dict = {key: weight for key, weight in scaled_weights.items()}
        strat_dict['team_name'] = team_name
        strat_dict['passcode'] = passcode
        return strat_dict


# Usage
analyzer = Strategy('data/decrypted_data/release_5723.csv')
sharpe_ratio = analyzer.calculate_sharpe_ratio()

output = analyzer.generate_team_info_from_scaled_weights(analyzer.adjusted_weights_dict, 'Longer Term Capital Management', 'DogCat')
print("Sharpe Ratio:", sharpe_ratio)
print(output)

import matplotlib.pyplot as plt

def plot_weighted_combination(self):
    # Get the adjusted weights and strategies' names
    strat_names = list(self.scaled_strat_slope_map.keys())
    adjusted_weights = np.array(list(self.adjusted_weights_dict.values()))

    # Calculate the weighted returns for each strategy
    weighted_returns = np.dot(adjusted_weights, self.test_df[strat_names].values.T)

    # Calculate cumulative returns
    cumulative_returns = np.cumsum(weighted_returns)

    # Plot the weighted combination of strategies
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_returns, label='Weighted Combination of Strategies', color='blue')
    plt.title('Cumulative Returns of the Weighted Combination of Strategies')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)
    plt.show()

# Add the function to your Strategy class
Strategy.plot_weighted_combination = plot_weighted_combination

# Usage
analyzer.plot_weighted_combination()
