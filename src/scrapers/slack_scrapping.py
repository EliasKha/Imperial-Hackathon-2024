import requests
import re
import pandas as pd
import cryptpandas as crp
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SlackMonitor:
    def __init__(self, bot_token, channel_id, target_user_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.target_user_id = target_user_id
        self.latest_ts = None  
        self.passcode_pattern = r"the passcode is '([^']+)'"
        self.file_name_pattern = r"Data has just been released '([^']+)\.crypt'"
        self.config_path = 'data/config.json'
        self.last_path = None 

        self._initialize_config()

    def _initialize_config(self):
        if not os.path.exists(self.config_path):
            existing_files = {}
            encrypted_dir = 'data/encrypted_data/'

            if os.path.exists(encrypted_dir):
                for file in os.listdir(encrypted_dir):
                    if file.endswith('.crypt'):
                        file_name = file.rsplit('.', 1)[0]  
                        existing_files[file_name] = {"scanned": False}

            with open(self.config_path, 'w') as config_file:
                json.dump(existing_files, config_file, indent=4)
            logger.info("Initialized config file with existing encrypted files.")

    def _get_channel_messages(self):
        url = "https://slack.com/api/conversations.history"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        all_messages = []
        has_more = True
        next_cursor = None

        while has_more:
            params = {"channel": self.channel_id, "limit": 100}
            if next_cursor:
                params["cursor"] = next_cursor

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status() 
                data = response.json()
                if data.get("ok"):
                    all_messages.extend(data.get("messages", []))
                    next_cursor = data.get("response_metadata", {}).get("next_cursor")
                    has_more = bool(next_cursor)
                else:
                    logger.error(f"Slack API Error: {data.get('error', 'Unknown error')}")
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                break

        logger.info(f"Retrieved {len(all_messages)} messages from Slack channel.")
        return all_messages[::-1] 

    def _process_message(self, message):
        if message.get("user") == self.target_user_id and message.get("text"):
            passcode_match = re.search(self.passcode_pattern, message["text"])
            file_name_match = re.search(self.file_name_pattern, message["text"])

            if passcode_match and file_name_match:
                file_name = file_name_match.group(1)
                if not self.check_scanned_status(file_name):
                    self._handle_file_message(file_name, passcode_match.group(1))
                    if self.last_path:  
                        return True
        return False

    def _handle_file_message(self, file_name, passcode):
        logger.info(f"Processing file: {file_name}.crypt with passcode.")
        self._decrypt_and_save(file_name, passcode)

    def _load_config(self):
        with open(self.config_path, 'r') as config_file:
            return json.load(config_file)

    def _save_config(self, config):
        with open(self.config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

    def check_scanned_status(self, file_name):
        config = self._load_config()
        return config.get(file_name, {}).get("scanned", False)

    def update_scanned_status(self, file_name):
        config = self._load_config()
        config[file_name] = {"scanned": True}
        self._save_config(config)
        logger.info(f"Updated config for {file_name}: marked as scanned.")

    def _decrypt_and_save(self, file_name, passcode):
        file_path = f"data/decrypted_data/{file_name}.csv"
        encrypted_path = f"data/encrypted_data/{file_name}.crypt"

        if not os.path.exists(encrypted_path):
            logger.warning(f"File {encrypted_path} not found.")
            return

        try:
            decrypted_df = crp.read_encrypted(path=encrypted_path, password=passcode)
            decrypted_df.to_csv(file_path, index=False)
            logger.info(f"Decrypted data saved to {file_path}")
            self.last_path = file_path 
            self.update_scanned_status(file_name)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to decrypt or save {file_name}: {e}")

    def monitor_channel(self):

        config = self._load_config()
        unprocessed_files = [file for file, status in config.items() if not status.get("scanned")]

        if not unprocessed_files:
            logger.info("No unprocessed files found in the config.")
            return None  

        messages = self._get_channel_messages()  
        for message in messages:
            if self._process_message(message):
                return self.last_path 

        logger.info("No new CSV files processed.")
        return None 
