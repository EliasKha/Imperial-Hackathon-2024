import os
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.data_processing.data_cleaner import DataProcessor 


class Backtest:
    def __init__(self, data_dir="data/decrypted_data", portfolio=None):
        self.data_dir = data_dir
        self.portfolio = portfolio
        self.all_returns = pd.DataFrame()

    def _get_ordered_files(self):
        files = [f for f in os.listdir(self.data_dir) if f.startswith("release_") and f.endswith(".csv")]
        files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        return files

    def _apply_weights(self, df, weights):
        for col in df.columns:
            if col not in weights:
                weights[col] = 0.0

        portfolio_returns = df[list(weights.keys())].dot(list(weights.values()))
        return portfolio_returns

    def run(self):
        files = self._get_ordered_files()

        if not files:
            return self.all_returns

        previous_data = None
        try:
            for i, file_name in enumerate(files):
                file_path = os.path.join(self.data_dir, file_name)
                current_data = DataProcessor(file_path).process() 

                if i != 0:
                    new_data = current_data.merge(previous_data, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1).fillna(0)
                    old_data = current_data.merge(previous_data, how='inner')
                    weights = self.portfolio(df=old_data).process()
                    returns = self._apply_weights(new_data, weights)
                    returns_df = pd.DataFrame(returns, columns=['returns'])
                    self.all_returns = pd.concat([self.all_returns, returns_df], ignore_index=True)

                previous_data = current_data

        except KeyboardInterrupt:
            return self.all_returns

        return self.all_returns
