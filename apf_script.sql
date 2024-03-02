CREATE TABLE IF NOT EXISTS City (
    CityId INTEGER PRIMARY KEY,
    CityName VARCHAR(255),
    COL REAL,
    Population INTEGER,
    CrimeRate REAL,
    TaxRate REAL,
    Unemployment REAL,
    MedianIncome REAL,
    Growth REAL
);

CREATE TABLE IF NOT EXISTS leasing_info (
    LeasingId INTEGER PRIMARY KEY,
    Name VARCHAR(255),
    Phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS ApartmentComplex (
    ComplexId INTEGER PRIMARY KEY,
    CityId INTEGER,
    Name VARCHAR(255),
    PropertyUrl VARCHAR(255),
    Lat REAL,
    Long REAL,
    PriceRange VARCHAR(100),
    Address VARCHAR(255),
    Neighborhood VARCHAR(255),
    ReviewScore REAL,
    NumReviews INTEGER,
    NumUnits INTEGER,
    Details TEXT,
    FOREIGN KEY (CityId) REFERENCES City(CityId)
);

CREATE TABLE IF NOT EXISTS ApartmentUnit (
    UnitId INTEGER PRIMARY KEY,
    PropertyId INTEGER,
    MaxRent REAL,
    ModelName VARCHAR(255),
    Beds INTEGER,
    Baths REAL,
    SquareFootage INTEGER,
    FOREIGN KEY (PropertyId) REFERENCES ApartmentComplex(ComplexId)
);

CREATE TABLE IF NOT EXISTS ComplexAmmenities (
    PropertyId INTEGER,
    CommunityAmenities TEXT,
    FOREIGN KEY (PropertyId) REFERENCES ApartmentComplex(ComplexId)
);

CREATE TABLE IF NOT EXISTS UnitAmmenities (
    PropertyId INTEGER,
    UnitAmenities TEXT,
    FOREIGN KEY (PropertyId) REFERENCES ApartmentUnit(UnitId)
);
