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
            "SERVER_URL": "http://localhost:8000",
            "LIVEKIT_URL": "ws://localhost:7880",
            "MQTT_URL": "mqtt://localhost",
            "MQTT_PORT": 1883,
            "MQTT_USER": "mqtt",
            "MQTT_PASSWORD": "",
            "TELESCOPE_NAME": "Teleskop Maciuś",
            "FRAME_PERIOD": 0.01,
            "LATITUDE": 50.0000,
            "LONGITUDE": 20.0000,
            "MAX_ZOOM": 5,
            "PRICE_PER_MINUTE": 1.0,
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