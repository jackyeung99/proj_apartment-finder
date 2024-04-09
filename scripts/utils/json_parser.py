import json 
import utils.pydantic_models as pyd

''' Opted for a nested parsing approach, in which child functions are responsible for parts, and parent functions call the children, the other option would be to employ a flat-parsing method '''

class BaseParser:
    """
    A base parser class to offer shared utilities across different parsers.
    """
    @staticmethod
    def construct_url(base_url, path_components):
        """
        Constructs a URL from base_url and path_components.
        """
        return f"{base_url}{'/'.join(path_components)}"

class ApartmentParser(BaseParser):
    def parse(self, apartment_json, city_id):
        # Improved parsing logic using Pydantic's powerful parsing capabilities.
        apartment_data = pyd.ApartmentComplex(
            CityId=city_id,
            WebsiteId=str(apartment_json['listingId']),
            Name=apartment_json.get('listingName'),
            BuildingUrl=self.construct_url('https://www.apartments.com/', [apartment_json['listingName'].replace(' ', '-'), str(apartment_json['listingId'])]),
            Latitude=apartment_json.get('location', {}).get('latitude'),
            Longitude=apartment_json.get('location', {}).get('longitude'),
            PriceMin=apartment_json.get('listingMinRent'),
            PriceMax=apartment_json.get('listingMaxRent'),
            Address=apartment_json.get('listingAddress'),
            Neighborhood=apartment_json.get('listingNeighborhood'),
            Zipcode=apartment_json.get('listingZip'),
            NumUnits=len(apartment_json.get('rentals', [])),
            Source='apartments.com'
        )
        units = [self.parse_unit(unit, None) for unit in apartment_json.get('rentals', [])]  # BuildingId to be updated post database insertion
        return apartment_data, units

    def parse_unit(self, unit_json, building_id):
        amenities = self.parse_amenities(unit_json)
        unit_data = pyd.ApartmentUnit(
            BuildingId=building_id,
            WebsiteId=unit_json.get('RentalKey'),
            MaxRent=unit_json.get('Rent'),
            ModelName=unit_json.get('Name', ''),
            Beds=unit_json.get('Beds', 0),
            Baths=unit_json.get('Baths', 0.0),
            SquareFootage=unit_json.get('SquareFeet'),
            Details=unit_json.get('Description', ''),
            IsAvailable=unit_json.get('AvailabilityStatus') == 1
        )
        return unit_data, amenities

    def parse_amenities(self, apartment_json):
        amenities = []

        for units in apartment_json.get('rentals', []):
            # Use an empty dictionary as the default value if 'InteriorAmenities' is None
            interior_amenities = units.get('InteriorAmenities', {}) or {}
            for subcategory in interior_amenities.get('SubCategories', []):
                for amenity in subcategory.get('Amenities', []):
                    amenities.append(pyd.UnitAmenities(websiteId=units.get('RentalKey'), UnitAmenities=amenity.get('Name')))
        
        return amenities

class ZillowParser(BaseParser):
    def parse(self, apartment_json, city_id):
        neighborhood = apartment_json.get('neighborhoodRegion', {}).get('name', None)
        
        apartment_data = pyd.ApartmentComplex(
            CityId=city_id,
            WebsiteId=str(apartment_json['zpid']),
            Name=apartment_json.get('name'),
            BuildingUrl=self.construct_url('https://www.zillow.com/', [apartment_json.get('hdpUrl', '')]),
            Latitude=apartment_json.get('latitude'),
            Longitude=apartment_json.get('longitude'),
            PriceMin=apartment_json.get('price'),
            PriceMax=apartment_json.get('price'),
            Address=apartment_json.get('streetAddress'),
            Neighborhood=neighborhood,
            Zipcode=apartment_json.get('address', {}).get('zipcode', 0),
            NumUnits=1,
            Source='zillow.com'
        )
        
        unit_model = pyd.ApartmentUnit(
            BuildingId=None,  # To be updated post database insertion
            WebsiteId=str(apartment_json['zpid']),
            MaxRent=apartment_json.get('price'),
            ModelName=apartment_json.get('name', ''),
            Beds=apartment_json.get('bedrooms', 0),
            Baths=apartment_json.get('bathrooms', 0.0),
            SquareFootage=apartment_json.get('livingAreaValue'),
            Details=apartment_json.get('description', ''),
            IsAvailable=apartment_json.get('moveInReady', False)
        )
        
        return apartment_data, unit_model
    def parse_ammenity(self,apartment_json):
        amenities = []

        multivalue_keys = ['appliances','allowedPets', 'exteriorFeatires','laundryFeatures','parkingFeatures']
        for k,v in apartment_json['resoFacts'].items():
            if v is True :
                # print(k,v)
                amenities.append((apartment_json['zpid'],k))
            if k in multivalue_keys and v:
                print(v)

        return amenities

class CityParser:
    def city_parser(self, city_json):
        # Assuming city_json is a dict containing city data and a list of crimes
        city_data = pyd.City(**{k: v for k, v in city_json.items() if k != 'crime'})
        crimes = [pyd.CityCrime(**crime) for crime in city_json.get('crime', [])]
        return city_data, crimes