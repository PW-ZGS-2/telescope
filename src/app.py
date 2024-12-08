import asyncio
import json
from src.config import Config
from src.utils.livekit_publisher import LiveKitPublisher, Resolution
from src.telescopes.telescope_mock import TelescopeMock
from src.assistant.telescope_assistant import TelescopeAssistant
from livekit import api
from src.utils.api import ApiClient, Location, Specifications, TelescopeData, TelescopeResponse
from src.utils.mqtt_client import MQTTClient

class Application:
    def __init__(self):
        self.config = Config()
        self.loop = asyncio.new_event_loop()
        self.api = ApiClient(self.config["SERVER_URL"])
        self.publisher = None
        self.tid = None
        self.telescope = TelescopeMock(self.config)
        self.telescope_assitant = TelescopeAssistant(self.telescope)
        self.mqtt = MQTTClient(self.config["MQTT_URL"], self.config["MQTT_PORT"], self.config["MQTT_USER"], self.config["MQTT_PASSWORD"])

    def run(self):
        tid, token = self.announce_telescope()
        if tid is None or token is None:
            print("failed to announce telescope")
            return
        self.tid = tid
        print("got connection to server, tid: ", tid)
        self.mqtt.add_subscriber(self)
        self.mqtt.connect()
        self.mqtt.subscribe(f"{tid}/#")
        self.publisher = LiveKitPublisher(
            self.loop, self.config["LIVEKIT_URL"], token)
        if self.loop.run_until_complete(self.publisher.connect()):
            print("connected to livekit")
        else:
            print("failed to connect to livekit")
            return
        
        resolution = self.telescope.get_resolution()
        self.loop.run_until_complete(self.publisher.start_streaming(
            Resolution(resolution[0], resolution[1])))
        
        self.loop.run_until_complete(self.process_frame(self.config["FRAME_PERIOD"]))

    async def process_frame(self, period):
        while True:
            start_time = asyncio.get_event_loop().time()

            frame = self.telescope_assitant.get_frame()
            self.publisher.feed_frame(frame)

            code_duration = asyncio.get_event_loop().time() - start_time
            await asyncio.sleep(period - code_duration)

    def announce_telescope(self):
        location = Location("null", "null", self.config["LATITUDE"], self.config["LONGITUDE"]) 
        specifications = Specifications(
            aperture=150,
            focal_length=1200,
            focal_ratio=8,
            weight=10,
            length=1.5,
            width=0.5,
            height=0.5,
            mount_type="EQUATORIAL",
            optical_design="Refractor"
        )
        telescope_data = TelescopeData(
            name=self.config["TELESCOPE_NAME"],
            location=location,
            specifications=specifications,
            price_per_minute=self.config["PRICE_PER_MINUTE"],
            status="FREE"
        )
        response = self.api.post_telescope(telescope_data)
        if type(response) is TelescopeResponse:
            return response.telescope_id, response.publish_token
        else:
            return None, None
        
    def mqtt_command_move(self, payload):
        if "type" not in payload or "value" not in payload:
            return
        da = 0.0
        de = 0.0
        dz = 0.0
        match payload["type"]:
            case "DX":
                da = payload["value"]
            case "DY":
                de = payload["value"]
            case "ZOOM":
                dz = payload["value"]
            case _:
                return
        self.telescope.move(da, de, dz)

    def mqtt_command_spot(self, payload):
        if not "interesting" in payload:
            return
        interesting = payload["interesting"]
        self.telescope_assitant.set_interesting(interesting)
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic.split('/')

        if len(topic) != 2 or topic[0] != self.tid:
            return
        command = topic[1]
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            return
        match command: 
            case "move":
                self.mqtt_command_move(payload)
            case "spot":
                self.mqtt_command_spot(payload)
            case _:
                return
