import json

class Config:
    # Config is always the same instance.
    alert_channel:int
    register_channel:int

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        for key, value in self.get_config().items():
            setattr(self, key, value)

    def get_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config

    def reload_config(self):
        for key, value in self.get_config().items():
            setattr(self, key, value)