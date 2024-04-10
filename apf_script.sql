DROP TABLE IF EXISTS City;
DROP TABLE IF EXISTS CityCrime;
DROP TABLE IF EXISTS ApartmentComplex;
DROP TABLE IF EXISTS ApartmentUnit;
DROP TABLE IF EXISTS UnitAmenities;

CREATE TABLE City (
    CityId INTEGER PRIMARY KEY AUTOINCREMENT,
    CityName TEXT,
    State TEXT,
    Population INTEGER,
    Population_change REAL,
    Population_males REAL, 
    Population_females REAL,
    Median_resident_age REAL,
    Income_2022 INTEGER, 
    Income_2020 INTEGER, 
    Per_capita_income_2022 INTEGER, 
    Per_capita_income_2020 INTEGER, 
    Median_house_value_2022 INTEGER, 
    Median_house_value_2020 INTEGER,
    Median_gross_rent_2022 INTEGER, 
    Cost_of_living REAL, 
    Poverty_percentage REAL,
    Land_area REAL, 
    Population_density INTEGER, 
    Tax_with_mortgage REAL,
    Tax_no_mortgage REAL, 
    Unemployment REAL
);

CREATE TABLE CityCrime( 
    Crime_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Year INTEGER, 
    Murders REAL,
    Rapes REAL,
    Robberies REAL,
    Assaults REAL,
    Burglaries REAL,
    Thefts REAL,
    Auto_thefts REAL, 
    Arson REAL,
    CityId INTEGER,
    FOREIGN KEY (CityId) REFERENCES City(CityId)
);

-- created are own id for each complex, utilizing prexisting ids given by each website to connect units and amenities.
CREATE TABLE ApartmentComplex (
    APFId INTEGER PRIMARY KEY AUTOINCREMENT,
    ComplexId VARCHAR(20),
    Name TEXT,
    BuildingUrl TEXT,
    Latitude REAL,
    Longitude REAL, 
    PriceMin INT,
    PriceMax INT,
    Address TEXT,
    Neighborhood TEXT,
    Zipcode INT, 
    NumUnits INTEGER,
    Source TEXT,
    CityId INTEGER,
    FOREIGN KEY (CityId) REFERENCES City(CityId)
);

CREATE TABLE ApartmentUnit (
    UnitId VARCHAR(20) PRIMARY KEY,
    MaxRent REAL,
    ModelName TEXT,
    Beds INTEGER,
    Baths REAL,
    SquareFootage INTEGER,
    Details TEXT,
    IsAvailable TEXT, 
    ComplexId INTEGER,
    FOREIGN KEY (WebsiteId) REFERENCES ApartmentComplex(WebsietId)
);

-- links the website rental id to each amenitiy
CREATE TABLE UnitAmenities (
    UnitId INTEGER,
    UnitAmenities TEXT,
    subtype TEXT,
    FOREIGN KEY (UnitId) REFERENCES ApartmentUnit(UnitId)
);