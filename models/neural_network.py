import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
import pandas as pd

class NeuralNetworkRegressor:
    def __init__(self, numeric_features, categorical_features, target_column):
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.target_column = target_column
        self.preprocessor = self._create_preprocessor()
        self.model = None

    def _create_preprocessor(self):
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])
        return preprocessor

    def _split_data(self, X, y, test_size=0.3, random_state=42):
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def _build_model(self, input_shape):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(input_shape,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def fit(self, df, epochs=10, batch_size=32, validation_split=0.2):
        # handle outliers
        lower_cap = df[self.target_column].quantile(0.05)
        upper_cap = df[self.target_column].quantile(0.95)
        df[self.target_column] = df[self.target_column].clip(lower_cap, upper_cap)

        X = df.drop(self.target_column, axis=1)
        y = df[self.target_column]
        
        # Split data
        X_train_raw, X_test_raw, y_train, y_test = self._split_data(X, y)
        
        # Preprocess data
        X_train = self.preprocessor.fit_transform(X_train_raw)
        self.X_test = self.preprocessor.transform(X_test_raw)
        
        # Save y_test as an attribute for later use in evaluation
        self.y_test = y_test  # This line is added to ensure y_test is available as an attribute
        
        # Further split X_train and y_train into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=validation_split, random_state=42)
        
        # Ensure data is in dense format for Keras
        X_train = X_train.toarray()
        X_val = X_val.toarray()
        self.X_test = self.X_test.toarray()
        
        # Build and train the model
        self.model = self._build_model(X_train.shape[1])
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))


    def evaluate(self):
        if self.model is not None and self.X_test is not None and self.y_test is not None:
            test_loss = self.model.evaluate(self.X_test, self.y_test)
            print(f"Test Loss: {test_loss}")
        else:
            print("Model is not trained or test data is not available.")


    
if __name__ == '__main__':
    numeric_features = ['Latitude', 'Longitude', 'ReviewScore', 'Leisure', 'Technology', 'Services', 'Location', 'Fitness & Wellness', 'Safety & Security', 'Apartment_features', 'Appliances', 'Baths', 'Beds', 'SquareFootage']
    categorical_features = ['Neighborhood_Label']
    target_column = 'MaxRent'
    df = pd.read_csv('../data/processed_data/austin_tx_processed.csv')
    # Initialize the model
    nn_model = NeuralNetworkRegressor(numeric_features, categorical_features, target_column)

    # Assuming `df` is your DataFrame
    nn_model.fit(df)

    # Evaluate the model on the test set
    nn_model.evaluate()

    y_pred = nn_model.model.predict(nn_model.X_test).flatten()  # Flatten to convert predictions from 2D to 1D

    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(nn_model.y_test, y_pred, alpha=0.3)

    # Plot a diagonal line for reference
    plt.plot([min(nn_model.y_test), max(nn_model.y_test)], [min(nn_model.y_test), max(nn_model.y_test)], color='red')  # Diagonal line

    plt.title('Actual vs. Predicted Values')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.grid(True)
    plt.show()