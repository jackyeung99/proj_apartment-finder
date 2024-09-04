import sqlite3
from src.utils.state_abbreviations import ABBR_TO_NAME
import pandas as pd
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    ''' General python file to handle all sql related functions '''
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
        ''' Insert Cities, if the city and state are already there update values.allows running the dataloader multiple times '''
        values = tuple(city.model_dump().values())
        self.execute_query('''
            INSERT INTO City (CityName, State, Population, Population_change, Population_males, Population_Females, Median_Resident_Age, Income_2022, Income_2020, per_capita_income_2022, per_capita_income_2020, Median_house_value_2022, Median_house_value_2020, Median_Gross_Rent_2022, Cost_of_living, Poverty_Percentage, Land_area, Population_Density, Tax_with_mortgage, Tax_no_mortgage, Unemployment) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(CityName, State) DO UPDATE SET
            Population=excluded.Population,
            Population_change=excluded.Population_change,
            Population_males=excluded.Population_males,
            Population_Females=excluded.Population_Females,
            Median_Resident_Age=excluded.Median_Resident_Age,
            Income_2022=excluded.Income_2022,
            Income_2020=excluded.Income_2020,
            per_capita_income_2022=excluded.per_capita_income_2022,
            per_capita_income_2020=excluded.per_capita_income_2020,
            Median_house_value_2022=excluded.Median_house_value_2022,
            Median_house_value_2020=excluded.Median_house_value_2020,
            Median_Gross_Rent_2022=excluded.Median_Gross_Rent_2022,
            Cost_of_living=excluded.Cost_of_living,
            Poverty_Percentage=excluded.Poverty_Percentage,
            Land_area=excluded.Land_area,
            Population_Density=excluded.Population_Density,
            Tax_with_mortgage=excluded.Tax_with_mortgage,
            Tax_no_mortgage=excluded.Tax_no_mortgage,
            Unemployment=excluded.Unemployment;
        ''', values)
        
       
    def insert_crime(self, crime, city_id):
        ''' insert crime values for each city, being careful to avoid duplicate years '''
        values = tuple(crime.model_dump().values()) + (city_id,)
        self.execute_query('INSERT OR IGNORE INTO CityCrime (Year, Murders, Rapes, Robberies, Assaults, Burglaries, Thefts, Auto_thefts, Arson, CityId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)


    def insert_complex(self, apartment_tuple):
        try:
            values = tuple(apartment_tuple.model_dump().values())
            self.execute_query('''
                INSERT INTO ApartmentComplex(ComplexId, Name, BuildingUrl, Latitude, Longitude, PriceMin, PriceMax, Address, Neighborhood, Zipcode, NumUnits, Source, Phone, CityId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ComplexId) DO UPDATE SET
                Name=excluded.Name,
                BuildingUrl=excluded.BuildingUrl,
                Latitude=excluded.Latitude,
                Longitude=excluded.Longitude,
                PriceMin=excluded.PriceMin,
                PriceMax=excluded.PriceMax,
                Address=excluded.Address,
                Neighborhood=excluded.Neighborhood,
                Zipcode=excluded.Zipcode,
                NumUnits=excluded.NumUnits,
                Source=excluded.Source,
                Phone=excluded.Phone,
                CityId=excluded.CityId;
            ''', values)
        except sqlite3.IntegrityError as e:
            logging.error(f"IntegrityError while inserting complex data: {e}")
        except Exception as e:
            logging.error(f"Error while inserting complex data: {e}")


    def insert_units(self, unit):
        ''' Insert or update unit for each complex. 
            Note: If a apartment has multiple units listed with the same id 
            they will only be counted once, this can be altered by removing code about condlict'''
        
        unit_dict = unit.model_dump()
        # convert isAvailable into boolean 0 or 1 
        unit_dict["IsAvailable"] = int(unit_dict["IsAvailable"])
        values = tuple(unit_dict.values())
        self.execute_query('''
            INSERT INTO ApartmentUnit(UnitId, MaxRent, ModelName, Beds, Baths, SquareFootage, Details, IsAvailable, ComplexId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(UnitId) DO UPDATE SET
            MaxRent=excluded.MaxRent,
            ModelName=excluded.ModelName,
            Beds=excluded.Beds,
            Baths=excluded.Baths,
            SquareFootage=excluded.SquareFootage,
            Details=excluded.Details,
            IsAvailable=excluded.IsAvailable,
            ComplexId=excluded.ComplexId;
        ''', values)

    def insert_amenities(self, amenity): 
        ''' Insert amenities, and avoiding inserting duplicate amenities'''
        values = tuple(amenity.model_dump().values())
        self.execute_query('''
            INSERT OR IGNORE INTO UnitAmenities(UnitId, UnitAmenity, subtype)
            VALUES (?, ?, ?)
        ''', values)

    def get_city_id(self, city, state_abbr):
        '''given a city and a state abbreviation find the city id '''
        state = ABBR_TO_NAME[state_abbr]
        self.execute_query("SELECT CityId FROM City WHERE CityName = ? AND State = ?", (city, state))
        result = self.fetch_one()
        return result[0] if result else None
    
    def retrieve_units(self, city, state_abbr):
        state_abbr = state_abbr.upper()
        city = city.title()
        city_id = self.get_city_id(city, state_abbr)  
        print(city_id)
       
        # Execute the SQL query with city_id as a parameter
        query = '''
            SELECT 
                u.UnitId,
                u.MaxRent AS RentPrice,  -- Target variable
                u.Beds,
                u.Baths,
                u.SquareFootage,
                u.ModelName,
                c.Latitude,
                c.Longitude,
                c.NumUnits,
                c.Neighborhood
            FROM 
                ApartmentUnit u
            JOIN 
                ApartmentComplex c ON u.ComplexId = c.ComplexId
            WHERE c.CityId = ?;
            '''
        
        self.execute_query(query, (city_id,))
        rows = self.fetch_all()
    
    
        columns = [
            'UnitId', 'RentPrice', 'Beds', 'Baths', 'SquareFootage', 
            'ModelName', 'Latitude', 'Longitude', 'NumUnits', 'Neighborhood'
        ]
        
        # Load data into a pandas DataFrame
        df = pd.DataFrame(rows, columns=columns)
        return df
    
    def retrieve_amenities(self, city, state_abbr):
        state_abbr = state_abbr.upper()
        city = city.title()
        city_id = self.get_city_id(city, state_abbr)  
     
        query = '''
            SELECT 
                u.UnitId,
                a.UnitAmenity,
                a.subtype
            FROM 
                ApartmentUnit u
            JOIN 
                ApartmentComplex c ON u.ComplexId = c.ComplexId
            LEFT JOIN 
                UnitAmenities a ON u.UnitId = a.UnitId
            WHERE 
                c.CityId = ?;
            '''
        
        # Assuming self.execute_query returns a list of tuples (rows) from the SQL query
        self.execute_query(query, (city_id,))
        rows = self.fetch_all()
   
        # Define column names that correspond to the SELECT statement
        columns = [
            'UnitId', 'UnitAmenity', 'subtype'
        ]
        
        # Load data into a pandas DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        return df
    


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
