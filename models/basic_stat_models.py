
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import math
import numpy as np

class BasicStatModels:

    def __init__(self, file):
        self.main_data = pd.read_csv(file)

    def prepare_data(self):
    
        self.main_data = self.main_data.drop('PropertyId', axis=1)
        # Ensure all data is numeric before calculating the correlation matrix
        self.main_data = self.main_data.apply(pd.to_numeric, errors='ignore')
        lower_cap = self.main_data['MaxRent'].quantile(0.05)
        upper_cap = self.main_data['MaxRent'].quantile(0.95)
        self.main_data['MaxRent'] = self.main_data['MaxRent'].clip(lower_cap, upper_cap)

    def histogram(self, ax):
        ax.hist(self.main_data['MaxRent'], bins='auto', color='blue', alpha=0.7)
        ax.set_title('Distribution of Rent Prices')
        ax.set_xlabel('Rent Price')
        ax.set_ylabel('Frequency')
        ax.grid(axis='y', alpha=0.75)

    def scatter_plot(self, ax):
        X = self.main_data[['SquareFootage']]
        y = self.main_data['MaxRent']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        ax.scatter(self.main_data['SquareFootage'], self.main_data['MaxRent'], color='grey')
        ax.plot(X_test, y_pred, color='red', linewidth=3, label='Predicted Rent')
        ax.set_xlabel('Square Footage')
        ax.set_ylabel('Max Rent')
        ax.set_title('Rent vs. Square Footage')


    def correlation_matrix(self, ax):
        corr_matrix = self.main_data.corr()
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
        ax.set_title('Correlation Matrix')

    def neighborhood_heat_map(self):
        neighborhoods = self.main_data.groupby('Neighborhood_Label').agg(
        MaxRent_Mean=('MaxRent', 'mean'),
        MaxRent_Std=('MaxRent', 'std'),
        Latitude_Mean=('Latitude', 'mean'),
        Longitude_Mean=('Longitude', 'mean')
        )
        for index, row in neighborhoods.iterrows():
            print(f"Neighborhood: {index}")
            print(f"MaxRent Mean: {row['MaxRent_Mean']}, MaxRent Std: {row['MaxRent_Std']}")
            print(f"Latitude Mean: {row['Latitude_Mean']}, Longitude Mean: {row['Longitude_Mean']}")
            print() 

    def flexible_plotting_system(self):
        plot_functions = [self.histogram, self.scatter_plot, self.correlation_matrix]
        num_plots = len(plot_functions)
        cols = 2  
        rows = math.ceil(num_plots / cols)

        fig, axs = plt.subplots(rows, cols, figsize=(cols * 6, rows * 6))

        for i, plot_func in enumerate(plot_functions):
            if rows > 1:
                ax = axs[i // cols, i % cols]
            else:  # If there's only one row, axs is a 1D array
                ax = axs[i]
            plot_func(ax)
        
        plt.tight_layout()
        plt.show()

    def main(self):
        self.prepare_data()
        self.neighborhood_heat_map()
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None): print(self.main_data.describe())
        self.flexible_plotting_system()

if __name__ == '__main__':
    stat = BasicStatModels('../data/processed_data/austin_tx_processed.csv')
    stat.main()

