from portfolio_1 import Portfolio as portfoilio_1
from portfolio_2 import Portfolio as portfoilio_2
from google_form_scrapping import GoogleFormAutomator
from slack_scrapping import SlackMonitor
 
SLACK_BOT_TOKEN = ""
CHANNEL_ID = "C080P6M4DKL"
TARGET_USER_ID = "U080GCRATP1"
slack_monitor = SlackMonitor(SLACK_BOT_TOKEN, CHANNEL_ID, TARGET_USER_ID, strategy_func=portfoilio_1)

while __name__ == "__main__":
    slack_monitor.monitor_channel()

    if portfolio := slack_monitor.output:
        google_form = GoogleFormAutomator(str(portfolio))
        google_form.login()  
        google_form.fill_form() 


