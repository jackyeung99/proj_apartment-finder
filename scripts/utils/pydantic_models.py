from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional

class City(BaseModel):
    CityName: str
    State: str
    Population: int
    Population_change: float
    Population_males: float
    Population_females: float
    Median_resident_age: float
    Income_2022: int
    Income_2000: int
    Per_capita_income_2022: int 
    Per_capita_income_2000: int
    Median_house_value_2022: int
    Median_house_value_2000: int 
    Median_gross_rent_2022: int
    Cost_of_living: float 
    Poverty_percentage: float
    Land_area: float
    Population_density: int
    Tax_with_mortgage: float
    Tax_no_mortgage: float
    Unemployment: float

class CityCrime(BaseModel):
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
    ComplexId: str
    Name: Optional[str]
    BuildingUrl: HttpUrl
    Latitude: Optional[float]
    Longitude: Optional[float]
    PriceMin: int
    PriceMax: int
    Address: str
    Neighborhood: Optional[str]
    Zipcode: int
    NumUnits: int
    Source: str
    CityId: int  #foreign key 

class ApartmentUnit(BaseModel):
    UnitId: str
    MaxRent: Optional[float]
    ModelName: Optional[str]
    Beds: int
    Baths: float
    SquareFootage: Optional[int]
    Details: str
    IsAvailable: bool
    ComplexId: str   #foreign key 

class UnitAmenities(BaseModel):
    UnitId: str   #foreign key 
    UnitAmenity: str  #foreign key 
    subtype: Optional[str]