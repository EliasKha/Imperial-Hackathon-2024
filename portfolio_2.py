import numpy as np

class Portfolio:
    def __init__(self, df_main):
        self.df = df_main
        self.sharpe_ratios = {}
        self.normalized_sharpe = {}

    def calculate_sharpe_ratios(self):
        for column in self.df.columns:
            if column.startswith("strat_"):
                mean_return = self.df[column].mean()
                std_dev = self.df[column].std()
                if std_dev != 0:
                    self.sharpe_ratios[column] = mean_return / std_dev
                else:
                    self.sharpe_ratios[column] = np.nan 

    def normalize_sharpe_ratios(self):
        self.sharpe_ratios = {k: v for k, v in self.sharpe_ratios.items() if not np.isnan(v)}
        sorted_sharpe = sorted(self.sharpe_ratios.items(), key=lambda x: x[1], reverse=True)
        
        top_12 = sorted_sharpe[:12]
        bottom_12 = sorted_sharpe[-12:]
        
        sum_abs_sharpe_top_3 = sum(abs(value) for _, value in top_12)
        sum_abs_sharpe_bottom_3 = sum(abs(value) for _, value in bottom_12)
        abs_sum = sum_abs_sharpe_bottom_3 + sum_abs_sharpe_top_3

        for strat, sharpe in top_12:
            self.normalized_sharpe[strat] = sharpe / abs_sum
        for strat, sharpe in bottom_12:
            self.normalized_sharpe[strat] = sharpe / abs_sum

        max_normalized_sharpe = max(self.normalized_sharpe.values())
        self.normalized_sharpe = {key: value / (10 * max_normalized_sharpe) for key, value in self.normalized_sharpe.items()}

        sum_abs_normalized_sharpe = sum(abs(value) for value in self.normalized_sharpe.values())
        self.normalized_sharpe = {key: value / sum_abs_normalized_sharpe for key, value in self.normalized_sharpe.items()}

    def apply_normalized_sharpe(self):
        top_3_columns = [strat for strat, _ in sorted(self.sharpe_ratios.items(), key=lambda x: x[1], reverse=True)[:12]]
        bottom_3_columns = [strat for strat, _ in sorted(self.sharpe_ratios.items(), key=lambda x: x[1], reverse=True)[-12:]]
        
        for strat in top_3_columns:
            self.df[strat] *= self.normalized_sharpe.get(strat, 0)

        for strat in bottom_3_columns:
            self.df[strat] *= self.normalized_sharpe.get(strat, 0)

    def get_results(self):
        normalized_sharpe_rounded = {key: round(value, 7) for key, value in self.normalized_sharpe.items()}
        normalized_sharpe_rounded['team_name'] = 'Longer Term Capital Management'
        normalized_sharpe_rounded['passcode'] = 'DogCat'
        return normalized_sharpe_rounded

    def process(self):
        self.calculate_sharpe_ratios()
        self.normalize_sharpe_ratios()
        self.apply_normalized_sharpe()
        return self.get_results()