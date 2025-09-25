import numpy as np
import pandas as pd
import plotly.express as px
from logger import LoggerSetup
import plotly.exceptions as pe
import plotly.graph_objects as go
from scipy.stats import chisquare
from typing import List, Dict, Any
from itertools import combinations
from scipy.stats import skew, kurtosis

class DataAnalysis:
    def __init__(self, input_data : str = None):
        """
        The class DataAnalysis is used to perform exploratory data analysis including statistical description, KPI calculation, distribution testing, 
        correlation, and other statistical insights.
        Arguments:
        ----------
            - input_data (str) : The dataset to be analyzed.
        """
        self.input_data = input_data
        self.log        = LoggerSetup(logger_name = 'data_analysis',
                                      logger_file = 'data_analysis.log').get_logger()

    def data_description(self):
        """
        Generates a statistical summary of the dataset excluding location and time-related columns.
        Returns:
        --------
            - pd.DataFrame : A table showing count, mean, standard deviation, quartiles, etc., for each numeric column.
        """
        try:
            data = self.input_data.copy()
            data = data.drop(columns   = ['Longitude', 'Latitude', 'Year', 'Date']).describe()
            data = data.transpose()
            data = data.rename(columns = {'count' : 'Count', 
                                          'mean'  : 'Mean', 
                                          'std'   : 'Standard Deviation', 
                                          'min'   : 'Minimum', 
                                          '25%'   : '1st Quartile', 
                                          '50%'   : 'Median', 
                                          '75%'   : '3rd Quartile',
                                          'max'   : 'Maximum'})
            data = data.transpose()
            return data
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')
        
    def calculate_kpi(self):
        """
        Calculates key performance indicators like total sales, total price, total quantity, number of unique customers, average sale, and average price.
        Returns:
        --------
            - tuple : Formatted total sale, total customers, total quantity, total price, average sale, average price.
        """
        try:
            def format_number(n):
                if n >= 1_000_000_000:
                    return f"{n/1_000_000_000:.2f}B"
                elif n >= 1_000_000:
                    return f"{n/1_000_000:.2f}M"
                elif n >= 1_000:
                    return f"{n/1_000:.2f}k"
                else:
                    return f"{n:.2f}"
            
            total_sale     = sum(self.input_data['Sales'])
            total_price    = sum(self.input_data['Price'])
            total_quantity = sum(self.input_data['Quantity'])
            total_customer = self.input_data['Customer Name'].nunique()
            average_sale   = total_sale/len(self.input_data)
            average_price  = total_price/len(self.input_data)



            return (format_number(total_sale), 
                    format_number(total_customer), 
                    format_number(total_quantity), 
                    format_number(total_price), 
                    format_number(average_sale), 
                    format_number(average_price))
        
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')

    def express_skewness(self, column_name : str = None):
        """
        Calculates the skewness of a numeric column in the dataset.
        Arguments:
        ----------
            - column_name (str) : The column for which skewness is to be calculated.
        Returns:
        --------
            - float : Skewness value of the specified column.
        """
        try:
            skewness = skew(self.input_data[column_name])
            return skewness
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')

    def express_kurtosis(self, column_name : str = None):
        """
        Calculates the kurtosis of a numeric column in the dataset.
        Arguments:
        ----------
            - column_name (str) : The column for which kurtosis is to be calculated.
        Returns:
        --------
            - float : Kurtosis value of the specified column.
        """
        try:
            kurtosis_val = kurtosis(self.input_data[column_name])
            return kurtosis_val
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')

    def check_distribution(self, column = None):
        """
        Performs a chi-square goodness-of-fit test to check whether a categorical column follows a uniform distribution.
        Arguments:
        ----------
            - column (str) : The categorical column to be tested.
        Returns:
        --------
            - tuple : Chi-square statistic and the corresponding p-value.
        """
        try:
            observation        = self.input_data[column].value_counts().sort_index()
            total_observations = sum(observation)
            expected           = [total_observations/len(observation)]*len(observation)
            chi2stat , p_value = chisquare(observation, expected)

            return (chi2stat , p_value)
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')

    def correlation_test(self):
        """
        Calculates the Pearson correlation matrix for all numeric columns and displays it as an interactive heatmap.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : An interactive correlation heatmap.
        """
        try:
            data               = self.input_data.select_dtypes(include = ['number'])
            correlation_matrix = data.corr(method = 'pearson')

            # Create interactive heatmap
            fig = px.imshow(correlation_matrix,
                            text_auto              = True,
                            color_continuous_scale = 'RdYlGn',
                            title                  = 'Pearson Correlation Matrix')
            fig.update_layout(autosize = False, 
                              width    = 800, 
                              height   = 800)

            return fig
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')

    def covariance_calculation(self, columns):
        """
        Calculates the covariance matrix between specified numeric columns.
        Arguments:
        ----------
            - columns (list) : List of column names for which covariance is to be calculated.
        Returns:
        --------
            - pd.DataFrame : Covariance matrix of the specified columns.
        """
        try:
            results = []

            for col1, col2 in combinations(columns, 2):
                cov_matrix = np.cov(self.input_data[col1], 
                                    self.input_data[col2])
                covariance = cov_matrix[0, 1]
                results.append({"Column 1"   : col1,
                                "Column 2"   : col2,
                                "Covariance" : covariance})

            return pd.DataFrame(results)
        
        except FileNotFoundError as e:
            self.log.error(f'Could not find the file: {e}')
        except Exception as e:
            self.log.error(f'No numerical data found: {e}')