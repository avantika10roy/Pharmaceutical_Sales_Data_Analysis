import os
import pandas as pd
from typing import Any
from logger import LoggerSetup

class DataHandler:
    def __init__(self):
        """
        The DataHandler class is used to handle data in any of the three formats (xlx, csv, xlsx) by loading and saving them in csv format.
        """
        self.log = LoggerSetup(logger_file = 'data_handler.log',
                               logger_name = 'data_handler').get_logger()

    def load_data(self, input_data : str = None):
        """
        The function is used to load dataset specifically in xlx, xlsx and csv formats.
        Arguments:
        ----------
        - input_data (str) : Data path of the file to be loaded.
        Returns:
        --------
        - data             : Returns the loaded dataset."""
        try:
            if hasattr(input_data, "name"):
                filename = input_data.name
            elif isinstance(input_data, str):
                filename = input_data
            else:
                raise TypeError("Unsupported input type for `input_data`")

            extension = os.path.splitext(filename)[1].lower()
            if extension == '.csv':
                data  = pd.read_csv(filepath_or_buffer = input_data)
                return data
            
            elif extension == ['.xlx', '.xlsx']:
                data  = pd.read_excel(filepath_or_buffer = input_data)
                return data
            
            else:
                self.log.warning("File not found. Please load file with extension: 'csv', 'xls', 'xlsx'.")

        except FileNotFoundError as e:
            self.log.error(f"Unable to find the document you're trying to load. {e}")

    def save_data(self, result : Any = None, output_file : str = None):
        """
        The function saves the manipulated dataset in a csv format.
        Arguments:
        ----------
        - result      (Any) : the manipulated (preprocessed) data.
        - output_file (str) : file path where the preprocessed data needs to be stored."""
        try:
            self.log.info('Saving file...')
            result.to_csv(output_file, encoding = 'utf-8', index = False)
            self.log.info(f'Saved results to {output_file}.')

        except Exception as e:
            self.log.error(f'Unable to save CSV. {e}')
                