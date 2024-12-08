from src.telescopes.telescope import Telescope

import numpy as np
import math
import cv2
from src.utils.noise_generator import NoiseGenerator
from src.utils.celestial_data_loader import CelestialDataLoader
from src.utils.resource_loader import ResourceLoader

class TelescopeMock(Telescope):
    def __init__(self, config):
        self.SKY_COLOR = (25, 25, 112)
        self.LAND_COLOR = (0, 100, 0)
        self.STAR_COLOR = (255, 255, 224)
        self.STAR_SIZE = 30

        self.resource_loader = ResourceLoader(2*self.STAR_SIZE)

        self.stream_width = config["TELESCOPE_STREAM_WIDTH"]
        self.stream_height = config["TELESCOPE_STREAM_HEIGHT"]
        self.base_fovx = config["TELESCOPE_FOVX"]
        self.base_fovy = config["TELESCOPE_FOVY"]
        self.latitute = config["LATITUDE"]
        self.longitude = config["LONGITUDE"]
        self.max_zoom = config["MAX_ZOOM"]

        self.celestial_data_loader = CelestialDataLoader((self.latitute, self.longitude))
        self.celestial_data_loader.fetch_data()
        self.celestials = self.celestial_data_loader.parse_data()
    
        self.azimuth = 0
        self.elevation = math.pi / 6
        self.set_zoom(1)

        self.empty_sky = self.draw_empty_sky()
        self.frame = self.draw()

    def get_resolution(self):
        return (self.stream_width, self.stream_height)
    
    def get_fov(self):
        return (self.fovx, self.fovy)
    
    def get_orientation(self):
        return (self.azimuth, self.elevation)
    
    def get_location(self):
        return (self.latitute, self.longitude)
    
    def set_orientation(self, azimuth, elevation):
        self.azimuth = azimuth
        self.elevation = elevation
        self.frame = self.draw()

    def get_frame(self):
        return self.frame
    
    def set_zoom(self, zoom):
        self.zoom = max(min(zoom, self.max_zoom), 1)
        self.fovx = self.base_fovx / self.zoom
        self.fovy = self.base_fovy / self.zoom
    
    def move(self, da, de, dz):
        self.set_zoom(self.zoom + dz)
        azimuth = self.azimuth + da
        if azimuth > math.pi:
            azimuth -= 2 * math.pi
        if azimuth < -math.pi:
            azimuth += 2 * math.pi
        elevation = max(min(self.elevation + de, math.pi / 2 - self.fovy / 2), 0)
        self.set_orientation(azimuth, elevation)

    def draw_empty_sky(self):
        canvas = np.full((self.stream_height, self.stream_width, 3), fill_value=self.SKY_COLOR, dtype=np.uint8)
        # noise = NoiseGenerator(self.stream_width, self.stream_height, scale=300.0).generate_perlin_noise()
        # noise = (noise * 10).astype(np.uint8)  
        # canvas[:, :, 0] += noise
        # canvas[:, :, 1] += noise
        # canvas[:, :, 2] += 5*noise
        return canvas
    
    def draw_terrain(self):
        if self.elevation > self.fovy / 2:
            return
        land_height = self.stream_height * (1 - (2 * self.elevation / self.fovy))
        amplitude = self.stream_width / 20
        for w in range(self.stream_width):
            az = self.azimuth + w * self.fovx / self.stream_width
            self.canvas[int(land_height + amplitude * math.sin(2 * az)):, w] = self.LAND_COLOR

    def circular_diff(self, base_angle, target_angle):
        diff = target_angle - base_angle
        if diff > math.pi:
            diff -= 2 * math.pi
        if diff < -math.pi:
            diff += 2 * math.pi
        return diff
    
    def draw_transparent_object(self, x, y, image):
        if image is None or image.shape[-1] != 4:
            return
            
        size = image.shape[0]
        half_size = size // 2

        y_min = y - half_size
        y_max = y + half_size
        x_min = x - half_size
        x_max = x + half_size

        canvas_h, canvas_w = self.canvas.shape[:2]
        if y_min < 0 or y_max > canvas_h or x_min < 0 or x_max > canvas_w:
            return

        alpha = image[:, :, 3] / 255.0
        for c in range(3):
            self.canvas[y_min:y_max, x_min:x_max, c] = (
                alpha * image[:, :, c] + (1 - alpha) * self.canvas[y_min:y_max, x_min:x_max, c]
            )

    def draw_star(self, x, y):
        star = self.resource_loader.get_image("star")
        self.draw_transparent_object(x, y, star)
            
    def draw_moon(self, x, y):
        moon = self.resource_loader.get_image("moon")
        self.draw_transparent_object(x, y, moon)

    def draw_planet(self, x, y):
        planet = self.resource_loader.get_image("planet")
        self.draw_transparent_object(x, y, planet)

    def draw_celestial(self):
        for celestial in self.celestials:
            relative_azimuth = self.circular_diff(self.azimuth, celestial.gha)
            relative_elevation = celestial.hc - self.elevation
            if abs(relative_azimuth) > self.fovx / 2 or abs(relative_elevation) > self.fovy / 2:
                continue
            x = int(self.stream_width * (0.5 + relative_azimuth / self.fovx))
            y = int(self.stream_height * (0.5 - relative_elevation / self.fovy))
            if celestial.object_name == "Moon":
                self.draw_moon(x, y)
            if celestial.object_name in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]:
                self.draw_planet(x, y)
            else:
                self.draw_star(x, y)
            
    def draw(self):
        self.canvas = self.empty_sky.copy()
        self.draw_celestial()
        self.draw_terrain()
        return self.canvas.copy()
    