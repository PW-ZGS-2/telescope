import asyncio
import numpy as np
from livekit import api, rtc
import time

class Resolution:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class LiveKitPublisher:
    def __init__(self, loop, url, token):
        self.loop = loop
        self.url = url
        self.token = token
        self.room = rtc.Room(loop=self.loop)
        self.source = None

    async def connect(self):
        try:
            await self.room.connect(self.url, self.token)
            print ("TOKEN %s", self.token)
            print("connected to room %s", self.room.name)
            return True
        except rtc.ConnectError as e:
            print("failed to connect to the room: %s", e)
            return False

    async def start_streaming(self, resolution : Resolution):
        self.source = rtc.VideoSource(resolution.width, resolution.height)
        track = rtc.LocalVideoTrack.create_video_track("telescope", self.source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_CAMERA
        options.video_codec = rtc.VideoCodec.VP8
        publication = await self.room.local_participant.publish_track(track, options)
        print("published track %s", publication.sid)

    def feed_frame(self, frame: rtc.VideoFrame):
        if self.source is None:
            return
        self.source.capture_frame(frame, timestamp_us=time.time_ns() // 1000)
        
    async def close(self):
        await self.room.disconnect()
        self.loop.stop()