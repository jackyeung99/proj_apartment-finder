import sys
import os 

import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, KFold
import joblib

class RentPricePredictor:
    
    def get_model(self, parameters):
        return xgb.XGBRegressor(objective='reg:squarederror',random_state=99, **parameters)

    def train_model(self, model, X_train, y_train):        
        
        return model.fit(X_train, y_train)

    def evaluate_model(self, model, X_test, y_test):
        # Make predictions on the test set
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        return mse
    
    def save_model(self, model, filename='XG_boosted_rent_predictor.pkl'):
        # Save the trained model to a file
        joblib.dump(model, filename)
        print(f"Model saved to {filename}")

    def tune_xgboost_hyperparameters(self,X, y, n_splits=5, n_iter=5):
        xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=99)
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'min_child_weight': [1, 3, 5],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0]
        }
        
        # Cross validation with standard k folds
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=99)
        
        random_search = RandomizedSearchCV(
            estimator=xgb_model,
            param_distributions=param_grid,
            n_iter=n_iter,
            scoring='neg_mean_squared_error',  
            cv=cv,
            verbose=1,
            n_jobs=1,  
            random_state=99
        )
        
        # Perform the hyperparameter search
        random_search.fit(X, y)
        
        # Get the best parameters, score, and model
        best_params = random_search.best_params_
        best_score = abs(random_search.best_score_) 
        best_model = random_search.best_estimator_

        return best_model, best_params, best_score




