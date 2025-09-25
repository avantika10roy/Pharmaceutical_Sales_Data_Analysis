import pandas as pd
from config import Config
import plotly.express as px
from logger import LoggerSetup
import plotly.exceptions as pe
from typing import List, Dict, Any

class SalesProductPerformance:
    def __init__(self, input_data : str):
        """
        The class SalesProductPerformance analyzes sales and product-level performance across channels, managers, countries, and teams.
        Arguments:
        ----------
            - input_data (pd.DataFrame) : The dataset that contains sales records.
        """
        self.input_data = input_data
        self.config     = Config()
        self.log        = LoggerSetup(logger_file = 'sales_product_performance.log',
                                      logger_name = 'sales_product_performance').get_logger()

    def top_product_by_rev(self) -> Dict:
        """
        Finds the top 10 products with the highest average revenue (sales).
        Returns:
        --------
            - pd.DataFrame : Top 10 products sorted by average sale value.
        """
        try:
            grouped = self.input_data.groupby('Product Name').agg(
                                                Avg_Price      = pd.NamedAgg(column  = "Price", 
                                                                             aggfunc = "mean"),
                                                Avg_Sale       = pd.NamedAgg(column  = "Sales", 
                                                                             aggfunc = "mean"),
                                                Avg_Units_Sold = pd.NamedAgg(column  = "Quantity", 
                                                                             aggfunc = "mean")).reset_index()
            top_n   = grouped.sort_values(by        = "Avg_Sale", 
                                        ascending = False).head(10)
            return top_n
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
    
    def top_sold_product(self, column_name : str) -> Dict:
        """
        Finds the top 10 products with the highest total quantity sold, grouped by a given column.
        Arguments:
        ----------
            - column_name (str) : Column by which to group (e.g., 'Product Name', 'Category').
        Returns:
        --------
            - pd.DataFrame : Top 10 groups sorted by total units sold.
        """
        try:
            grouped = self.input_data.groupby(column_name).agg(
                                                Total_Sale       = pd.NamedAgg(column  = "Sales", 
                                                                               aggfunc = "sum"),
                                                Total_Units_Sold = pd.NamedAgg(column  = "Quantity", 
                                                                               aggfunc = "sum")).reset_index()
            top_n   = grouped.sort_values(by        = "Total_Units_Sold", 
                                          ascending = False).head(10)
            
            return top_n
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
    
    def manager_performance(self, top : int = 3) -> Dict:
        """
        Analyzes average sales performance of sales managers.
        Arguments:
        ----------
            - top (int) : Number of top-performing managers to return. Default is 3.
        Returns:
        --------
            - pd.DataFrame : Top managers ranked by average sale value.
        """
        try:
            grouped = self.input_data.groupby('Sales Manager').agg(
                                                Avg_Sale       = pd.NamedAgg(column  = "Sales", 
                                                                             aggfunc = "mean"),
                                                Avg_Units_Sold = pd.NamedAgg(column  = "Quantity", 
                                                                             aggfunc = "mean")).reset_index()

            top_n   = grouped.sort_values(by        = "Avg_Sale", 
                                          ascending = False).head(top)
            return top_n
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')

    def best_sales_channel(self, top : int = 3) -> Dict:
        """
        Analyzes sales performance by channel and sub-channel.
        Arguments:
        ----------
            - top (int) : Number of top-performing channel combinations to return. Default is 3.
        Returns:
        --------
            - pd.DataFrame : Top channel and sub-channel combinations by average sales.
        """
        try:
            grouped = self.input_data.groupby(['Channel', 'Sub-channel']).agg(
                                                Avg_Sale       = pd.NamedAgg(column  = "Sales", 
                                                                             aggfunc = "mean"),
                                                Avg_Units_Sold = pd.NamedAgg(column  = "Quantity", 
                                                                             aggfunc = "mean")).reset_index()

            top_n   = grouped.sort_values(by        = "Avg_Sale", 
                                          ascending = False).head(top)
            return top_n
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
    
    def price_variation_by_country(self) -> Dict:
        """
        Analyzes price variation across countries for each product class.
        Returns:
        --------
            - dict : Dictionary with average product prices for Poland and Germany, grouped by product class.
        """
        try:
            result = {}

            for country in ['Poland', 'Germany']:
                country_data   = self.input_data[self.input_data['Country'] == country]
                if not country_data.empty:
                    avg_prices = country_data.groupby('Product Class')['Price'].mean()
                    result[f'{country} Price'] = avg_prices

            return result
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
    
    def price_variation_by_market(self) -> Dict:
        """
        Analyzes price variation across different sales markets (channels).
        Returns:
        --------
            - dict : Dictionary with average product prices in Hospital and Pharmacy markets.
        """
        try:
            result = {}

            for channel in ['Hospital', 'Pharmacy']:
                channel_data   = self.input_data[self.input_data['Channel'] == channel]
                if not channel_data.empty:
                    avg_prices = channel_data.groupby('Product Class')['Price'].mean()
                    result[f'{channel} Price'] = avg_prices

            return result
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')

    def team_performance(self) -> Dict:
        """
        Evaluates average sales performance by sales team and returns a visualization.
        Returns:
        --------
        - tuple :
            - pd.DataFrame                     : Average sales by sales team.
            - plotly.graph_objs._figure.Figure : Bar chart of team-wise sales performance.
        """
        try:
            data = self.input_data.groupby('Sales Team')['Sales'].mean().reset_index()
            
            fig = px.bar(data,
                        x       = 'Sales Team',
                        y       = 'Sales',
                        color   = 'Sales Team',
                        barmode = 'group')
            
            fig.update_layout(xaxis       = dict(type     = 'category',
                                                 tickmode = 'array',
                                                 tickvals = data['Sales Team'],
                                                 ticktext = data['Sales Team'],
                                                 tickson  = 'labels'),
                            bargap      = 0.3, 
                            bargroupgap = 0.1,
                            xaxis_title = 'Sales Team',
                            yaxis_title = 'Sales',
                            showlegend  = False)
            
            return data, fig
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
    
    def cross_market_performance(self) -> Dict:
        """
        Analyzes cross-channel performance for each product class using a funnel chart.
        Returns:
        --------
        - tuple :
            - pd.DataFrame                     : Average sales by product class and channel.
            - plotly.graph_objs._figure.Figure : Funnel chart of cross-market performance.
        """
        try:
            grouped = self.input_data.groupby(['Product Class', 'Channel'])['Sales'].mean().reset_index()
            grouped = grouped.sort_values(by        = 'Sales', 
                                          ascending = False)
            fig = px.funnel(grouped,
                            x     = 'Sales',
                            y     = 'Product Class',
                            color = 'Channel')
            
            return grouped, fig
        except pe.PlotlyError as e:
            self.log.error(f'Unable to plot data: {e}')
