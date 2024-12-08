import asyncio
from src.config import Config
from src.utils.livekit_publisher import LiveKitPublisher, Resolution
from src.telescopes.telescope_mock import TelescopeMock
from src.assistant.telescope_assistant import TelescopeAssistant
from livekit import api
from src.utils.api import ApiClient, Location, Specifications, TelescopeData

class Application:
    def __init__(self):
        self.config = Config()
        self.loop = asyncio.new_event_loop()
        self.api = ApiClient(self.config["SERVER_URL"])
        self.publisher = None
        self.telescope = TelescopeMock(self.config)
        self.telescope_assitant = TelescopeAssistant(self.telescope)

    def run(self):
        token = self.announce_telescope()
        if token is None:
            print("failed to announce telescope")
            return
        print("got token")
        LiveKitPublisher(
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
        if not "error" in response:
            return response.publish_token
        else:
            return None