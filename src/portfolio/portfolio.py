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

    def _optimize(self, objective, space, n_calls=50):
        return gp_minimize(objective, space, n_calls=n_calls, random_state=42, n_jobs=-1, acq_func='PI', n_initial_points=20)
    
    def optimize_linear_combination(self):
        def objective(params):
            weights = params[:-1]
            lookback = params[-1]
            weights /= np.sum(np.abs(weights))
            portfolio = np.dot(weights, self.df[-lookback:].values.T)
            sharp_ratio = qs.stats.sharpe(pd.DataFrame(portfolio)).values[0]
            x = np.arange(lookback)
            slope, _, _, _, stderr = linregress(x, portfolio)
            return - ( sharp_ratio + .4 * slope / stderr )

        optimization_result = self._optimize(objective, [Real(-1, 1) for _ in range(len(self.df.columns))] + [Integer(500, 2000)])

        best_weights = optimization_result.x[:-2] / np.sum(np.abs(optimization_result.x[:-2]))

        return {self.df.columns[i]: best_weights[i] for i in range(len(best_weights))}
    
    def process(self, team_name=None, passcode=None):
        
        strat_dict = self.optimize_linear_combination()
        
        if team_name and passcode:
            strat_dict.update({'team_name': team_name, 'passcode': passcode})

        return strat_dict
