from ..telescopes.telescope import Telescope

import numpy as np
import math
import cv2
from livekit import rtc
from src.utils.noise_generator import NoiseGenerator
from src.utils.celestial_data_loader import CelestialDataLoader


class TelescopeAssistant():
    def __init__(self, telescope: Telescope):
        self.telescope = telescope
        self.celestial_data_loader = CelestialDataLoader(telescope.get_location())
        self.celestials = self.celestial_data_loader.parse_data()
        self.interesting = []

    def set_interesting(self, interesting : list[str]):
        self.interesting = interesting

    def spot_celestial(self,canvas, x, y):
        cv2.circle(canvas, (x, y), 80, (0, 255, 0), 10)

    def circular_diff(self, base_angle, target_angle):
        diff = target_angle - base_angle
        if diff > math.pi:
            diff -= 2 * math.pi
        if diff < -math.pi:
            diff += 2 * math.pi
        return diff

    def get_frame(self):
        resolution = self.telescope.get_resolution()
        fov = self.telescope.get_fov()
        orientation = self.telescope.get_orientation()
        canvas = self.telescope.get_frame()

        for celestial in self.celestials:
            if len(self.interesting) > 0 and not celestial.object_name in self.interesting:
                continue
            relative_azimuth = self.circular_diff(orientation[0], celestial.gha)
            relative_elevation = celestial.hc - orientation[1]
            if abs(relative_azimuth) > fov[0] / 2 or abs(relative_elevation) > fov[1] / 2:
                continue
            x = int(resolution[0] * (0.5 + relative_azimuth / fov[0]))
            y = int(resolution[1] * (0.5 - relative_elevation / fov[1]))
            self.spot_celestial(canvas, x, y)
          
        argb_frame = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)
        argb_frame[:, :, 3] = 255
        argb_frame = argb_frame.tobytes()
        return rtc.VideoFrame(resolution[0], resolution[1], rtc.VideoBufferType.RGBA, argb_frame)

    