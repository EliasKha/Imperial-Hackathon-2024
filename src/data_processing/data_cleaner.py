import numpy as np
import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
    
    def replace_outliers_with_zero(self):
        Q1 = self.df.quantile(0.001)
        Q3 = self.df.quantile(0.999)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        self.df[self.df.select_dtypes(include=[np.number]).columns] = self.df.select_dtypes(include=[np.number]).apply(
            lambda col: np.where((col < lower_bound[col.name]) | (col > upper_bound[col.name]), 0, col)
        )
    
    def check_column_means(self):
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if not (-0.5 <= self.df[col].mean() <= 0.5):
                self.df = self.df.drop(col, axis=1)
    
    def fill_nan_values(self, method='ffill', value=None):
        if method == 'ffill':
            self.df = self.df.fillna(method='ffill')
        elif method == 'bfill':
            self.df = self.df.fillna(method='bfill')
        elif method == 'constant' and value is not None:
            self.df = self.df.fillna(value)
        else:
            print("Invalid method or value for filling NaNs.")
    
    def process(self):
        self.replace_outliers_with_zero()
        self.check_column_means()
        return self.df
