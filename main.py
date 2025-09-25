from src import DataHandler, Preprocessor, DataAnalysis, ExploratoryDataAnalysis
from logger import LoggerSetup
import pandas as pd

class Main:
    def __init__(self, input_data):
        self.log          = LoggerSetup(logger_file = 'main.log',
                                        logger_name = 'main').get_logger()
        self.handler      = DataHandler()
        self.analyser     = DataAnalysis(input_data = '../data/preprocessed_data.csv')
        self.eda          = ExploratoryDataAnalysis(input_data = '../data/preprocessed_data.csv')
        self.data         = self.handler.load_data(input_data = input_data)
        self.preprocessor = Preprocessor(self.data)
        
    def run(self):
        self.log.info('Starting Description Steps...')
        self.preprocessor.view_data()
        self.preprocessor.data_size()
        self.preprocessor.check_null()
        self.preprocessor.check_unique_values()
        self.preprocessor.check_column_types()
        self.preprocessor.check_duplicates()
        self.preprocessor.add_date()

        self.log.info('Performing basic preprocessing...')
        data = self.preprocessor.drop_columns(column = 'Longitude')
        data = self.preprocessor.drop_columns(column = 'Latitude')
        data = self.preprocessor.correct_spelling(column   = 'Sales Team', 
                                                  original = 'Alfa', 
                                                  replace  = 'Alpha')
        data = self.preprocessor.remove_duplicate_rows()
        self.log.info('Preprocessing Complete.')
        
        self.log.info('Saving file...')
        self.handler.save_data(result      = data,
                               output_file = './data/preprocessed_data.csv')
        self.log.info(f'File saved to <path>')

        self.log.info('Performing Data Analysis...')
        self.analyser.data_description()

        column_list = ['Quantity', 'Price', 'Sales']
        skew_list = []
        for i in column_list:
            skew_list.append(self.analyser.express_skewness(i))

        kurt_list = []
        for i in column_list:
            kurt_list.append(self.analyser.express_kurtosis(i))

        result = pd.DataFrame({'skewness': skew_list,
                            'kurtosis': kurt_list})
            
        self.log.info(result)

        self.analyser.check_distribution(column = 'Sales')
        self.analyser.check_distribution(column = 'Quantity')
        self.analyser.check_distribution(column = 'Price')
        self.analyser.correlation_test()
        self.analyser.covariance_calculation(column1 = 'Quantity', column2 = 'Sales')
        self.analyser.covariance_calculation(column1 = 'Price', column2 = 'Sales')
        self.analyser.covariance_calculation(column1 = 'Quantity', column2 = 'Price')







if __name__ == '__main__':
    main = Main(input_data = 'data/pharma-data.csv')
    main.run()