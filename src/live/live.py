
import os
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src import * 


class Live:
    def __init__(self, portfolio, slack_bot_token, channel_id, target_user_id, email, password, should_send=True):
        self.slack_bot_token = slack_bot_token
        self.channel_id = channel_id
        self.target_user_id = target_user_id
        self.email = email
        self.password = password
        self.should_send = should_send
        self.slack_monitor = SlackMonitor(self.slack_bot_token, self.channel_id, self.target_user_id)
        self.portfolio = portfolio
    
    def run(self):
        while True:
            file_path = self.slack_monitor.monitor_channel()
            if not file_path:
                break
            
            # Process the data
            df = DataProcessor(file_path).process()
            portfolio_weights = self.portfolio(df).process(team_name='Longer Term Capital Management', passcode='DogCat')
            
            # Send the portfolio weights via Google Form if necessary
            if self.should_send:
                google_form = GoogleFormAutomator(mytext=str(portfolio_weights), email=self.email, password=self.password)
                google_form.login()  
                google_form.fill_form() 
                google_form.close_browser()