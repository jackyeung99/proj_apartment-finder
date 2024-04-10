import sqlite3
from utils.state_abbreviations import ABBR_TO_NAME

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish a database connection and cursor."""
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints

    def execute_query(self, query, params=()):
        """Execute a single SQL query."""
        if not self.conn:
            self.connect()
        self.cur.execute(query, params)

    def execute_many(self, query, param_list):
        """Execute a query against all parameter sequences."""
        if not self.conn:
            self.connect()
        self.cur.executemany(query, param_list)

    def fetch_one(self):
        """Fetch the next row of a query result set."""
        return self.cur.fetchone()

    def fetch_all(self):
        """Fetch all (remaining) rows of a query result set."""
        return self.cur.fetchall()

    def commit(self):
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()

    def rollback(self):
        """Roll back any changes since the last commit."""
        if self.conn:
            self.conn.rollback()


    def insert_city(self, city): 
        values = tuple(city.dict().values())
        self.execute_query('INSERT INTO City (CityName, State, Population, Population_change, Population_males, Population_Females, Median_Resident_Age, Income_2022, Income_2020, per_capita_income_2022, per_capita_income_2020, Median_house_value_2022, Median_house_value_2020, Median_Gross_Rent_2022, Cost_of_living, Poverty_Percentage, Land_area, Population_Density, Tax_with_mortgage, Tax_no_mortgage, Unemployment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
        return self.cur.lastrowid  # Returning the ID of the newly inserted city

    def insert_crime(self, crime):
        values = tuple(crime.dict().values())
        self.execute_query('INSERT INTO CityCrime (CityId, Year, Murders, Rapes, Robberies, Assaults, Burglaries, Thefts, Auto_thefts, Arson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)

    def insert_complex(self,apartment_tuple):
        self.execute_query('INSERT INTO ApartmentComplex(CityId, WebsiteId, Name, BuildingUrl, Latitude, Longitude, PriceMin, PriceMax, Address, Neighborhood, Zipcode, NumUnits, Source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', apartment_tuple)

    def insert_units(self, units):
        self.execute_many(' INSERT INTO ApartmentUnit(BuildingId,WebsiteId,MaxRent,ModelName,Beds,Baths,SquareFootage,Details) VALUES (?,?,?,?,?,?,?,?)',units)

    def insert_amenities(self, amenities): 
        self.execute_many(' INSERT INTO Unit-Amenities(Unit_Id,CommunityAmmenities) VALUES (?,?)', amenities)

    def get_city_id(self, city, state_abbr):
        state = ABBR_TO_NAME[state_abbr]
        self.execute_query("SELECT CityId FROM City WHERE CityName = ? AND State = ?", (city, state))
        result = self.fetch_one()
        return result[0] if result else None

    def commit_and_close(self):
        """Commit changes and close the connection."""
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit_and_close()
