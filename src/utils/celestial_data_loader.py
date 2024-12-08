import requests
import math
from datetime import datetime, timezone

class CelestialData:
    def __init__ (self, object_name, dec, gha, hc, zn):
        self.object_name = object_name
        self.dec = dec
        self.gha = gha
        self.hc = hc
        self.zn = zn

class CelestialDataLoader:
    BASE_URL = "https://aa.usno.navy.mil/api/celnav"

    def __init__(self, coords):
        self.coords = coords
        self.data = self.fetch_data()

    def fetch_data(self):
        params = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "coords": f"{self.coords[0]},{self.coords[1]}"
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            self.raw_data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch data: {e}")
    
    def get_raw_data(self):
        return self.raw_data
    
    def deg2rad(self, deg):
        return deg * (math.pi / 180)
    
    def parse_data(self) -> list[CelestialData]:
        celestial_data = []
        if not self.raw_data:
            return
        if "properties" in self.raw_data and "data" in self.raw_data["properties"]:
            for entry in self.raw_data["properties"]["data"]:
                object_name = entry.get("object", None)
                if not object_name:
                    continue
                almanac = entry.get("almanac_data", {})
                if not almanac:
                    continue
                dec = almanac.get("dec", None)
                gha = almanac.get("gha", None)
                hc = almanac.get("hc", None)
                zn = almanac.get("zn", None)
                if not dec or not gha or not hc or not zn:
                    continue
                celestial_data.append(CelestialData(object_name.lower(), 
                    self.deg2rad(dec), 
                    self.deg2rad(gha),
                    self.deg2rad(hc), 
                    self.deg2rad(zn))) 
        return celestial_data