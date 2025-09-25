import pandas as pd
from config import Config
import plotly.express as px
import plotly.exceptions as pe
from logger import LoggerSetup
import plotly.graph_objects as go
from typing import List, Dict, Any
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose

class TimeSeriesAnalysis:
    def __init__(self, input_data : str):
        """
        The class TimeSeriesAnalysis provides time-based analytical and visualization tools for exploring sales trends, decomposition, and growth patterns.
        Arguments:
        ----------
            - input_data (pd.DataFrame) : The dataset to be analyzed for time-series trends.
        """
        self.input_data = input_data
        self.config     = Config()
        self.log        = LoggerSetup(logger_file = 'time_series_analysis.log',
                                      logger_name = 'time_series_analysis').get_logger()

    def sale_trend(self) -> Any:
        """
        Generates a line chart showing total sales over time.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Line chart of daily total sales across all channels.
        """
        try:
            data_sorted = self.input_data.sort_values(by = 'Date')
            grouped     = data_sorted.groupby(['Date'])['Sales'].sum().reset_index()
            grouped     = pd.DataFrame(grouped)
            fig         = px.line(grouped,
                                x      = 'Date',
                                y      = 'Sales',
                                height = 500,
                                width  = 800,
                                title  = 'Overall Channel Sale in Four Years')
            
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def decompose_revenue(self) -> Any:
        """
        Performs seasonal decomposition (multiplicative model) on monthly sales data and visualizes the original series, trend, seasonality, and residual.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Subplot with decomposed components of sales.
        """
        try:
            data   = self.input_data.sort_values(by = 'Date')
            data   = data.groupby('Date')['Sales'].sum().reset_index()
            result = seasonal_decompose(data['Sales'], 
                                        model  = 'multiplication', 
                                        period = 12)

            # Create a Plotly subplot with 4 rows (original, trend, seasonal, residual)
            decomposition_plot = make_subplots(rows        = 4, 
                                            cols           = 1, 
                                            shared_xaxes   = True,
                                            subplot_titles = ("Original Series", 
                                                                "Trend", 
                                                                "Seasonal", 
                                                                "Residual"))

            # Original series
            decomposition_plot.add_trace(go.Scatter(x    = data.index, 
                                                    y    = data['Sales'],
                                                    mode = 'lines', 
                                                    name = 'Original',
                                                    line = dict(color = 'red')),
                                                    row  = 1, 
                                                    col  = 1)

            # Trend
            decomposition_plot.add_trace(go.Scatter(x    = data.index, 
                                                    y    = result.trend,
                                                    mode = 'lines', 
                                                    name = 'Trend',
                                                    line = dict(color = 'blue')),
                                                    row  = 2, 
                                                    col  = 1)

            # Seasonal
            decomposition_plot.add_trace(go.Scatter(x    = data.index, 
                                                    y    = result.seasonal,
                                                    mode = 'lines', 
                                                    name = 'Seasonal',
                                                    line = dict(color = 'green')),
                                                    row  = 3, 
                                                    col  = 1)

            # Residual
            decomposition_plot.add_trace(go.Scatter(x      = data.index, 
                                                    y      = result.resid,
                                                    mode   = 'lines', 
                                                    name   = 'Residual',
                                                    marker = dict(color = 'red')),
                                                    row    = 4, 
                                                    col    = 1)

            # Layout settings
            decomposition_plot.update_layout(height     = 400, 
                                             width      = 600,
                                             title_text = "Multiplicative Decomposition of Monthly Revenue (Period = 12)",
                                             showlegend = False)

            return decomposition_plot
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")

    def monthly_sales_trend_product(self) -> str:
        """
        Generates a line chart showing monthly sales trends per product class.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Line chart showing average sales by product class over time.
        """
        try:
            data_sorted = self.input_data.sort_values(by = 'Date')
            grouped     = data_sorted.groupby(['Date', 'Product Class'])['Sales'].mean()
            grouped_df  = pd.DataFrame(grouped)

            fig         = px.line(grouped_df,
                                x      = grouped_df.index.get_level_values('Date'),
                                y      = 'Sales',
                                color  = grouped_df.index.get_level_values('Product Class'),
                                height = 500,
                                width  = 800,
                                title  = 'Overall Channel Sale in Four Years')

            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def growth_rate_analysis(self, category: str) -> Any:
        """
        Analyzes yearly average sales growth across a specified category.
        Arguments:
        ----------
            - category (str) : Column name to analyze growth by (e.g., 'Channel', 'Sub-channel').
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Bar chart showing yearly sales grouped by selected category.
        """
        try:
            sorted_data = self.input_data.sort_values(by = 'Year')
            grouped     = sorted_data.groupby(['Year', 
                                               'Sub-channel', 
                                               'Channel', 
                                               'Product Class'])['Sales'].mean()
            grouped     = pd.DataFrame(grouped)
            fig         = px.bar(grouped,
                                x       = grouped.index.get_level_values('Year'),
                                y       = 'Sales',
                                color   = grouped.index.get_level_values(category),
                                barmode = 'group',
                                height  = 500,
                                width   = 800)
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def sales_team_yearly_growth(self) -> Any:
        """
        Generates a line chart showing the yearly sales trend for each sales team.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Line chart showing yearly average sales per sales team.
        """
        try:
            data    = self.input_data.sort_values(by = 'Year')
            grouped = data.groupby(['Year', 'Sales Team'])['Sales'].mean()
            grouped = pd.DataFrame(grouped)

            fig     = px.line(grouped,
                            x      = grouped.index.get_level_values('Year'),
                            y      = 'Sales',
                            color  = grouped.index.get_level_values('Sales Team'),
                            height = 500,
                            width  = 800,
                            title  = 'Yearly Sales Growth of Sales Teams')
            
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def customer_trend(self):
        """
        Analyzes the customer count trend over time by country.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Line chart showing monthly customer count by country.
        """
        try:
            data         = self.input_data.groupby(['Date', 'Country'])['Customer Name'].count().reset_index()
            data.columns = ['Date', 'Country', 'Customer Count (monthly)']
            data         = pd.DataFrame(data)
            fig          = px.line(data,
                                x      = 'Date',
                                y      = 'Customer Count (monthly)',
                                color  = 'Country',
                                title  = 'Customer Behaviour Trend',
                                height = 400,
                                width  = 800)
            
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")

    def moving_average_analysis(self, window = 1):
        """
        Computes the moving average of sales for each country over time.
        Arguments:
        ----------
            - window (int) : The number of periods to use for the moving average. Default is 1.
        Returns:
        --------
            - dict : A dictionary where each key is a country and the value is a DataFrame containing original sales and moving average.
        """
        try:
            unique_countries   = list(set(self.input_data['Country']))
            country_sales_data = dict()
            for country in unique_countries:
                country_sales                              = self.input_data[self.input_data['Country'] == country][['Date', 'Sales']]
                country_sales_sorted                       = country_sales.sort_values(by = 'Date')
                indexed_country_sales                      = country_sales_sorted.set_index('Date')
                aggregated_country_sales                   = indexed_country_sales.groupby(indexed_country_sales.index).mean()
                aggregated_country_sales['Moving_Average'] = aggregated_country_sales[['Sales']].rolling(window = window).mean()
                country_sales_data.update({country: aggregated_country_sales})

            return country_sales_data
        except Exception as e:
            self.log.error(f'Could not group data: {e}')
        except FileNotFoundError as e:
            self.log.error(f"Couldn't find data: {e}")
   