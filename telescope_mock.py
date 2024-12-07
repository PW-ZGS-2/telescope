import numpy as np
from livekit import rtc

class TelescopeMock:
    def __init__(self, config):
        self.config = config
        
    def get_frame(self):
        argb_frame = bytearray(self.config["STREAM_WIDTH"] * self.config["STREAM_HEIGHT"] * 4)
        arr = np.frombuffer(argb_frame, dtype=np.uint8)
        arr[0::4] = 255  # Set alpha channel to 255
        arr[1::4] = np.random.randint(0, 256, size=self.config["STREAM_WIDTH"] * self.config["STREAM_HEIGHT"], dtype=np.uint8)
        arr[2::4] = np.random.randint(0, 256, size=self.config["STREAM_WIDTH"] * self.config["STREAM_HEIGHT"], dtype=np.uint8)
        arr[3::4] = np.random.randint(0, 256, size=self.config["STREAM_WIDTH"] * self.config["STREAM_HEIGHT"], dtype=np.uint8)
        return rtc.VideoFrame(self.config["STREAM_WIDTH"], self.config["STREAM_HEIGHT"], rtc.VideoBufferType.ARGB, argb_frame)

        
