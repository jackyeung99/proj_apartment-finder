import sys
import os 

import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, KFold
import joblib

class RentPricePredictor:
    def __init__(self, parameters=None):
        """Initialize the model with default or provided parameters."""
        self.parameters = parameters if parameters else {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3,
            'min_child_weight': 1,
            'subsample': 1.0,
            'colsample_bytree': 1.0,
            'random_state': 99
        }
        self.model = self.get_model()

    def get_model(self):
        """Returns an XGBoost model with the defined parameters."""
        return xgb.XGBRegressor(objective='reg:squarederror', **self.parameters)

    def set_model_parameters(self, new_params):
        """Updates model parameters and reinitializes the model."""
        self.parameters.update(new_params)
        self.model = self.get_model()

    def train_model(self, X_train, y_train):
        """Train the model and update self.model with the trained version."""
        self.model.fit(X_train, y_train)
        return self.model

    def evaluate_model(self, X_test, y_test):
        """Evaluate the model on test data and return the MSE."""
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        return mse

    def save_model(self, filename='XG_boosted_rent_predictor.pkl'):
        """Save the trained model to a file."""
        joblib.dump(self.model, filename)
        print(f"Model saved to {filename}")

    def load_model(self, filename='XG_boosted_rent_predictor.pkl'):
        """Load a previously saved model."""
        self.model = joblib.load(filename)
        print(f"Model loaded from {filename}")

    def tune_xgboost_hyperparameters(self, X, y, n_splits=5, n_iter=5):
        """Perform hyperparameter tuning using RandomizedSearchCV."""
        xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=99)

        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'min_child_weight': [1, 3, 5],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0]
        }

        # K-Fold cross-validation
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=99)

        random_search = RandomizedSearchCV(
            estimator=xgb_model,
            param_distributions=param_grid,
            n_iter=n_iter,
            scoring='neg_mean_squared_error',
            cv=cv,
            verbose=1,
            n_jobs=-1,  # Use all available cores
            random_state=99
        )

        # Perform the hyperparameter search
        random_search.fit(X, y)

        # Update model with best found parameters
        best_params = random_search.best_params_
        best_score = abs(random_search.best_score_)  # Convert negative MSE to positive
        self.set_model_parameters(best_params)  # Update model with tuned parameters

        print(f"Best Hyperparameters: {best_params}")
        print(f"Best Cross-Validation MSE: {best_score:.4f}")

        return self.model, best_params, best_score


