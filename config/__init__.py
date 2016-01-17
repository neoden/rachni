import os
import json
import inspect


class Config(dict):
    def __init__(self, d=None):
        if d:
            self.update(d)

    @classmethod
    def from_dict(cls, d):
        return cls(d)

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            return cls(json.load(f))

    @classmethod
    def from_json(cls, data):
        return cls(json.loads(data))

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    @property
    def __dict__(self):
        return self    


class App:
    def __init__(self, instance_path=None, configs=None, default_config=None):
        _, filename, _, _, _, _ = inspect.getouterframes(inspect.currentframe())[1]
        self.root_path = os.path.dirname(os.path.abspath(filename))
        self.instance_path = instance_path or self.root_path

        self.config = default_config or Config()
        config_set = {'config.json', 'config.local.json'}
        if configs:
            config_set.update(configs)
        for config_name in config_set:
            path = self._config_path(config_name)
            if path:
                self.config.update(Config.from_file(path))

    def _config_path(self, config):
        if os.path.isabs(config):
            return config

        path = os.path.join(self.root_path, config)
        if os.path.isfile(path):
            return path

        path = os.path.join(self.instance_path, config)
        if os.path.isfile(path):
            return path

    def run(self):
        raise NotImplemented
