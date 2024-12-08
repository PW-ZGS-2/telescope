import cv2
import matplotlib.pyplot as plt

class ResourceLoader:
    def __init__(self, size):
        self.resources = {}
        self.resources.update({
            "moon": ("resources/moon.png", 10),
            "star": ("resources/star.png", 1),
            "planet": ("resources/planet.png", 0.5)
        })

        self.images = {}
        for name, (path, scaler) in self.resources.items():
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
                img = cv2.resize(img, (int(size * scaler), int(size * scaler)))
                self.images[name] = img
            else:
                print(f"Error loading image: {path}")

    def get_image(self, name):
        return self.images[name]
