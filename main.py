from portfolio import Portfolio as portfoilio
from google_form_scrapping import GoogleFormAutomator
from slack_scrapping import SlackMonitor
import pandas as pd
 
SLACK_BOT_TOKEN = ""
CHANNEL_ID = "C080P6M4DKL"
TARGET_USER_ID = "U080GCRATP1"
EMAIL = "imperialalgothon@gmail.com"
PASSWORD = "DogCat@123"
SHOULD_SEND = False

#TODO: optimise the lookback perids
#TODO: filter the ones which are too noisy
#TODO: organise the folder
#TODO: make backtest framework

slack_monitor = SlackMonitor(SLACK_BOT_TOKEN, CHANNEL_ID, TARGET_USER_ID, strategy_func=portfoilio)
while __name__ == "__main__":

    if not (file_path:=slack_monitor.monitor_channel()):
        break
    df = pd.read_csv(file_path).drop(['strat_9', 'strat_14', 'strat_5', 'strat_4', 'strat_1', 'strat_13', 'strat_17'], axis=1).fillna(0)
    portfoilio_weights = portfoilio(df).process()
    print(portfoilio_weights)
    if SHOULD_SEND:
        google_form = GoogleFormAutomator(mytext=str(portfoilio_weights), email=EMAIL, password=PASSWORD)
        google_form.login()  
        google_form.fill_form() 
        google_form.close_browser()


