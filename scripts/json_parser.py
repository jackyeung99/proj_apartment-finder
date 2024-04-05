import json 
import pydantic_models as pyd

''' Opted for a nested parsing approach, in which child functions are responsible for parts, and parent functions call the children, the other option would be to employ a flat-parsing method '''

class ApartmentParser:

    def apartment_parser(self, apartment_json, city_id): 
        # Use Pydantic model for the apartment
        apartment_data = pyd.ApartmentComplex(
            CityId=city_id, 
            ListingId=apartment_json['listingId'],
            Name=apartment_json['listingName'],
            BuildingUrl='https://www.apartments.com/' + '-'.join(apartment_json['listingName'].split(' ')) + f"/{apartment_json['listingId']}",
            Latitude=apartment_json['location']['latitude'],
            Longitude=apartment_json['location']['longitude'],
            PriceMin=apartment_json['listingMinRent'],
            PriceMax=apartment_json['listingMaxRent'],
            Address=apartment_json['listingAddress'],
            Neighborhood=apartment_json['listingNeighborhood'],
            Zipcode=apartment_json['listingZip'],
            NumUnits=len(apartment_json.get('rentals', [])),
            Source='apartments.com'
        )
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
                IsAvailable='yes' if unit_data['AvailabilityStatus'] == 1 else 'no'
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
    def apartment_parser(self, apartment_json, city_id): 
    def unit_parser(self, rentals, building_id): 
    def amenity_parser(self, unit):


class CityParser:
    def city_parser(self,city_json): 
        city_tuple = (city['city'], 
                    city['state'],
                    city['population'],
                    city['population_change'],
                    city['males'],
                    city['females'],
                    city['median_resident_age'],
                    city['median_household_income_2022'],
                    city['median_household_income_2000'],
                    city['per_capita_income_2022'],
                    city['per_capita_income_2000'],
                    city['median_house_value_2022'],
                    city['median_house_value_2000'],
                    city['median_gross_rent'],
                    city['cost_of_living_index'],
                    city['poverty_percentage'],
                    city['land_area'],
                    city['population_density(per square mile)'],
                    city['tax_percentage_with_mortgage'],
                    city['tax_percentage_no_mortgage'],
                    city['unemployment_rate'])
        

    def crime_parser: 
        for year in city.get('crime', []):
                crime_tuple = (city_id,
                                year['year'],
                                year['Murders'],
                                year['Rapes'],
                                year['Robberies'],
                                year['Assaults'],
                                year['Burglaries'],
                                year['Thefts'],
                                year['Auto thefts'],
                                year['Arson'])