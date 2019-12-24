import os
import yaml
from os.path import expanduser

from entity.constants import ENV_TEST_LEVEL, TEST_LEVEL_INTEGRATION


class TradingConfig(object):
    def __init__(self, config=None):
        if config is None:
            config = os.environ.get('RUNTIME_ENV', 'development')
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self._load_config(config)

    def _load_config(self, env="development"):
        # load config
        yaml_file = "{}/{}.yaml".format(self.dir_path, env)
        priv_yaml_file = "{}/priv.yaml".format(self.dir_path)

        print("load config: {}".format(yaml_file))
        with open(yaml_file, 'r') as f:
            self.config = yaml.safe_load(f)

        self.logging_level = self.config["dev"]["logging-level"]
        self.ib_ip = self.config["ib"]["ip"]
        self.ib_port = self.config["ib"]["port"]
        self.ib_clientId = self.config["ib"]["clientId"]

        assert self.logging_level
        assert self.ib_ip
        assert self.ib_port

        self.alpaca_url = self.config["alpaca"]["url"]
        assert self.alpaca_url

        # data
        base_folder = self.config["data"]["base_folder"]
        csv_folder_name = self.config["data"]["csv_folder"]
        self.csv_data_path = "{}/{}/{}".format(expanduser("~"), base_folder, csv_folder_name)
        if not os.path.exists(self.csv_data_path):
            os.makedirs(self.csv_data_path)

        assert self.csv_data_path

        # private data
        if os.getenv(ENV_TEST_LEVEL) == TEST_LEVEL_INTEGRATION or env != "test":
            print("load priv config: {}".format(yaml_file))
            with open(priv_yaml_file, 'r') as f:
                self.priv_config = yaml.safe_load(f)

            self.alpaca_id = self.priv_config["alpaca"]["id"]
            self.alpaca_key = self.priv_config["alpaca"]["key"]
            self.binance_api_key = self.priv_config["binance"]["key"]
            self.binance_secret_key = self.priv_config["binance"]["secret"]
        else:
            self.alpaca_id = self.config["alpaca"]["id"]
            self.alpaca_key = self.config["alpaca"]["key"]
            self.binance_api_key = self.config["binance"]["key"]
            self.binance_secret_key = self.config["binance"]["secret"]

        assert self.alpaca_id  # it's in priv.yaml
        assert self.alpaca_key  # it's in priv.yaml
