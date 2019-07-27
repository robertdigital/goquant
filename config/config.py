import os
import yaml


class TradingConfig(object):
    def __init__(self, config="development"):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self._load_config(config)

    def _load_config(self, config="development"):
        # load config
        yaml_file = self.dir_path + "/" + config + ".yaml"
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
        self.alpaca_id = self.config["alpaca"]["id"]
        self.alpaca_key = self.config["alpaca"]["key"]

        assert self.alpaca_url
        assert self.alpaca_id
        assert self.alpaca_key
