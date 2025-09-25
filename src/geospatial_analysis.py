import pycountry
import numpy as np
import pandas as pd
from config import Config
import plotly.express as px
from logger import LoggerSetup
import plotly.exceptions as pe
import plotly.graph_objects as go
from typing import List, Dict, Any
from sklearn.cluster import KMeans
from plotly.subplots import make_subplots

class GeospatialAnalysis:
    def __init__(self, input_data : str):
        """
        The class GeospatialAnalysis performs spatial data analysis to explore revenue distribution, market penetration, and geographic sales patterns.
        Arguments:
        ----------
            - input_data (pd.DataFrame) : The dataset containing geographic and sales information.
        """
        self.input_data = input_data
        self.config     = Config()
        self.log        = LoggerSetup(logger_file = 'geospatial_analysis.log',
                                      logger_name = 'geospatial_analysis').get_logger()
    
    def revenue_concentration_by_city(self) -> Any:
        """
        Generates a smooth density map showing customer concentration using individual sales records
        to create a granular visualization with color gradients instead of large blue clusters.
        
        Returns:
        --------
        plotly.graph_objs._figure.Figure : Density map visualizing customer concentration hotspots.
        """
        try:
            data = self.input_data.copy()
            data['Log_Sales'] = np.log1p(data['Sales'])
            fig = px.density_mapbox(data,
                                    lat                    = "Latitude",
                                    lon                    = "Longitude",
                                    z                      = 'Log_Sales',
                                    radius                 = 6,
                                    center                 = {"lat" : 51.5, 
                                                              "lon" : 15},
                                    zoom                   = 4.5,
                                    mapbox_style           = "open-street-map",
                                    hover_data             = ["Sales"],
                                    hover_name             = "City",
                                    opacity                = 0.7)
            
            fig.update_coloraxes(colorbar_title = "Revenue<br>Density")
            
            fig.update_layout(
                margin = {"r" : 0, 
                          "t" : 0, 
                          "l" : 0, 
                          "b" : 0},
                title  = {'text'    : "Customer Concentration Map",
                          'x'       : 0.5,
                          'xanchor' : 'center'})

            return fig

        except Exception as e:
            self.log.error(f"Couldn't plot customer concentration data: {e}")

    def performance_analysis(self) -> Any:
        """
        Compares top 20 and bottom 20 performing cities based on total sales.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Subplot with two bar charts for top and bottom performing cities.
        """
        try:
            data      = self.input_data.copy()
            data      = data.groupby(['City'])['Sales'].sum().reset_index()
            data      = data.sort_values(by        = 'Sales', 
                                         ascending = False)
            data      = pd.DataFrame(data)
            top_20    = data.head(20)
            bottom_20 = data.tail(20)

            performance_comparison = make_subplots(rows           = 1,
                                                   cols           = 2,
                                                   subplot_titles = ("Top 20 Cities", "Bottom 20 Cities"))
            performance_comparison.add_trace(go.Bar(x     = top_20['City'],
                                                    y     = top_20['Sales']),
                                                    row   = 1,
                                                    col   = 1)
            performance_comparison.add_trace(go.Bar(x   = bottom_20['City'],
                                                    y   = bottom_20['Sales']),
                                                    row = 1,
                                                    col = 2)
            
            performance_comparison.update_layout(height     = 400,
                                                 width      = 600,
                                                 title_text = "Performance Comparison",
                                                 showlegend = False)
            return performance_comparison
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")

    def market_penetration(self) -> Any:
        """
        Visualizes the customer distribution across countries using a pie chart.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Pie chart of customer count per country.
        """
        try:

            data         = self.input_data.groupby('Country')['Customer Name'].nunique().reset_index()
            data.columns = ['Country', 'Customer Count']
            data         = pd.DataFrame(data)
            fig          = px.pie(data,
                                  values = 'Customer Count',
                                  names  = 'Country',
                                  color  = 'Country',
                                  title  = 'Market Penetration in each Country',
                                  height = 500,
                                  width  = 500)
            return fig
        
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")

    def optimize_territories(self) -> Any:
        """
        Applies KMeans clustering to assign sales territories based on latitude, longitude, and sales.
        Returns:
        --------
            - pd.DataFrame           : The dataset with an additional 'Territory' column indicating assigned cluster.
            - sklearn.cluster.KMeans : Fitted KMeans clustering model.
        Raises:
        -------
            - ValueError : If required fields ('Latitude', 'Longitude', 'Sales') are missing in the dataset.
        """
        try:
            data = self.input_data.copy()

            if not {'Latitude', 'Longitude', 'Sales'}.issubset(data.columns):
                raise ValueError("Dataset must have Latitude, Longitude, and Sales columns")

            features          = data[['Latitude', 'Longitude', 'Sales']].copy()
            features['Sales'] = (features['Sales'] - features['Sales'].mean()) / features['Sales'].std()
            kmeans            = KMeans(n_clusters=data['Sales Team'].nunique(), random_state=42)
            data['Territory'] = kmeans.fit_predict(features)

            return data, kmeans
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")
    
    def visualize_territories(self, clustered_data) -> Any:
        """
        Visualizes the optimized sales territories on a Mapbox scatter map.
        Arguments:
        -----------
            - clustered_data : pd.DataFrame Dataset containing 'Latitude', 'Longitude', 'Sales', and 'Territory' columns.
        Returns:
        --------
            - plotly.graph_objs._figure.Figure : Scatter map visualizing assigned sales territories by cluster.
        Raises:
        -------
            - ValueError : If required fields ('Latitude', 'Longitude', 'Sales', 'Territory') are missing in the dataset.
        """
        try:
            # Ensure 'Sales' is non-negative for size
            clustered_data          = clustered_data.copy()
            clustered_data['Sales'] = clustered_data['Sales'].clip(lower = 0.1)

            fig = px.scatter_mapbox(clustered_data,
                                    lat          = 'Latitude',
                                    lon          = 'Longitude',
                                    color        = 'Territory',
                                    size         = 'Sales',
                                    hover_name   = 'City',
                                    hover_data   = ['Country', 
                                                    'Sales'],
                                    zoom         = 4,
                                    mapbox_style = "open-street-map",
                                    title        = "Optimized Sales Territories")
            return fig
        except pe.PlotlyError as e:
            self.log.error(f"Couldn't plot data: {e}")