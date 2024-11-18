import pandas as pd
import numpy as np
from scipy.stats import linregress
import quantstats as qs
from skopt import gp_minimize
from skopt.space import Real
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Portfolio:
    def __init__(self, df):
        self.df = df[-2000:] 
        self.linear_columns = []
        self.non_linear_columns = []

    def select_linear_strats(self):
        for column in self.df.columns:
            x = np.arange(len(self.df))
            y = self.df[column].cumsum()
            _, _, r_value, p_value, _ = linregress(x, y)

            if r_value**2 > .8 and p_value < 0.05:
                self.linear_columns.append(column)

    def bayesian_optimization_weights(self):
        def negative_sharp_ratio(weights):
            weights /= np.sum(np.abs(weights))              
            returns = np.dot(weights, self.df[self.linear_columns].values.T)
            sharpe_ratio = qs.stats.sharpe(pd.Series(returns))
            return -sharpe_ratio  

        search_space = [Real(-0.01, 0.01) for _ in range(len(self.linear_columns))]
        optimization_result = gp_minimize(negative_sharp_ratio, search_space, n_calls=50, random_state=42)

        best_weights = optimization_result.x
        best_weights /= np.sum(np.abs(best_weights)) 
        
        weights = {self.linear_columns[i]: best_weights[i].clip(-.1,.1) for i in range(len(best_weights))}       
        return weights
    
    def bayesian_optimization_linearity_fitting(self):
        def negative_sharp_ratio(params):
            weights = params[:-1]
            alpha = params[-1]
            
            weights /= np.sum(np.abs(weights))
            
            error = 0
            for i in range(len(self.df)):
                row_error = np.dot(weights, self.df[self.non_linear_columns].iloc[i].values.T) - alpha * i
                error += row_error ** 2
                
            return error

        search_space = [Real(-0.01, 0.01) for _ in range(len(self.non_linear_columns))]
        search_space.append(Real(-100, 100))
        
        optimization_result = gp_minimize(negative_sharp_ratio, search_space, n_calls=50, random_state=42)

        best_params = optimization_result.x
        best_weights = best_params[:-1]

        best_weights /= np.sum(np.abs(best_weights))

        weights = {self.non_linear_columns[i]: best_weights[i].clip(-.1, .1) for i in range(len(best_weights))}
        return weights

    def process(self, team_name='Longer Term Capital Management', passcode='DogCat'):
        self.select_linear_strats()
       

        self.non_linear_columns = [item for item in self.df.columns if item not in self.linear_columns]
        synthetic_strat_weights = self.bayesian_optimization_linearity_fitting()

        self.df.loc[:, 'strat_synthetic'] = self.df.loc[:, list(synthetic_strat_weights.keys())].dot(list(synthetic_strat_weights.values()))   
        self.linear_columns.append('strat_synthetic')
        weights = self.bayesian_optimization_weights()

        scaled_non_linear_weights = {key: weights['strat_synthetic'] * weight for key, weight in synthetic_strat_weights.items()}
        strat_dict = {key: weight for key, weight in weights.items()} 
        strat_dict = {**{key: weight for key, weight in weights.items() if key != 'strat_synthetic'}, **scaled_non_linear_weights}
        strat_dict['team_name'] = team_name
        strat_dict['passcode'] = passcode
        
        return strat_dict