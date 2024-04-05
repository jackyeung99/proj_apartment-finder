from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional

class City(BaseModel):
    CityId: Optional[int]
    CityName: str
    State: str
    Population: int
    Population_change: float
    Population_males: float
    Population_Females: float
    Median_Resident_Age: float
    Income_2022: int
    Income_2020: int
    per_capita_income_2022: int
    per_capita_income_2020: int
    Median_house_value_2022: int
    Median_house_value_2020: int
    Median_Gross_Rent_2022: int
    Cost_of_living: float
    Poverty_Percentage: float
    Land_area: float
    Population_Density: int
    Tax_with_mortgage: float
    Tax_no_mortgage: float
    Unemployment: float

class CityCrime(BaseModel):
    Crime_ID: Optional[int]
    CityId: int
    Year: int
    Murders: float
    Rapes: float
    Robberies: float
    Assaults: float
    Burglaries: float
    Thefts: float
    Auto_thefts: float
    Arson: float

class ApartmentComplex(BaseModel):
    BuildingId: Optional[int]
    CityId: int
    WebsiteId: str
    Name: str
    BuildingUrl: HttpUrl
    Latitude: float
    Longitude: float
    PriceMin: int
    PriceMax: int
    Address: str
    Neighborhood: str
    Zipcode: int
    NumUnits: int
    Source: str

class ApartmentUnit(BaseModel):
    UnitId: Optional[int]
    BuildingId: int
    WebsiteId: str
    MaxRent: float
    ModelName: str
    Beds: int
    Baths: float
    SquareFootage: int
    Details: str
    IsAvailable: str
    # Ensuring IsAvailable is either 'yes' or 'no'
    @validator('IsAvailable')
    def is_available_validator(cls, v):
        if v not in ('yes', 'no'):
            raise ValueError("IsAvailable must be 'yes' or 'no'")
        return v

class BuildingAmenities(BaseModel):
    BuildingId: int
    CommunityAmenities: str

class UnitAmenities(BaseModel):
    UnitId: int
    UnitAmenities: str