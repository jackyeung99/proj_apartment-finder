import json 
import utils.pydantic_models as pyd

''' Opted for a nested parsing approach, in which child functions are responsible for parts, and parent functions call the children, the other option would be to employ a flat-parsing method '''

class ApartmentParser:

    def apartment_parser(self, apartment_json, city_id): 
        # Use Pydantic model for the apartment
        apartment_data = pyd.ApartmentComplex({
            'ListingId':apartment_json['listingId'],
            'Name':apartment_json['listingName'],
            'BuildingUrl':'https://www.apartments.com/' + '-'.join(apartment_json['listingName'].split(' ')) + f"/{apartment_json['listingId']}",
            'Latitude':apartment_json['location']['latitude'],
            'Longitude':apartment_json['location']['longitude'],
            'PriceMin':apartment_json['listingMinRent'],
            'PriceMax':apartment_json['listingMaxRent'],
            'Address':apartment_json['listingAddress'],
            'Neighborhood':apartment_json['listingNeighborhood'],
            'Zipcode':apartment_json['listingZip'],
            'NumUnits':len(apartment_json.get('rentals', [])),
            'Source':'apartments.com'
            })
        units = self.unit_parser(self.json.get('rentals', []), apartment_data.BuildingId)
        return apartment_data, units
    
    def unit_parser(self, rentals, building_id): 
        units = []
        for unit_data in rentals:
            unit_model = pyd.ApartmentUnit(
                BuildingId=building_id,
                WebsiteId=unit_data['RentalKey'],
                MaxRent=unit_data.get('Rent', None),
                ModelName=unit_data.get('Name', ''),
                Beds=unit_data['Beds'],
                Baths=unit_data['Baths'],
                SquareFootage=unit_data.get('SquareFeet', None),
                Details=unit_data.get('Description', ''),
                IsAvailable= True if unit_data['AvailabilityStatus'] == 1 else False
            )
            units.append(unit_model)
            amenities = self.amenity_parser(unit_data)
            
        return units

    def amenity_parser(self, unit):
        amenities = []
        if 'InteriorAmenities' in unit and unit['InteriorAmenities'] is not None:
            for subcategory in unit['InteriorAmenities']['SubCategories']: 
                for amenity in subcategory['Amenities']:
                    amenity_model = pyd.UnitAmenities(UnitId=unit['RentalKey'], UnitAmenities=amenity['Name'])
                    amenities.append(amenity_model)
        return amenities

class ZillowParser:
    def apartment_parser(self, apartment_json,city_id): 
        if apartment_json.get('neighborhoodRegion') is not None:
            neighborhood = apartment_json['neighborhoodRegion'].get('name', '')
        else:
            neighborhood = None
            
        apartment_data = pyd.ApartmentComplex(
            CityId = city_id,
            WebsiteId=str(apartment_json['zpid']),
            Name=apartment_json.get('name', None), 
            BuildingUrl=f"https://www.zillow.com/{apartment_json['hdpUrl']}",
            Latitude=apartment_json['latitude'],
            Longitude=apartment_json['longitude'],
            PriceMin=apartment_json['price'],
            PriceMax=apartment_json['price'],
            Address=apartment_json['streetAddress'],
            Neighborhood= neighborhood,
            Zipcode=apartment_json['address']['zipcode'],
            NumUnits=1,
            Source='zillow.com'
        )
        
        
        unit_model = pyd.ApartmentUnit(
                BuildingId=None,
                WebsiteId=str(apartment_json['zpid']),
                MaxRent=apartment_json['price'],
                ModelName=apartment_json.get('Name', ''),
                Beds=apartment_json['bedrooms'],
                Baths=apartment_json['bathrooms'],
                SquareFootage=apartment_json.get('livingAreaValue', None),
                Details=apartment_json.get('Description', ''),
                IsAvailable= apartment_json['moveInReady']
            )
        
        return apartment_data, unit_model
    
    def amenity_parser(self,apartment_json):
        amenities = []

        for k,v in apartment_json['resoFacts'].items():
            if v == 'True':
                print(k,v)

class CityParser:
    def city_parser(self, city_json):
        # Assuming city_json is a dict containing city data and a list of crimes
        city_data = pyd.City(**{k: v for k, v in city_json.items() if k != 'crime'})
        crimes = [pyd.CityCrime(**crime) for crime in city_json.get('crime', [])]
        return city_data, crimes