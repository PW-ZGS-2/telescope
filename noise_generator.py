import numpy as np

class NoiseGenerator:
    def __init__(self, stream_width, stream_height, scale=1.0):
        self.stream_width = stream_width
        self.stream_height = stream_height
        self.scale = scale if scale > 0 else 1.0

    def generate_perlin_noise(self):
        # Initialize the noise array
        noise = np.zeros((self.stream_height, self.stream_width))

        # Determine the frequency and amplitude of the noise
        frequency = 1 / self.scale
        amplitude = 1.0

        # Generate gradients
        gradients = self._generate_gradients()

        # Populate the noise array
        for y in range(self.stream_height):
            for x in range(self.stream_width):
                # Scale coordinates
                sx = x * frequency
                sy = y * frequency

                # Get the top-left grid point
                x0 = int(sx)
                y0 = int(sy)

                # Get the offsets within the grid cell
                dx = sx - x0
                dy = sy - y0

                # Determine gradient vectors for each corner
                g00 = gradients[y0 % gradients.shape[0], x0 % gradients.shape[1]]
                g10 = gradients[y0 % gradients.shape[0], (x0 + 1) % gradients.shape[1]]
                g01 = gradients[(y0 + 1) % gradients.shape[0], x0 % gradients.shape[1]]
                g11 = gradients[(y0 + 1) % gradients.shape[0], (x0 + 1) % gradients.shape[1]]

                # Compute dot products
                dot00 = np.dot(g00, [dx, dy])
                dot10 = np.dot(g10, [dx - 1, dy])
                dot01 = np.dot(g01, [dx, dy - 1])
                dot11 = np.dot(g11, [dx - 1, dy - 1])

                # Interpolate between dot products
                u = self._fade(dx)
                v = self._fade(dy)
                nx0 = self._lerp(dot00, dot10, u)
                nx1 = self._lerp(dot01, dot11, u)
                nxy = self._lerp(nx0, nx1, v)

                # Assign noise value
                noise[y, x] = nxy

        # Normalize noise to range [0, 1]
        noise = (noise - np.min(noise)) / (np.max(noise) - np.min(noise))

        return noise

    def _generate_gradients(self):
        # Randomly generate gradient vectors for a grid
        gradients = np.random.rand(self.stream_height + 1, self.stream_width + 1, 2) * 2 - 1
        gradients /= np.linalg.norm(gradients, axis=-1, keepdims=True)
        return gradients

    @staticmethod
    def _fade(t):
        # Smoothstep function for interpolation
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a, b, t):
        # Linear interpolation
        return a + t * (b - a)