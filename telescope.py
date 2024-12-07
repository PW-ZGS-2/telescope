from abc import ABC, abstractmethod

class Telescope(ABC):
    @abstractmethod
    def get_resolution(self):
        """
        Return the resolution of the telescope's video stream.
        :return: Tuple of (width, height).
        """
        pass

    @abstractmethod
    def get_fov(self):
        """
        Return the field of view of the telescope.
        :return: Tuple of (fovx, fovy).
        """
        pass

    @abstractmethod
    def get_orientation(self):
        """
        Return the orientation of the telescope.
        :return: Tuple of (azimuth, elevation).
        """
        pass

    @abstractmethod
    def get_location(self):
        """
        Return the location of the telescope.
        :return: Tuple of (latitude, longitude).
        """
        pass

    @abstractmethod
    def set_orientation(self, azimuth: float, elevation: float):
        """
        Set the orientation of the telescope.
        :param azimuth: Azimuth angle in radians.
        :param elevation: Elevation angle in radians.
        """
        pass

    @abstractmethod
    def get_frame(self):
        """
        Return the current video frame.
        :return: An instance of opencv canvas.
        """
        pass

    @abstractmethod
    def set_zoom(self, zoom: float):
        """
        Set the zoom level of the telescope.
        :param zoom: Zoom level (1 for default, max_zoom for maximum).
        """
        pass

    @abstractmethod
    def move(self, da: float, de: float, dz: float):
        """
        Move the telescope by adjusting azimuth, elevation, and zoom.
        :param da: Change in azimuth in radians.
        :param de: Change in elevation in radians.
        :param dz: Change in zoom level.
        """
        pass