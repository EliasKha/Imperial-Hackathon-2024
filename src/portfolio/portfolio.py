import pandas as pd
import numpy as np
from scipy.stats import linregress
import quantstats as qs
from skopt import gp_minimize
from skopt.space import Real, Integer
import logging
import warnings
warnings.filterwarnings("ignore", message="The objective has been evaluated at this point before.")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
pd.options.mode.copy_on_write = True

class Portfolio:
    def __init__(self, df):
        self.df = df
        self.linear_columns = []
        self.non_linear_columns = []
        self.lookback_period = len(df)

    def _optimize(self, objective, space, n_calls=100):
        return gp_minimize(objective, space, n_calls=n_calls, random_state=42)

    def optimize_lookback_period(self):
        def objective(lookback):
            lookback = lookback[0]
            temp_df = self.df[-lookback:]
            x = np.arange(lookback)
            count = 0
            for col in temp_df.columns:
                y = temp_df[col].cumsum().values
                slope, _, r_value, p_value, stderr = linregress(x, y)
                if r_value**2 > 0.8 and p_value < 0.05:
                    count += slope/stderr
            return -count 

        optimization_result = self._optimize(objective, [Integer(500, len(self.df) - 1)])
        self.lookback_period = optimization_result.x[0]

    def select_linear_strats(self):
        self.optimize_lookback_period()
        df = self.df[-self.lookback_period:]
        x = np.arange(self.lookback_period)

        for col in df.columns:
            y = df[col].cumsum().values
            _, _, r_value, p_value, _ = linregress(x, y)
            if r_value**2 > 0.8 and p_value < 0.05:
                self.linear_columns.append(col)

    def optimize_weights(self):
        def objective(weights):
            weights /= np.sum(np.abs(weights))  
            returns = np.dot(weights, self.df[self.linear_columns].values.T)
            return -qs.stats.sharpe(pd.Series(returns))  

        optimization_result = self._optimize(objective, [Real(-0.1, 0.1) for _ in range(len(self.linear_columns))])

        best_weights = optimization_result.x / np.sum(np.abs(optimization_result.x))
        
        return {self.linear_columns[i]: best_weights[i] for i in range(len(best_weights))}   
    
    def optimize_linear_combination(self):
        def objective(params):
            weights = params[:-2]
            alpha = params[-2]
            lookback = int(params[-1])
            weights /= np.sum(np.abs(weights))
            error = np.mean((np.dot(weights, self.df[-lookback:][self.non_linear_columns].values.T) - alpha * np.arange(lookback)) ** 2)
            return -abs(alpha) / error * lookback

        optimization_result = self._optimize(objective, [Real(-1, 1) for _ in range(len(self.non_linear_columns))] + [Real(-10, 10)] + [Integer(500, len(self.df) - 1)])

        best_weights = optimization_result.x[:-2] / np.sum(np.abs(optimization_result.x[:-2]))

        return {self.non_linear_columns[i]: best_weights[i] for i in range(len(best_weights))}
    
    def process(self, team_name=None, passcode=None):
        self.select_linear_strats()
        self.non_linear_columns = [col for col in self.df.columns if col not in self.linear_columns]
        
        synthetic_strat_weights = self.optimize_linear_combination()
        self.df['strat_synthetic'] = self.df[list(synthetic_strat_weights.keys())].dot(list(synthetic_strat_weights.values()))
        self.linear_columns.append('strat_synthetic')
        
        weights = self.optimize_weights()
        scaled_non_linear_weights = {key: weights['strat_synthetic'] * weight for key, weight in synthetic_strat_weights.items()}

        strat_dict = {**{key: weight for key, weight in weights.items() if key != 'strat_synthetic'},
                      **scaled_non_linear_weights}
        
        if team_name and passcode:
            strat_dict.update({'team_name': team_name, 'passcode': passcode})

        return strat_dict
