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
            "LIVEKIT_URL": "ws://localhost:7880",
            "TOKEN": "",
            "FRAME_PERIOD": 0.01,
            "LATITUDE": 50.0000,
            "LONGITUDE": 20.0000,
            "MAX_ZOOM": 5,
            "TELESCOPE_FOVX": 1.6,
            "TELESCOPE_FOVY": 0.9,
            "TELESCOPE_STREAM_WIDTH": 1920,
            "TELESCOPE_STREAM_HEIGHT": 1080
        }
        return default_config

    def to_json(self):
        return json.dumps(self)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)