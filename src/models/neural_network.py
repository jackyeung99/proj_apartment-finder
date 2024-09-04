

import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
import pandas as pd

class NeuralNetworkRegressor:

    def _build_neural_network_model(self, input_shape):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(input_shape,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def train_model(self, X_train, y_train, epochs=200, batch_size=32):
        # Train the neural network
        input_shape = X_train.shape[1]
        model = self._build_neural_network_model(input_shape)
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)
        return model

    def evaluate_model(self, model, X_test, y_test):
        # Evaluate the neural network
        test_loss = model.evaluate(X_test, y_test, verbose=0)
        return test_loss

    