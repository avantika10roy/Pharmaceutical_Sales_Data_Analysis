import warnings
from prophet import Prophet
from logger import LoggerSetup
import plotly.exceptions as pe
import plotly.graph_objects as go

warnings.filterwarnings('ignore')

class TSAForecasting:
    def __init__(self, input_data = None):
        """
        The class TSAForecasting uses Facebook Prophet to forecast future sales trends based on historical time series data from different countries.
        Arguments:
        ----------
            - input_data (pd.DataFrame) : The dataset containing time-series sales data.
        """
        self.data     = input_data
        self.model    = None
        self.forecast = None
        self.log      = LoggerSetup(logger_file = 'tsa_forecasting.log',
                                    logger_name = 'tsa_forecasting').get_logger()

    def data_organization(self):
        """
        Organizes and aggregates sales data for Poland and Germany by month.
        Returns:
        --------
            - poland_data (pd.DataFrame)  : Monthly aggregated sales data for Poland.
            - germany_data (pd.DataFrame) : Monthly aggregated sales data for Germany.
        """
        try:
            input_data   = self.data
            poland_data  = input_data[input_data['Country'] == 'Poland'][['Date', 'Sales']]
            germany_data = input_data[input_data['Country'] == 'Germany'][['Date', 'Sales']]

            germany_data = germany_data.groupby('Date')['Sales'].sum().reset_index()
            poland_data  = poland_data.groupby('Date')['Sales'].sum().reset_index()
            
            return poland_data, germany_data
        except Exception as e:
            self.log.error(f'Could not organize data: {e}')
        except FileNotFoundError as e:
            self.log.error(f'Could not find file: {e}')

    def fit_prophet_model(self, data, data_key=None, **prophet_params):
        """
        Fits a Facebook Prophet model on the given time series data.
        Arguments:
        ----------
            - data (pd.DataFrame or dict) : The dataset or dictionary of datasets to fit the model on.
            - data_key (str)              : The key to select data from dictionary if input is a dict.
            - **prophet_params            : Optional Prophet parameters to override default ones.
        Returns:
        --------
            - prophet_model (Prophet) : Fitted Prophet model.
        """
        try:
            default_params = {'yearly_seasonality' : True,
                            'weekly_seasonality' : False,
                            'daily_seasonality'  : False,
                            'seasonality_mode'   : 'multiplicative'}
            default_params.update(prophet_params)
            
            if isinstance(data, dict):
                if data_key is None:
                    print("Available data groups:")
                    for key in self.data.keys():
                        print(f"  - {key}")
                    return
                fit_data = data[data_key]
            else:
                fit_data = data
            
            self.prophet_model = Prophet(**default_params)
            self.prophet_model.fit(fit_data)
            
            print(f"Prophet model fitted successfully!")
            print(f"Training data shape: {fit_data.shape}")
            
            return self.prophet_model
        except Exception as e:
            self.log.error(f'Could not find model: {e}')
        except FileNotFoundError as e:
            self.log.error(f'Could not find file: {e}')

    def forecast_sales(self, data, horizon_months = 12, data_key = None):
        """
        Generates sales forecast using the previously fitted Prophet model.
        Arguments:
        ----------
            - data (pd.DataFrame or dict) : Dataset for which forecast is to be generated.
            - horizon_months (int)        : Number of months to forecast into the future.
            - data_key (str)              : Key to use if data is a dictionary.

        Returns:
        --------
            - forecast (pd.DataFrame) : DataFrame containing forecasted values with intervals.
        """
        try:
            if self.prophet_model is None:
                print("Please fit the model first!")
                return
            
            if isinstance(data, dict):
                historical_data = data[data_key] if data_key else list(data.values())[0]
            else:
                historical_data = data

            historical_data = historical_data.rename(columns = {"Date"  : "ds", 
                                                                "Sales" : "y"})
            future          = self.prophet_model.make_future_dataframe(periods = horizon_months, 
                                                                       freq    = 'M')
            self.forecast   = self.prophet_model.predict(future)
            
            print(f"Forecast generated for {horizon_months} months ahead!")
            return self.forecast
        except Exception as e:
            self.log.error(f'Could not forecast: {e}')
        except FileNotFoundError as e:
            self.log.error(f'Could not find file: {e}')

    def plot_forecast(self, historical_data = None, country_name = ""):
        """
        Plots the historical data along with the Prophet forecast and confidence interval.
        Arguments:
        ----------
            - historical_data (pd.DataFrame) : Historical sales data (optional).
            - country_name (str)             : Country name to show in title (optional).
        Returns:
        --------
            - fig (plotly.graph_objs._figure.Figure) : Forecast visualization.
        """
        try:
            if self.forecast is None:
                print("Please generate forecast first!")
                return

            fig = go.Figure()

            if historical_data is not None:
                fig.add_trace(go.Scatter(x    = historical_data['ds'],
                                        y    = historical_data['y'],
                                        mode = 'lines',
                                        name = 'Historical Sales',
                                        line = dict(color = 'black')))

            fig.add_trace(go.Scatter(x    = self.forecast['ds'],
                                    y    = self.forecast['yhat'],
                                    mode = 'lines',
                                    name = 'Prophet Forecast',
                                    line = dict(color = 'blue',
                                                dash  = 'dash')))

            fig.add_trace(go.Scatter(x          = self.forecast['ds'],
                                    y          = self.forecast['yhat_upper'],
                                    mode       = 'lines',
                                    line       = dict(width = 0),
                                    showlegend = False))

            fig.add_trace(go.Scatter(x         = self.forecast['ds'],
                                    y         = self.forecast['yhat_lower'],
                                    mode      = 'lines',
                                    fill      = 'tonexty',
                                    fillcolor = 'rgba(0,0,255,0.2)',
                                    line      = dict(width = 0),
                                    name      = 'Confidence Interval'))

            fig.update_layout(title       = f"Prophet Forecast for {country_name}" if country_name else "Prophet Sales Forecast",
                            xaxis_title = "Date",
                            yaxis_title = "Sales",
                            template    = "plotly_white")

            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
        except FileNotFoundError as e:
            self.log.error(f'Could not find file: {e}')

    def get_forecast_summary(self, data, perioDate = 12):
        """
        Generates a summary of the forecast, including total sales, average, growth rate, etc.
        Arguments:
        ----------
            - data (pd.DataFrame or dict) : Dataset used for fitting and forecasting.
            - perioDate (int)             : Number of months of forecast to summarize.
        Returns:
        --------
            - summary (dict)                 : Dictionary with forecast metrics.
            - future_forecast (pd.DataFrame) : Subset of forecasted future data.
        """
        try:
            if self.forecast is None:
                print("Please generate forecast first!")
                return

            historical_data = (data 
                               if not isinstance(data, dict) 
                               else list(data.values())[0])
            n_historical    = len(historical_data)

            future_forecast = self.forecast.iloc[n_historical:n_historical + perioDate]

            summary         = {'Total_Forecast_Sales'  : future_forecast['yhat'].sum(),
                               'Average_Monthly_Sales' : future_forecast['yhat'].mean(),
                               'Min_Expected_Sales'    : future_forecast['yhat_lower'].min(),
                               'Max_Expected_Sales'    : future_forecast['yhat_upper'].max(),
                               'Sales_Growth_Rate'     : ((future_forecast['yhat'].iloc[-1] / historical_data['y'].iloc[-1]) - 1) * 100}

            print("\n=== FORECAST SUMMARY ===")
            for key, value in summary.items():
                print(f"{key.replace('_', ' ')}: {value:,.2f}")

            return summary, future_forecast
        except FileNotFoundError as e:
            self.log.error(f'Could not find file: {e}')
        except Exception as e:
            self.log.error(f'Could not summarize forecast: {e}')
