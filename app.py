import asyncio
from config import Config
from livekit_publisher import LiveKitPublisher, Resolution
from telescope_mock import TelescopeMock
from telescope_assistant import TelescopeAssistant
from livekit import api
from load_env import load_env

class Application:
    def __init__(self):
        self.config = Config()
        self.loop = asyncio.new_event_loop()

        load_env(".env")
        self.config["TOKEN"] = (
        api.AccessToken()
            .with_identity("telescope")
            .with_name("TEST TEST TEST")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room="my-room",
                )
        )
        .to_jwt()
    )

        self.publisher = LiveKitPublisher(
            self.loop, self.config["LIVEKIT_URL"], self.config["TOKEN"])
        self.telescope = TelescopeMock(self.config)
        self.telescope_assitant = TelescopeAssistant(self.telescope)

    def run(self):
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

if __name__ == '__main__':
    app = Application()
    app.run()