import numpy as np
import pandas as pd
import seaborn as sns
from logger import LoggerSetup
import matplotlib.pyplot as plt

class Preprocessor:
    def __init__(self, input_data : str = None):
        """
        The class Preprocessor manipulates the dataset to understand the data as well as handle missing or erroenous inputs in the dataset.
        Arguments:
        ----------
        - input_data (str) : The dataset that needs to be manipulated and processed.
        """
        self.input_data = input_data
        self.log        = LoggerSetup(logger_file = 'preprocessor.log',
                                      logger_name = 'preprocessor').get_logger()
        
    def view_data(self):
        """
        The function displays the first 10 rows of data in a tabular format.
        Returns:
        --------
            - data : The input dataset that needs to be analyzed.
        """
        try:
            self.log.info('Displaying first 10 rows of data...')
            return self.input_data.head(10)
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def data_size(self) -> tuple:
        """
        The function is used to check the number of rows and columns present in the dataset.
        Return:
        -------
            - input_data.shape : A tuple with the total number of rows and columns."""
        try:
            self.log.info('Size of the dataset...')
            return self.input_data.shape
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def check_null(self):
        """
        This function checks if the dataset contains any null values in each column.
        Returns:
        --------
            - data_null : The total number of null values contained in the dataset
        """
        try:
            self.log.info('Total null values in each column...')
            return self.input_data.isnull().sum().sum()
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def check_unique_values(self) -> dict:
        """
        The function checks the number of unique values in each column.
        Returns:
        --------
            - unique_count (dict) : Dictionary containing the count of each unique value in each column of the dataset.
        """
        try:
            self.log.info('Total number of unique values in each column...')
            unique_counts = self.input_data.nunique()
            return unique_counts.reset_index().rename(columns={'index': 'Column', 0: 'Unique Count'})
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def check_duplicates(self):
        """
        The function checks how many rows are duplicates in the dataset.
        Returns:
        --------
            - duplicated rows : the count of the duplicated rows in the dataset.
        """
        try:
            self.log.info('Checking for duplicate rows...')
            return self.input_data.duplicated().sum()
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    # Use if duplicate values are present
    def remove_duplicate_rows(self):
        """
        This function is used if the data contains duplicate rows to remove them, therefore handling redundancy issues.
        Returns:
        --------
            - drop_duplicates : the dataset free from duplicate data inputs
        """
        try:
            self.log.info('Removing duplicate rows...')
            return self.input_data.drop_duplicates()
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def check_column_types(self):
        """
        The function checks the datatype of all the values present in each column.
        Returns:
        --------
            - data_dtypes : A table of all the datatypes of each column
        """
        try:
            self.log.info('Types of values present in each column...')
            return self.input_data.dtypes
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def correct_spelling(self, original : str, column : str, replace : str):
        """
        The function corrects the spelling of words in columns.
        Arguments:
        ----------
            - original (str) : The original word in the dataset column
            - column   (str) : The column where the word exists
            - replace  (str) : The words used to replace the original word

        Returns:
        --------
            - input_data : The dataset with the editted values
        """
        try:
            self.input_data[column] = self.input_data[column].replace({original : replace})
            return self.input_data
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")
    
    def rename_columns(self, original, renamed):
        """
        The function used to rename the columns of the dataset.
        Arguments:
        ----------
            - original (str) : The original name of the column in the dataset
            - renamed  (str) : The new name that replacs the original column name
        Returns:
        --------
            - input_data : The dataset with renamed columns
        """
        try:
            self.input_data = self.input_data.rename(columns = {original : renamed})
            return self.input_data
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def checking_outliers(self, column_name : str = None):
        """
        The function checks the outliers present in the numerical columns of the dataset.
        Arguments:
        ----------
            - column_name (str) : the name of the numerical column to check the outlier for.
        Returns:
        --------
            - boxplot (plot) : The plot depicting the outliers present in the dataset."""
        # Column name from quantity, price and sale
        try:
            sns.boxplot(self.input_data[column_name])
            plt.title(f"Outliers in {column_name}")
            plt.show()
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def count_outliers_iqr(self):
        """
        The function counts the number of outliers found in the dataset using Inter Quartile Range.
        Returns:
        --------
            - outlier_count (int) : the total number of outliers present in the dataset
        """
        try:
            outlier_count   = 0
            for column in self.input_data.select_dtypes(include = np.number).columns:
                q1          = self.input_data[column].quantile(0.25)
                q3          = self.input_data[column].quantile(0.75)
                iqr         = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                # Count outliers for the current column
                column_outliers = ((self.input_data[column] < lower_bound) | (self.input_data[column] > upper_bound)).sum()
                outlier_count  += column_outliers
            return outlier_count
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")

    def drop_columns(self, column):
        """
        The function drops/removes the unnecessary columns from the dataset.
        Arguemnts:
        ----------
            - column (str) : The name of the column that needs to be removed
        Returns:
        --------
            - input_data : the dataset with the column removed"""
        try:
            data            = self.input_data.drop(column, 
                                                   axis = 1)
            self.input_data = data
            return self.input_data
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")
    
    def add_date(self):
        """
        The function adds a new column to the dataset named 'Date', to help in Time Series Analysis.
        Returns:
        --------
            - input_data : The new dataset with the new 'Date' column
        """
        try:
            data          = self.input_data.copy()
            month_replace = {'January'   : 1, 
                             'February'  : 2, 
                             'March'     : 3, 
                             'April'     : 4, 
                             'May'       : 5, 
                             'June'      : 6, 
                             'July'      : 7, 
                             'August'    : 8, 
                             'September' : 9, 
                             'October'   : 10, 
                             'November'  : 11, 
                             'December'  : 12}
            
            data['Month']           = data['Month'].replace(month_replace)
            data['Date']            = pd.to_datetime(data['Year'].astype(str) + '-' + data['Month'].astype(str) + '-01')
            self.input_data['Date'] = data['Date']
            return self.input_data
        except FileNotFoundError as e:
            self.log.error(f'File not found {e}.')
        except Exception as e:
            self.log.error(f"File is empty {e}.")
    
