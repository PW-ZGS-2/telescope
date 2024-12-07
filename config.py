import json

class Config(dict):
    def __init__(self):
        super().__init__()
        try:
            with open('config.json', 'r') as file:
                config_data = json.load(file)
        except FileNotFoundError:
            config_data = self.create_default_config()
            with open('config.json', 'w') as file:
                json.dump(config_data, file, indent=4)
        
        self.update(config_data)

    def create_default_config(self):
        default_config = {
            "LIVEKIT_URL": "http://localhost:7880",
            "TOKEN": "",
            "TELESCOPE_STREAM_WIDTH": 640,
            "TELESCOPE_STREAM_HEIGHT": 480,
            "FRAME_PERIOD": 0.2
        }
        return default_config

    def to_json(self):
        return json.dumps(self)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)