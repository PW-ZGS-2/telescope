import requests

class TelescopeData:
    def __init__(self, name, location, specifications, price_per_minute, status):
        self.name = name
        self.location = location
        self.specifications = specifications
        self.price_per_minute = price_per_minute
        self.status = status

    def to_dict(self):
        return {
            "telescope_name": self.name,
            "location": self.location.to_dict(),
            "specifications": self.specifications.to_dict(),
            "price_per_minute": self.price_per_minute,
            "status": self.status
        }

class Location:
    def __init__(self, city, country, latitude, longitude):
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "city": self.city,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

class Specifications:
    def __init__(self, aperture, focal_length, focal_ratio, weight, length, width, height, mount_type, optical_design):
        self.aperture = aperture
        self.focal_length = focal_length
        self.focal_ratio = focal_ratio
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.mount_type = mount_type
        self.optical_design = optical_design

    def to_dict(self):
        return {
            "aperture": self.aperture,
            "focal_length": self.focal_length,
            "focal_ratio": self.focal_ratio,
            "weight": self.weight,
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "mount_type": self.mount_type,
            "optical_design": self.optical_design
        }

class TelescopeResponse:
    def __init__(self, telescope_id, publish_token=None, subscribe_token=None):
        self.telescope_id = telescope_id
        self.publish_token = publish_token
        self.subscribe_token = subscribe_token

    @classmethod
    def from_dict(cls, data):
        return cls(
            telescope_id=data.get("telescope_id"),
            publish_token=data.get("publish_token"),
            subscribe_token=data.get("subscribe_token")
        )

class DeleteResponse:
    def __init__(self, message):
        self.message = message

    @classmethod
    def from_dict(cls, data):
        return cls(message=data.get("message"))

class ApiClient:
    def __init__(self, base_url):
        """
        Initialize the TelescopeClient.

        Args:
            base_url (str): The base URL of the Telescope API.
        """
        self.base_url = base_url

    def post_telescope(self, data):
        """
        Add a new telescope.

        Args:
            data (TelescopeData): The telescope data to add.

        Returns:
            TelescopeResponse: The response from the API.
        """
        url = f"{self.base_url}/telescopes/"
        response = requests.post(url, json=data.to_dict())
        if response.status_code == 200:
            return TelescopeResponse.from_dict(response.json())
        else:
            return {"error": response.json()}

    def update_telescope(self, telescope_id, data):
        """
        Update details of a specific telescope.

        Args:
            telescope_id (str): The ID of the telescope to update.
            data (TelescopeData): The updated telescope data.

        Returns:
            TelescopeResponse: The response from the API.
        """
        url = f"{self.base_url}/telescopes/{telescope_id}"
        response = requests.put(url, json=data.to_dict())
        if response.status_code == 200:
            return TelescopeResponse.from_dict(response.json())
        else:
            return {"error": response.json()}

    def delete_telescope(self, telescope_id):
        """
        Delete a specific telescope.

        Args:
            telescope_id (str): The ID of the telescope to delete.

        Returns:
            DeleteResponse: The response from the API.
        """
        url = f"{self.base_url}/telescopes/{telescope_id}"
        response = requests.delete(url)
        if response.status_code == 200:
            return DeleteResponse.from_dict({"message": "Telescope deleted successfully."})
        else:
            return {"error": response.json()}
