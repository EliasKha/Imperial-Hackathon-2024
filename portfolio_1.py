import pandas as pd
import numpy as np
from scipy.stats import linregress
import quantstats as qs
from skopt import gp_minimize
from skopt.space import Real

class Portfolio:
    def __init__(self, df, train_size=.8, r_squared_threshold=.8):
        self.df = df
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

    def sum_abs_values_with_strat(self, data):
        strat_values = [abs(value) for key, value in data.items() if 'strat_' in key]
        total = sum(strat_values)
        all_within_limit = all(value <= 0.1 for value in strat_values)

        if total != 1:
            print(f"Sum of abs values is {total}")

        if not all_within_limit:
            print("Not all values with keys containing 'strat_' are within the limit (<= 0.1).")

    def bayesian_optimization_adjust_weights(self):
        def objective_function(weights):
            weights /= np.sum(np.abs(weights))              
            returns = np.dot(weights, self.test_df[list(self.scaled_strat_slope_map.keys())].values.T)
            sharpe_ratio = qs.stats.sharpe(pd.Series(returns))
            return -sharpe_ratio  

        search_space = [Real(-0.01, 0.01) for _ in range(len(self.scaled_strat_slope_map))]

        optimization_result = gp_minimize(objective_function, search_space, n_calls=50, random_state=42)

        best_weights = optimization_result.x
        best_weights /= np.sum(np.abs(best_weights)) 
        
        adjusted_weights_dict = {list(self.scaled_strat_slope_map.keys())[i]: best_weights[i] for i in range(len(best_weights))}
        
        self.sum_abs_values_with_strat(adjusted_weights_dict)

        return adjusted_weights_dict

    def calculate_sharpe_ratio(self):
        strat_names = list(self.scaled_strat_slope_map.keys())
        adjusted_weights = np.array(list(self.adjusted_weights_dict.values()))
        weighted_returns = np.dot(self.test_df[strat_names].values, adjusted_weights)
        returns_series = pd.Series(weighted_returns, index=self.test_df.index)
        returns_series = returns_series.dropna()
        sharpe_ratio = qs.stats.sharpe(returns_series)
        return sharpe_ratio


    def process(self, team_name='Longer Term Capital Management', passcode='DogCat'):
        self.train_df, self.test_df = self.split_train_test()
        self.scaled_strat_slope_map = self.select_columns_with_high_r_squared()
        self.adjusted_weights_dict = self.bayesian_optimization_adjust_weights()

        strat_dict = {key: weight for key, weight in self.adjusted_weights_dict.items()}
        strat_dict['team_name'] = team_name
        strat_dict['passcode'] = passcode
        
        return strat_dict

