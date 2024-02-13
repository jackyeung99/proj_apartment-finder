from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class GeoCoder:
    def __init__(self, user_agent="my_geocoder", max_workers=5):
        self.geolocator = Nominatim(user_agent=user_agent)
        self.max_workers = max_workers
        logging.basicConfig(level=logging.INFO)

    def geocode_address(self, address, attempt=1, max_attempts=3):
        try:
            location = self.geolocator.geocode(address, timeout=10)
            return (location.latitude, location.longitude) if location else (None, None)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            if attempt < max_attempts:
                logging.warning(f"Geocoding attempt {attempt} failed for {address}, retrying...")
                return self.geocode_address(address, attempt + 1, max_attempts)
            else:
                logging.error(f"Geocoding failed after {max_attempts} attempts for {address}.")
                return None, None

    def batch_geocode(self, addresses):
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_address = {executor.submit(self.geocode_address, address): address for address in addresses}

            for future in as_completed(future_to_address):
                address = future_to_address[future]
                try:
                    results[address] = future.result()
                except Exception as exc:
                    logging.error(f"{address} generated an exception: {exc}")
                    results[address] = (None, None)
        return results

if __name__ == '__main__':
    geocoder = GeoCoder(max_workers=10)
    addresses = ["1600 Amphitheatre Parkway, Mountain View, CA", "1 Infinite Loop, Cupertino, CA"]
    results = geocoder.batch_geocode(addresses)
    for address, (lat, lon) in results.items():
        print(f"{address}: Latitude = {lat}, Longitude = {lon}")