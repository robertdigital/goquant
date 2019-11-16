import os
import yaml


class TradingConfig(object):
    def __init__(self, config=None):
        if config is None:
            config = os.environ.get('RUNTIME_ENV', 'development')
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self._load_config(config)

    def _load_config(self, config="development"):
        # load config
        yaml_file = "{}/{}.yaml".format(self.dir_path, config)
        priv_yaml_file = "{}/priv.yaml".format(self.dir_path)

        print("load config: {}".format(yaml_file))
        with open(yaml_file, 'r') as f:
            self.config = yaml.safe_load(f)

        print("load priv config: {}".format(priv_yaml_file))
        with open(priv_yaml_file, 'r') as f:
            self.priv_config = yaml.safe_load(f)

        self.logging_level = self.config["dev"]["logging-level"]
        self.ib_ip = self.config["ib"]["ip"]
        self.ib_port = self.config["ib"]["port"]
        self.ib_clientId = self.config["ib"]["clientId"]

        assert self.logging_level
        assert self.ib_ip
        assert self.ib_port

        self.alpaca_url = self.config["alpaca"]["url"]
        self.alpaca_id = self.priv_config["alpaca"]["id"]
        self.alpaca_key = self.priv_config["alpaca"]["key"]

        assert self.alpaca_url
        assert self.alpaca_id   # it's in priv.yaml
        assert self.alpaca_key  # it's in priv.yaml

        # data
        self.csv_folder = self.config["data"]["csv_folder"]

        assert self.csv_folder

        print("env cfg: {}\npriv cfg: {}".format(self.config, self.priv_config))
