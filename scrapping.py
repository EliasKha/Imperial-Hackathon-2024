import requests
import time
import re
import pandas as pd
import cryptpandas as crp

class SlackMonitor:
    def __init__(self, bot_token, channel_id, target_user_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.target_user_id = target_user_id
        self.latest_ts = None
        self.passcode_pattern = r"the passcode is '([^']+)'"
        self.file_name_pattern = r"Data has just been released '([^']+)\.crypt'"

    def _get_channel_messages(self):
        """Fetch messages from a Slack channel."""
        url = "https://slack.com/api/conversations.history"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        params = {
            "channel": self.channel_id,
            "limit": 100,
        }
        if self.latest_ts:
            params["oldest"] = self.latest_ts
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                return data["messages"]
            else:
                print(f"Slack API Error: {data['error']}")
        else:
            print(f"HTTP Error: {response.status_code}")
        return []

    def _process_message(self, message):
        """Process a single Slack message."""
        user_id = message.get("user")
        text = message.get("text")
        ts = message.get("ts")
        if user_id == self.target_user_id and text:
            passcode_match = re.search(self.passcode_pattern, text)
            file_name_match = re.search(self.file_name_pattern, text)
            if passcode_match and file_name_match:
                passcode = passcode_match.group(1)
                file_name = file_name_match.group(1)
                print(f"Passcode detected: {passcode}")
                print(f"File name detected: {file_name}")
                self._execute_custom_code(text, ts, passcode, file_name)
                self._new_env(file_name, passcode)
        self.latest_ts = ts

    def _execute_custom_code(self, message, ts, passcode, file_name):
        """Custom logic triggered by a specific message."""
        print(f'Custom code executed for message: "{message}" - {ts}')
        print(f"Extracted passcode: {passcode}")
        print(f"Extracted file name: {file_name}")

    def _new_env(self, file_name, passcode):
        """Decrypt and process the file."""
        decrypted_df = crp.read_encrypted(path=f'data/encrypted_data/{file_name}.crypt', password=passcode)
        decrypted_df.to_csv(f'data/decrypted_data/{file_name}.csv')
        print(f"Data from {file_name} processed successfully.\n")

    def monitor_channel(self, poll_interval=5):
        """Continuously poll the channel for new messages."""
        while True:
            messages = self._get_channel_messages()
            for message in reversed(messages):
                self._process_message(message)
            time.sleep(poll_interval)

if __name__ == "__main__":
    SLACK_BOT_TOKEN = "xoxb-8020284472341-8040286707987-rLUD0Hkxc2UQlklZRUAN6wmf"
    CHANNEL_ID = "C080P6M4DKL"
    TARGET_USER_ID = "U080GCRATP1"
    
    slack_monitor = SlackMonitor(SLACK_BOT_TOKEN, CHANNEL_ID, TARGET_USER_ID)
    slack_monitor.monitor_channel()
