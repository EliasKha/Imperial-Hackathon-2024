import requests
import time
import re
import pandas as pd
import cryptpandas as crp
import json


class SlackMonitor:
    def __init__(self, bot_token, channel_id, target_user_id, strategy_func=None):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.target_user_id = target_user_id
        self.latest_ts = None  
        self.passcode_pattern = r"the passcode is '([^']+)'"
        self.file_name_pattern = r"Data has just been released '([^']+)\.crypt'"
        self.strategy_func = strategy_func
        self.output = None 

    def _get_channel_messages(self):
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
        user_id = message.get("user")
        text = message.get("text")
        
        if user_id == self.target_user_id and text:
            passcode_match = re.search(self.passcode_pattern, text)
            file_name_match = re.search(self.file_name_pattern, text)
            
            if passcode_match and file_name_match:
                passcode = passcode_match.group(1)
                file_name = file_name_match.group(1)
                self._handle_file_message(file_name, passcode)

    def _handle_file_message(self, file_name, passcode):
        print(f"Now scanning Filename: {file_name}, {passcode}")
        self._new_env(file_name, passcode)

    def check_scanned_status(self, filepath):
        with open('data/config.json', 'r') as config_file:
            config = json.load(config_file)

        if filepath not in config:
            print(f"{filepath} not found in configuration.")
            return False  # Return False to indicate it's not scanned
        return config[filepath].get("scanned", False)

    def update_scanned_status(self, filepath):
        with open('data/config.json', 'r') as config_file:
            config = json.load(config_file)

        if filepath not in config:
            file_name = filepath.split('/')[-1].split('.')[0]
            file_number = file_name.split('_')[1]
            config[filepath] = {"scanned": True, "file_name": file_name, "file_number": file_number}
            print(f"{filepath} not found in configuration. Added with scanned: True")
        else:
            config[filepath]["scanned"] = True

        with open('data/config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

    def _new_env(self, file_name, passcode):
        file_path = f"data/decrypted_data/{file_name}.csv"
        if self.check_scanned_status(file_path):
            return
        
        decrypted_df = crp.read_encrypted(path=f'data/encrypted_data/{file_name}.crypt', password=passcode)
        decrypted_df.to_csv(file_path)
        df = pd.read_csv(file_path).drop(['Unnamed: 0', 'strat_9', 'strat_14', 'strat_5', 'strat_4', 'strat_1', 'strat_13', 'strat_17'], axis=1).fillna(0)

        if self.strategy_func:
            self.output = self.strategy_func(df).process()
            print(self.output)

        self.update_scanned_status(file_path)

    def monitor_channel(self):
        self.output = None
        messages = self._get_channel_messages()
        for message in reversed(messages):
            self._process_message(message)


