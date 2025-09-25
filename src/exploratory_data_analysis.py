import pandas as pd
from config import Config
import plotly.express as px
import plotly.exceptions as pe
from logger import LoggerSetup
from typing import List, Dict, Any

class ExploratoryDataAnalysis:
    def __init__(self, input_data : str):
        """
        The class ExploratoryDataAnalysis is responsible for creating visualizations and basic aggregations to understand the distribution and trends of sales data.
        Arguments:
        ----------
            - input_data (pd.DataFrame) : The dataset to be explored.
        """
        self.input_data = input_data
        self.config     = Config()
        self.log        = LoggerSetup(logger_name = 'exploratory_data_analysis',
                                      logger_file = 'exploratory_data_analysis.log').get_logger()
        
    def top_ns(self, column_name : str, top : int = 5) -> Any:
        """
        Returns top N groups based on average sale value and total quantity sold.
        Arguments:
        ----------
            - column_name (str) : The column to group by (e.g., 'Product Name').
            - top (int)         : Number of top records to return. Default is 5.

        Returns:
        --------
            - pd.DataFrame : Top N records sorted by average sale.
        """
        try:
            grouped = self.input_data.groupby(column_name).agg(
                                                Average_Sale     = pd.NamedAgg(column  = "Sales", 
                                                                               aggfunc = "mean"),
                                                Total_Units_Sold = pd.NamedAgg(column  = "Quantity", 
                                                                               aggfunc = "sum")).reset_index()

            top_n = grouped.sort_values(by        = "Average_Sale", 
                                        ascending = False).head(top)
            return top_n
        except Exception as e:
            self.log.error(f"Could not form a table: {e}")

    def pie_plot_distributor(self):
        """
        Creates a pie chart of distributors with a grouping threshold for 'Other'.
        Returns:
        --------
            - pd.DataFrame                     : Distribution of distributors with threshold applied.
            - plotly.graph_objs._figure.Figure : Pie chart visualization.
        """
        try:
            count_data         = self.input_data['Distributor'].value_counts().reset_index()
            count_data.columns = ['Distributor', 
                                'Count']
            threshold          = 6000
            category_name      = 'Other'
            summation          = count_data[count_data['Count']< threshold]['Count'].sum()
            other_row          = pd.DataFrame([{'Distributor' : category_name, 
                                                'Count'       : summation}])
            filtered_data      = count_data[count_data['Count']>= threshold]
            result = pd.concat([filtered_data, 
                                other_row], 
                                ignore_index = True)
            fig    = px.pie(result,
                            values = 'Count',
                            names  = 'Distributor',
                            color  = 'Distributor',
                            title  = 'Pie Chart to Determine Distributor Percentage',
                            height = 500,
                            width  = 500)

            return result, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
        
    def pie_plot_categories(self, column_name):
        """
        Creates a pie chart for a given categorical column based on value counts.
        Arguments:
        ----------
            - column_name (str) : The column to visualize.
        Returns:
        --------
            - pd.DataFrame                     : Distribution count for each category.
            - plotly.graph_objs._figure.Figure : Pie chart visualization.
        """
        try:
            count_data         = self.input_data[column_name].value_counts().reset_index()
            count_data.columns = [column_name, 'Count']

            fig = px.pie(count_data,
                        values = 'Count',
                        names  = column_name,
                        color  = column_name,
                        title  = f'Pie Chart to Determine {column_name} Percentage',
                        height = 500,
                        width  = 500)

            return count_data, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def pie_chart_on_sale(self, column_name):
        """
        Creates a pie chart showing the percentage of total sales per category.
        Arguments:
        ----------
            - column_name (str) : Column to group sales by.
        Returns:
        --------
            - pd.DataFrame                     : Total sales per category.
            - plotly.graph_objs._figure.Figure : Pie chart visualization of sales distribution.
        """
        try:
            column_sale = self.input_data.groupby(column_name, 
                                                  as_index = False)['Sales'].sum()
            fig = px.pie(column_sale,
                        values = 'Sales',
                        names  = column_name,
                        title  = f'Sale percentage based on {column_name}',
                        color  = column_name,
                        height = 500,
                        width  = 500)
            
            return column_sale, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")

    def line_chart_on_sale(self):
        """
        Creates a line chart showing sales over months across different years.
        Returns:
        --------
            - pd.DataFrame                     : Monthly aggregated sales per year.
            - plotly.graph_objs._figure.Figure : Line chart visualization.
        """
        try:
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December']

            # Group and reset
            grouped = self.input_data.groupby(['Year', 'Month'])['Sales'].sum().reset_index()

            # Convert 'Month' to a categorical type with proper order
            grouped['Month'] = pd.Categorical(grouped['Month'], 
                                              categories = month_order, 
                                              ordered    = True)

            # Sort by year and month
            grouped = grouped.sort_values(['Year', 
                                        'Month'])
            fig = px.line(grouped,
                        x       = 'Month',
                        y       = 'Sales',
                        color   = 'Year',
                        markers = True,
                        title   = 'Timeline of Sale over time per year',
                        height  = 500,
                        width   = 500)
            
            return grouped, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
 
    def grouped_bar_on_subchannel(self):
        """
        Creates a grouped bar chart showing total sales by Channel and Sub-channel.
        Returns:
        --------
            - pd.DataFrame                     : Sales grouped by channel and sub-channel.
            - plotly.graph_objs._figure.Figure : Grouped bar chart visualization.
        """
        try:
            grouped = self.input_data.groupby(['Channel', 'Sub-channel'])['Sales'].sum().reset_index()
            fig     = px.bar(grouped,
                            x       = 'Channel',
                            y       = 'Sales',
                            color   = 'Sub-channel',
                            barmode = 'group',
                            height  = 500)
            
            return grouped, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def sunburst_profit_in_channel(self):
        """
        Creates a sunburst chart showing hierarchical sales by Channel → Sub-channel → Product Class.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Sunburst chart visualization.
        """
        try:
            # profit = (self.input_data['Sales'] - self.input_data['Price'])/self.input_data['Sales']*100
            fig    = px.sunburst(self.input_data,
                                path   = ['Channel', 
                                          'Sub-channel', 
                                          'Product Class'],
                                values = 'Sales',
                                title  = 'Hierarchical Sale Analysis from Channel to Product Class using Sunburst',
                                height = 500,
                                width  = 500)
            
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def channel_sale(self):
        """
        Creates a line chart showing sales trends over time for each sales channel.
        Returns:
        --------
            - pd.DataFrame                     : Daily sales per channel.
            - plotly.graph_objs._figure.Figure : Line chart visualization of channel-wise sales.
        """
        try:
            data_sorted = self.input_data.sort_values(by = 'Date')
            grouped = data_sorted.groupby(['Date', 'Channel'])['Sales'].sum().reset_index()
            fig = px.line(grouped,
                        x      = 'Date',
                        y      = 'Sales',
                        color  = 'Channel',
                        height = 500,
                        width  = 800,
                        title  = 'Overall Channel Sale in Four Years')
            
            return grouped, fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")