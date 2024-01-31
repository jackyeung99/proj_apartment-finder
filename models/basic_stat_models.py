
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


class basic_stat_models:
    
    def __init__(self, file):
        self.units = pd.read_csv(file)

    def prepare_data(self):
        # Convert 'MaxRent' to numeric and handle 'SquareFootage'
        self.units['MaxRent'] = pd.to_numeric(self.units['MaxRent'], errors='coerce')

        # Drop NaN values that may have resulted from conversion errors
        self.units.dropna(subset=['MaxRent', 'SquareFootage'], inplace=True)

    def main(self):
        self.prepare_data()

        # Creating subplots
        fig, axs = plt.subplots(1, 2, figsize=(20, 6))

        # Histogram
        axs[0].hist(self.units['MaxRent'], bins='auto', color='blue', alpha=0.7)
        axs[0].set_title('Distribution of Rent Prices')
        axs[0].set_xlabel('Rent Price')
        axs[0].set_ylabel('Frequency')
        axs[0].grid(axis='y', alpha=0.75)

        # Linear Regression
        X = self.units[['SquareFootage']]
        y = self.units['MaxRent']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        axs[1].scatter(X_test, y_test, color='black', label='Actual Rent')
        axs[1].plot(X_test, y_pred, color='blue', linewidth=3, label='Predicted Rent')
        axs[1].set_xlabel('Square Footage')
        axs[1].set_ylabel('Rent Price')
        axs[1].set_title('Linear Regression: Rent Price vs. Square Footage')
        axs[1].legend()

        # Display the plots side by side
        plt.show()

if __name__ == '__main__':
    stat = basic_stat_models('../test.csv')
    stat.main()