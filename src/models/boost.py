import sys
import os 

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(repo_root)

from src.utils.database_manager import DatabaseManager

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

class RentPricePredictor:
    
    def __init__(self, city, state_abbr):
        self.city = city
        self.state_abbr = state_abbr
    
    def retrieve_units(self):
        # This function should be implemented based on the previous example.
        # It retrieves the data and returns a pandas DataFrame.
        self.db_manager = DatabaseManager(db_path='apf.db')
        df = DatabaseManager.retrieve_units(self.city, self.state_abbr)
        return df
    
    def prepare_data(self, df):
        # Drop columns that won't be used as features and handle missing values
        df = df.drop(columns=['UnitId', 'CityId', 'UnitAmenity', 'subtype'])
        df = df.dropna()
        
        # Separate features and target variable
        X = df.drop(columns=['RentPrice'])
        y = df['RentPrice']
        
        # Convert categorical data to one-hot encoding
        X = pd.get_dummies(X, drop_first=True)
        
        return X, y
    
    def train_model(self, X, y):
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create an XGBoost regressor model
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=6)
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Make predictions on the test set
        y_pred = model.predict(X_test)
        
        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse}")
        
        return model
    
    def save_model(self, model, filename='rent_price_model.pkl'):
        # Save the trained model to a file
        joblib.dump(model, filename)
        print(f"Model saved to {filename}")
    
    def run(self):
        # Step 1: Retrieve the data
        df = self.retrieve_units()
        
        # Step 2: Prepare the data
        X, y = self.prepare_data(df)
        
        # Step 3: Train the model
        model = self.train_model(X, y)
        
        # Step 4: Save the model
        self.save_model(model)

# Example usage
if __name__ == "__main__":


    db_manager = DatabaseManager(db_path='apf.db')
    df = db_manager.retrieve_amenities('austin', 'tx')
    print(df)    



    # predictor = RentPricePredictor(city='San Francisco', state_abbr='CA')
    # predictor.run()