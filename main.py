from src import *

simulation_type = 'live'

if __name__ == "__main__":
    if simulation_type == 'live':
        simulation = Live(
            portfolio = Portfolio,
            slack_bot_token="",
            channel_id="",
            target_user_id="",
            email="",
            password="",
            should_send=False
        )
    elif simulation_type == 'backtest':
        simulation = Backtest(data_dir="data/decrypted_data", portfolio=Portfolio)
    else:
        raise ValueError("Wrong simulation type")
    simulation.run()



