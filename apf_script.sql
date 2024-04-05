CREATE TABLE IF NOT EXISTS City (
    CityId INTEGER PRIMARY KEY AUTOINCREMENT,
    CityName TEXT,
    State TEXT,
    Population INTEGER,
    Population_change REAL,
    Population_males REAL, 
    Population_Females REAL,
    Median_Resident_Age REAL,
    Income_2022 INTEGER, 
    Income_2020 INTEGER, 
    per_capita_income_2022 INTEGER, 
    per_capita_income_2020 INTEGER, 
    Median_house_value_2022 INTEGER, 
    Median_house_value_2020 INTEGER,
    Median_Gross_Rent_2022 INTEGER, 
    Cost_of_living REAL, 
    Poverty_Percentage REAL,
    Land_area REAL, 
    Population_Density INTEGER, 
    Tax_with_mortgage REAL,
    Tax_no_mortgage REAL, 
    Unemployment REAL
);

CREATE TABLE IF NOT EXISTS City_Crime( 
    Crime_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CityId INTEGER,
    Year INTEGER, 
    Murders REAL,
    Rapes REAL,
    Robberies REAL,
    Assaults REAL,
    Burglaries REAL,
    Thefts REAL,
    Auto_thefts REAL, 
    Arson REAL,
    FOREIGN KEY (CityId) REFERENCES City(CityId)
);

CREATE TABLE IF NOT EXISTS ApartmentComplex (
    BuildingId INTEGER PRIMARY KEY AUTOINCREMENT,
    CityId INTEGER,
    WebsiteId VARCHAR(20),
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
    FOREIGN KEY (CityId) REFERENCES City(CityId)
);

CREATE TABLE IF NOT EXISTS ApartmentUnit (
    UnitId INTEGER PRIMARY KEY AUTOINCREMENT,
    BuildingId INTEGER,
    WebsiteId VARCHAR(20),
    MaxRent REAL,
    ModelName TEXT,
    Beds INTEGER,
    Baths REAL,
    SquareFootage INTEGER,
    Details TEXT,
    IsAvailable TEXT, 
    FOREIGN KEY (BuildingId) REFERENCES ApartmentComplex(BuildingId)
);

CREATE TABLE IF NOT EXISTS BuildingAmenities (
    BuildingId INTEGER,
    CommunityAmenities TEXT,
    FOREIGN KEY (BuildingId) REFERENCES ApartmentComplex(BuildingId)
);

CREATE TABLE IF NOT EXISTS UnitAmenities (
    UnitId INTEGER,
    UnitAmenities TEXT,
    FOREIGN KEY (UnitId) REFERENCES ApartmentUnit(UnitId)
);