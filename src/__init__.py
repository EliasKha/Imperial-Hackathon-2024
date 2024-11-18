# src/__init__.py

from .scrapers.google_form_scrapping import GoogleFormAutomator
from .scrapers.slack_scrapping import SlackMonitor
from .portfolio.portfolio import Portfolio
# from .backtest.backtest import Backtester
from .data_processing.data_cleaner import DataProcessor

# Optional package metadata
__version__ = '1.0.0'
__author__ = 'Elias'
