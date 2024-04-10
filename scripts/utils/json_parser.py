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
        apartment_data = self.parse_complex(apartment_json, city_id)

        units_data = [self.parse_unit(unit, apartment_data.ComplexId ) for unit in apartment_json.get('rentals', [])] 

        amenities_data = self.parse_amenities(apartment_json)

        return apartment_data, units_data, amenities_data
    
    def parse_complex(self, apartment_json, city_id):
        apartment_data = pyd.ApartmentComplex(
            CityId = city_id,
            ComplexId = str(apartment_json['listingId']),
            Name = apartment_json.get('listingName'),
            BuildingUrl = self.construct_url('https://www.apartments.com/', [apartment_json['listingName'].replace(' ', '-'), str(apartment_json['listingId'])]),
            Latitude = apartment_json.get('location', {}).get('latitude'),
            Longitude = apartment_json.get('location', {}).get('longitude'),
            PriceMin = apartment_json.get('listingMinRent'),
            PriceMax = apartment_json.get('listingMaxRent'),
            Address = apartment_json.get('listingAddress'),
            Neighborhood = apartment_json.get('listingNeighborhood'),
            Zipcode = apartment_json.get('listingZip'),
            NumUnits = len(apartment_json.get('rentals', [])),
            Source = 'apartments.com')
        
        return apartment_data

    def parse_unit(self, unit_json, complex_id):
        unit_data = pyd.ApartmentUnit(
            ComplexId=complex_id,
            UnitId=unit_json.get('RentalKey'),
            MaxRent=unit_json.get('Rent'),
            ModelName=unit_json.get('Name', ''),
            Beds=unit_json.get('Beds', 0),
            Baths=unit_json.get('Baths', 0.0),
            SquareFootage=unit_json.get('SquareFeet'),
            Details=unit_json.get('Description', ''),
            IsAvailable=unit_json.get('AvailabilityStatus') == 1
        )
        return unit_data

    def parse_amenities(self, apartment_json):
        amenity_data = []

        for units in apartment_json.get('rentals', []):
            interior_amenities = units.get('InteriorAmenities', {}) or {}
            for subcategory in interior_amenities.get('SubCategories', []):
                for amenity in subcategory.get('Amenities', []):
                    amenity_data.append(
                        pyd.UnitAmenities(
                                UnitId=units.get('RentalKey'), UnitAmenity=amenity.get('Name'),
                                subtype = subcategory.get('Name')
                                ))
                   
        
        return amenity_data

class ZillowParser(BaseParser):
    def parse(self, apartment_json, city_id):

        apartment_data = self.parse_complex(apartment_json, city_id)

        units_data = self.parse_unit(apartment_json, apartment_data.ComplexId)

        amenities_data = self.parse_amenities(apartment_json)

        return apartment_data, units_data, amenities_data




    def parse_complex(self,apartment_json, city_id): 
        
        neighborhood = apartment_json.get('neighborhoodRegion')
        neighborhood_name = neighborhood.get('name') if neighborhood is not None else None

        apartment_data = pyd.ApartmentComplex(
            CityId = city_id,
            ComplexId = str(apartment_json['zpid']),
            Name = apartment_json.get('name'),
            BuildingUrl = self.construct_url('https://www.zillow.com/', [apartment_json.get('hdpUrl', '')]),
            Latitude = apartment_json.get('latitude'),
            Longitude = apartment_json.get('longitude'),
            PriceMin = apartment_json.get('price'),
            PriceMax = apartment_json.get('price'),
            Address = apartment_json.get('streetAddress'),
            Neighborhood = neighborhood_name,
            Zipcode = apartment_json.get('address', {}).get('zipcode', 0),
            NumUnits = 1,
            Source = 'zillow.com'
            )
        
        return apartment_data
    
    def parse_unit(self,apartment_json, complex_id):
        unit_data = pyd.ApartmentUnit(
            ComplexId = complex_id, 
            UnitId = str(apartment_json['zpid']),
            MaxRent = apartment_json.get('price'),
            ModelName = apartment_json.get('name', ''),
            Beds = apartment_json.get('bedrooms', 0),
            Baths = apartment_json.get('bathrooms', 0.0),
            SquareFootage = apartment_json.get('livingAreaValue'),
            Details = apartment_json.get('description', ''),
            IsAvailable = apartment_json.get('moveInReady', False)
        )
        return unit_data

    def parse_amenities(self,apartment_json):
        amenities = []

        multivalue_keys = ['appliances','allowedPets', 'exteriorFeatires','laundryFeatures','parkingFeatures']
        for k,v in apartment_json['resoFacts'].items():
            if v is True :

                amenities.append(pyd.UnitAmenities(
                    UnitId=str(apartment_json['zpid']),
                    UnitAmenity=k,
                    subtype = None
                    ))
                
            if k in multivalue_keys and v:
                for val in v:  
                    amenities.append(pyd.UnitAmenities(
                        UnitId=str(apartment_json['zpid']),
                        UnitAmenity=val,
                        subtype = k 
                        ))
                    

        return amenities

class CityParser:
    def city_parser(self, city_json):
        # Assuming city_json is a dict containing city data and a list of crimes
        city_data = pyd.City(**{k: v for k, v in city_json.items() if k != 'crime'})
        crimes = [pyd.CityCrime(**crime) for crime in city_json.get('crime', [])]
        return city_data, crimes