import pandas as pd
import streamlit as st
from config import Config
import plotly.express as px
from logger import LoggerSetup
import plotly.graph_objects as go
from streamlit import session_state as state
from src import (DataHandler, 
                 DataAnalysis, 
                 Preprocessor, 
                 TSAForecasting,
                 GeospatialAnalysis, 
                 TimeSeriesAnalysis,
                 ExploratoryDataAnalysis, 
                 SalesProductPerformance)
                 

st.set_page_config(page_title            = "Pharmacuticals Sales Analysis Dashboard", 
                   layout                = "wide", 
                   initial_sidebar_state = "expanded")

# Upload Section
st.title("Pharmacuticals Sales Data Analysis and Forecasting Dashboard")
st.sidebar.header("Menu")

st.sidebar.subheader("Upload Your Pharma Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type = ["csv", "xls", "xlsx"])

if "data" not in st.session_state:
    st.session_state.df = None

# Show welcome page only if no file is uploaded
if uploaded_file is None:
    st.markdown("""
    ## Pharmacutical Company Sales Data Analysis and Risk Analysis Tool

    .....

    ### 🧾 What You Need to Do:
    1. Prepare a CSV, XLX or XLSX file containing your sales data.
    2. Make sure it includes columns like ....
    3. Upload the file using the uploader in the side pannel.
    4. Explore forecasts, model evaluations, and risk profiles.

    ---
    ....
    _The dashboard will automatically detect and process your data once the file is uploaded._

    ---
    """)
    st.stop()

class App:
    def __init__(self):
        self.config     = Config()
        self.handler    = DataHandler()
        self.log        = LoggerSetup(logger_file = 'app.log',
                                      logger_name = 'app').get_logger()

    def main_contents(self):
        if uploaded_file:
            with st.spinner("Processing your file.."):
                data = self.handler.load_data(uploaded_file)
                st.success("File processed successfully!")
                state.data            = data
                st.session_state.data = data

                st.markdown(self.config.CSS, unsafe_allow_html = True)

                self.original  = Preprocessor(input_data = data)
                processed_data = self.original.remove_duplicate_rows()
                processed_data = self.original.correct_spelling(original    = 'Alfa', 
                                                                column      = 'Sales Team', 
                                                                replace     = 'Alpha')
                processed_data = self.original.correct_spelling(original    = 'Antipiretics', 
                                                                column      = 'Product Class', 
                                                                replace     = 'Antipyretics')
                processed_data = self.original.rename_columns(original      = 'Name of Sales Rep', 
                                                              renamed       = 'Sales Representative')
                processed_data = self.original.rename_columns(original      = 'Manager', 
                                                              renamed       = 'Sales Manager')
                processed_data = self.original.add_date()

                self.preprocess = Preprocessor(input_data = processed_data)
                
                def create_filters(data):
                    # FILTERS FOR ADJUSTMENT

                    st.sidebar.subheader("Filter Your Data")
                    # Select Year Range
                    try:
                        selected_date_range = st.sidebar.multiselect("Select Year Range:",
                                                                    data['Year'].unique(),
                                                                    default = data['Year'].unique())
                        
                        filtered_data = data[data['Year'].isin(selected_date_range)]
                        return filtered_data
                    
                    except Exception as e:
                        self.log.warning(f"No data found due to : {repr(e)}")
                        return 'No Data Found. Please Select a date to ensure data is present.'
                    
                    
                
                self.filtered_data = create_filters(processed_data)

                if ((isinstance(self.filtered_data, pd.DataFrame)) and (len(self.filtered_data != 0))):

                    self.analyser      = DataAnalysis(input_data            = self.filtered_data)
                    self.eda           = ExploratoryDataAnalysis(input_data = self.filtered_data)
                    self.salesperf     = SalesProductPerformance(input_data = self.filtered_data)
                    self.geo           = GeospatialAnalysis(input_data      = self.filtered_data)
                    self.tsa           = TimeSeriesAnalysis(input_data      = self.filtered_data)
                    self.forecaster    = TSAForecasting(input_data          = self.filtered_data)


                    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Data Analysis', 
                                                            'Exploratory Data Analysis', 
                                                            'Sales and Product Analysis', 
                                                            'Time Series Analysis', 
                                                            'Geospatial Analytics'])
                    with tab1:
                        st.subheader('Data Overview')
                        with st.expander('Click to view data sample:', expanded = True):
                            try:
                                st.dataframe(self.original.view_data(),
                                            use_container_width = True)
                            except Exception as e:
                                self.log.error(f'Could not load dataframe: {e}')

                        st.subheader('General Data Summary')
                        with st.expander('Click to read summary insights:', expanded = True):
                            # Display Data Summary
                            try:
                                col1, col2, col3, col4, col5 = st.columns(spec = 5)
                                    
                                with col1:
                                    st.markdown("""
                                        <div class='stat-box'>
                                            <small>Observations:</small>
                                            <h3>{}</h3>
                                        </div>
                                    """.format(self.original.data_size()[0]), unsafe_allow_html = True)

                                with col2:
                                    st.markdown("""
                                        <div class = 'stat-box'>
                                            <small>Observable Attributes:</small>
                                            <h3>{}</h3>
                                        </div>
                                    """.format(self.original.data_size()[1]), unsafe_allow_html = True)

                                with col3:
                                    st.markdown("""
                                        <div class = 'stat-box'>
                                            <small>Missing Values:</small>
                                            <h3>{}</h3>
                                        </div>
                                    """.format(self.original.check_null()), unsafe_allow_html = True)

                                with col4:
                                    st.markdown("""
                                        <div class = 'stat-box'>
                                            <small>Duplicate Observations:</small>
                                            <h3>{}</h3>
                                        </div>
                                    """.format(self.original.check_duplicates()), unsafe_allow_html = True)

                                with col5:
                                    st.markdown("""
                                        <div class = 'stat-box'>
                                            <small>Anomalies:</small>
                                            <h3>{}</h3>
                                        </div>
                                    """.format(self.original.count_outliers_iqr()), unsafe_allow_html = True)
                            except Exception as e:
                                self.log.error(f'Could not load key metrics: {e}')

                            # Insights 
                            st.markdown(" ")                   
                            st.markdown(f"""
                                        ### Insights:
                                        - The dataset contains {self.original.data_size()[0]} observations and {self.original.data_size()[1]} observable attributes, suggesting a reasonably large dataset with enough variables to perform meaningful analysis.
                                        - The dataset does not contain any missing values suggesting that it is well maintained and updated.
                                        - There are {self.original.check_duplicates()} indicating some redundant entries.
                                        - A significant number of anomalies ({self.original.count_outliers_iqr()}) exist in the dataset. Their existance could be credited to intentional (event-driven) causes like mass purchases.
                                        """)

                        st.subheader('KPI Metrics')
                        with st.expander('Click to view KPI Metrics:', expanded = True): 
                            total_sale, total_customer, total_quantity, total_price, average_sale, average_price = self.analyser.calculate_kpi()
                            try:
                                col1, col2, col3, col4, col5, col6 = st.columns(spec = 6)

                                with col1:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Total Sale:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(total_sale), 
                                                unsafe_allow_html = True)

                                with col2:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Total Customer:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(total_customer), 
                                                unsafe_allow_html = True)

                                with col3:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Total Quantity:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(total_quantity), 
                                                unsafe_allow_html = True)

                                with col4:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Total Price:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(total_price), 
                                                unsafe_allow_html = True)
                                        
                                with col5:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Average Sale:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(average_sale), 
                                                unsafe_allow_html = True)
                                        
                                with col6:
                                    st.markdown("""**<div class='stat-box'>
                                                        <small>Average Price:</small>
                                                        <h3>{}</h3>
                                                    </div>**""".format(average_price), 
                                                unsafe_allow_html = True)
                            except Exception as e:
                                self.log.error(f'Could not load dataframe: {e}')

                            st.markdown(" ")       
                        
                            # Insights
                            st.markdown(f"""
                                        ### Insights
                                        1. **Strong Revenue Generation**

                                        - *Total Sale* : The company has made {total_sale} sales in the past {self.filtered_data['Year'].nunique()} years. This implies a healthy business size. Business focuses on high-value sales or large-order volumes.
                                        - *Average Sale* : On average, each customer contributes {average_sale} in sales, which is high, indicating a likely Business to Business or high-ticket Business to Customer business.

                                        2. **Average Unit Economics**

                                        - *Total Quantity Sold* : {total_quantity} units sold in the {self.filtered_data['Year'].nunique()} years, which is a significant amount. 
                                        - *Average Price per Unit* : On an average, the price of products purchased by the customers is {average_price} (mid-hundreds range) suggesting premium-priced pharmaceutical products.

                                        3. **Customer Behavior**
                                        - *Total Customers* : {total_customer} customers buy products fromt he company in the {self.filtered_data['Year'].nunique()} years, where the total number of times purchases have been made is around {self.preprocess.data_size()[0]}. This suggests repeated purchase from customers.
                                        - *Average Quantity sold per Customer* : {int(sum(self.filtered_data['Quantity']))/int(self.filtered_data['Customer Name'].nunique()):.2f} quantity of items are sold to each customer. This means customers are not just buying one or two units; they’re making bulk purchases (avg ~114 units), again suggesting enterprise-scale or wholesale transactions.

                                        4. **Sales Concentration**

                                        - With a high Average Sale per Customer ({average_sale}), there may be a concentration risk if a few customers make up a large portion of revenue.
                                        - Actionable Insight: Analyze revenue by customer segments to assess dependence on key accounts.
                                        """)

                        st.subheader('Unique Value and Statistical Summary')
                        with st.expander('Click to view unique value count and statistical summary:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                st.subheader('Unique Value Count')
                                try:
                                    st.dataframe(self.preprocess.check_unique_values())
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')

                            with subcol2:
                                st.subheader('Statistical Summary')
                                try:
                                    st.dataframe(self.analyser.data_description(), use_container_width = True)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')

                            # Insights 
                            st.markdown(f"""
                                    ### Insights on Number of Unique Values in each Column:
                                    The following count of unique values in each data feature suggests:
                                    - **Distributor**: There are {self.preprocess.check_unique_values().iloc[0,1]} unique values in the dataset. The values are a string of characters suggesting it could be a categorical data.
                                    - **Customer Name, Cities**: 'Customer Name' and 'Cities' features contain {self.preprocess.check_unique_values().iloc[1,1]} and {self.preprocess.check_unique_values().iloc[2,1]} unique values in the dataset, respectively. Despite the data not being numerical, their high number of unique values make it impossible to categorize them as categorical features. Therefore it is a high-cardinality categorical feature. The count of these features shall be useful to interpret some insights from the data.
                                    - **Country**: There are only {self.preprocess.check_unique_values().iloc[3,1]} unique values in this feature. Since the values are strings of characters it will be treated as categorical feature.
                                    - **Latitude, Longitude**: 'Latitude' and 'Longitude' features have {self.preprocess.check_unique_values().iloc[4,1]} and {self.preprocess.check_unique_values().iloc[5,1]} unique continuous numerical values respectively. They are helpful in conducting geospatial analysis of how the data is distributed across the countries.
                                    - **Channel, Sub-channel**: 'Channel' contains {self.preprocess.check_unique_values().iloc[6,1]} unqiue categorical (string) values and 'Sub-channel' contains {self.preprocess.check_unique_values().iloc[7,1]} unique features, also categorical.
                                    - **Product Name**: 'Product Name' also has high-cardinality with unique values counting to {self.preprocess.check_unique_values().iloc[8,1]}. Due to this property of the feature, it is suitable for the count of products within the data.
                                    - **Product Class**: With a total number of {self.preprocess.check_unique_values().iloc[9,1]} unique values, this feature helps understand the type of pharmaceutical products sold by the company and by how much.
                                    - **Quantity**: 'Quantity' is a numerical feature providing insights on how much each product has been sold. The total number of unique values within this feature is {self.preprocess.check_unique_values().iloc[10,1]}. Compared to the size of the dataset, the number of unique values are quite less suggesting similar buying pattern.
                                    - **Price, Sales**: 'Price' has a unique count of {self.preprocess.check_unique_values().iloc[11,1]}. This suggests some products are sold in the same price. 'Sales' on the other hand has a unique count of {self.preprocess.check_unique_values().iloc[12,1]} which suggests the total cost of purchase of each item considring how much (Quantity) has been bought.
                                    - **Month, Year, Date**: These three features, each {self.preprocess.check_unique_values().iloc[13,1]}, {self.preprocess.check_unique_values().iloc[14,1]} and {self.preprocess.check_unique_values().iloc[18,1]}, represent the time of purchase. These features are helpful in time series analysis. The unique count of 'Date' suggests full cycle has been completed in all four years, meaning all the months are present in the final year as well.
                                    - **Sales Representative, Sales Manager, Sales Team**: These 3 features (each {self.preprocess.check_unique_values().iloc[15,1]}, {self.preprocess.check_unique_values().iloc[16,1]} and {self.preprocess.check_unique_values().iloc[17,1]}) hold the names of the representatives, managers and teams responsible for sales. Due to the low cardinality, they are suitable for being categorical features.
                                    """)
                            st.markdown(f"""
                                        ### Insights on Data Statictical Summary:
                                        - The dataset contains {int(self.analyser.data_description().iloc[0,0])} transactions, indicating a robust sample size for reliable business analysis and forecasting models.
                                        - Average transaction quantity is {(self.analyser.data_description().iloc[1,0]):.2f} units with extremely high variability (standard deviation of {(self.analyser.data_description().iloc[2,0]):.2f}), suggesting a mix of small retail orders and large institutional bulk purchases.
                                        - Price points are well-distributed with an average of {(self.analyser.data_description().iloc[1,1]):.2f}, ranging from {int(self.analyser.data_description().iloc[3,1])} to {int(self.analyser.data_description().iloc[7,1])}, indicating diverse product portfolio spanning budget to premium segments.
                                        - Sales values show an enormous range from {(self.analyser.data_description().iloc[3,2]):.2f} to {(self.analyser.data_description().iloc[7,2]/1000000):.2f}M per transaction, with 75% of transactions below {(self.analyser.data_description().iloc[6,2]):.2f}, while top quartile drives significantly higher revenues.
                                        - The median transaction size ({(self.analyser.data_description().iloc[5,2]):.2f}) is much lower than the average ({(self.analyser.data_description().iloc[1,2]):.2f}), indicating most sales are smaller volume while a few large deals heavily impact overall performance.
                                        """)
                            
                        st.subheader('Skewness and Kurtosis')
                        with st.expander('Click to open the tables for skewness and kurtosis:', expanded = True):
                            col1, col2 = st.columns(spec = 2)
                            with col1:
                                try:
                                    s_for_sale     = self.analyser.express_skewness(column_name = 'Sales')
                                    s_for_quantity = self.analyser.express_skewness(column_name = 'Quantity')
                                    s_for_price    = self.analyser.express_skewness(column_name = 'Price')
                                    st.dataframe(pd.DataFrame({"Skewness" : {'Sales'       : [s_for_sale],
                                                                            'Quantity'     : [s_for_quantity],
                                                                            'Price'        : [s_for_price]}}))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')

                            with col2:
                                try:
                                    k_for_sale     = self.analyser.express_kurtosis(column_name = 'Sales')
                                    k_for_quantity = self.analyser.express_kurtosis(column_name = 'Quantity')
                                    k_for_price    = self.analyser.express_kurtosis(column_name = 'Price')
                                    st.dataframe(pd.DataFrame({"Kurtosis" : {'Sales'    : [k_for_sale],
                                                                            'Quantity'  : [k_for_quantity],
                                                                            'Price'     : [k_for_price]}}))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                            
                            st.markdown(f"""
                                        #### Insights on Skewness and Kurtosis:
                                        - **Sales Skewness ({s_for_sale:.2f})**: Extremely right-skewed distribution means the business is heavily dependent on occasional very large sales transactions, creating revenue concentration risk and making cash flow unpredictable.
                                        - **Quantity Skewness ({s_for_quantity:.2f})**: Most orders are small volume, but occasional massive bulk orders significantly impact inventory planning and supply chain management requirements.
                                        - **Price Skewness ({s_for_price:.2f})**: Nearly normal distribution suggests well-balanced pricing strategy across the product portfolio without extreme concentration in high or low-priced items.
                                        - **High Kurtosis Values (Sales: {k_for_sale:.2f}, Quantity: {k_for_quantity:.2f})**: Extreme outliers occur much more frequently than normal distribution would predict, indicating the business experiences unpredictable "black swan" events requiring robust risk management strategies.
                                        - **Price Kurtosis ({k_for_price:.2f})**: More uniform price distribution than normal, suggesting deliberate pricing strategy to avoid extreme price points that might alienate customer segments.
                                        """)

                    with tab2:
                        st.subheader("Top N's Based on Average Sale")
                        with st.expander("Click to view Top N's:", expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                st.subheader('Top 5 Distributors')
                                try:
                                    st.dataframe(self.eda.top_ns(column_name = 'Distributor'))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {self.eda.top_ns(column_name = 'Distributor').iloc[0,0]} dominates by a huge margin with an average sale of ~{(self.eda.top_ns(column_name = 'Distributor').iloc[0,1])/100000:.2f}M and {self.eda.top_ns(column_name = 'Distributor').iloc[0,2]/1000:.2f}k units sold, far higher than all other distributors.
                                            - {self.eda.top_ns(column_name = 'Distributor').iloc[1,0]} and {self.eda.top_ns(column_name = 'Distributor').iloc[2,0]} are the next tier, with average sales in the {(self.eda.top_ns(column_name = 'Distributor').iloc[2,1]/1000):.2f}k–{(self.eda.top_ns(column_name = 'Distributor').iloc[1,1]/1000):.2f}k range, but unit sales differ ({self.eda.top_ns(column_name = 'Distributor').iloc[1,0]} sells fewer units but at higher value).
                                            - {self.eda.top_ns(column_name = 'Distributor').iloc[2,0]} has the highest units sold ({self.eda.top_ns(column_name = 'Distributor').iloc[2,2]/100000:.2f}M), suggesting strong volume-based sales despite lower average revenue compared to Romaguera-Fay.
                                            - {self.eda.top_ns(column_name = 'Distributor').iloc[3,0]} and {self.eda.top_ns(column_name = 'Distributor').iloc[4,0]} contribute smaller shares, both in terms of average sale and unit volumes.
                                            - Distributor performance is highly skewed, with one giant ({self.eda.top_ns(column_name = 'Distributor').iloc[0,0]}), two mid-tier players, and two minor contributors.""")
                            with subcol2:
                                st.subheader('Top 5 Product Class')
                                try:
                                    st.dataframe(self.eda.top_ns(column_name = "Product Class"))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {self.eda.top_ns(column_name = 'Product Class').iloc[0,0]} lead with the highest average sale (~{self.eda.top_ns(column_name = 'Product Class').iloc[0,1]/1000:.2f}k) and over {self.eda.top_ns(column_name = 'Product Class').iloc[0,2]/100000:.2f}M units sold.
                                            - {self.eda.top_ns(column_name = 'Product Class').iloc[1,0]} are close in sales (~{self.eda.top_ns(column_name = 'Product Class').iloc[1,1]/1000:.2f}k) but significantly fewer units sold ({self.eda.top_ns(column_name = 'Product Class').iloc[1,2]/1000000:.2f}M).
                                            - {self.eda.top_ns(column_name = 'Product Class').iloc[2,0]} contribute moderately ({self.eda.top_ns(column_name = 'Product Class').iloc[2,1]/1000:.2f}k average sale, {self.eda.top_ns(column_name = 'Product Class').iloc[2,2]/1000000:.2f}M units sold).
                                            - {self.eda.top_ns(column_name = 'Product Class').iloc[3,0]} generate slightly lower average sales (~{self.eda.top_ns(column_name = 'Product Class').iloc[3,1]/1000:.2f}k) but surprisingly high unit sales (~{self.eda.top_ns(column_name = 'Product Class').iloc[3,2]/1000000:.2f}M).
                                            - {self.eda.top_ns(column_name = 'Product Class').iloc[4,0]} show the lowest revenue per sale (~{self.eda.top_ns(column_name = 'Product Class').iloc[4,1]/1000:.2f}k) but have the second-highest unit sales ({self.eda.top_ns(column_name = 'Product Class').iloc[4,2]/1000000:.2f}M).
                                            - Overall: High-volume categories ({self.eda.top_ns(column_name = 'Product Class').iloc[3,0]}, {self.eda.top_ns(column_name = 'Product Class').iloc[4,0]}) may rely on bulk low-value transactions, while {self.eda.top_ns(column_name = 'Product Class').iloc[0,0]} and {self.eda.top_ns(column_name = 'Product Class').iloc[1,0]} balance both value and volume.""")
                            st.markdown('__________________________')
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                st.subheader('Top 4 Sub-Channels')
                                try:
                                    st.dataframe(self.eda.top_ns(column_name = 'Sub-channel'))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {self.eda.top_ns(column_name = 'Sub-channel').iloc[0,0]} dominates sub-channels with the highest average sale (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[0,1]/1000:.2f}k) and ~{self.eda.top_ns(column_name = 'Sub-channel').iloc[0,2]/1000000:.2f}M units sold.
                                            - {self.eda.top_ns(column_name = 'Sub-channel').iloc[1,0]} follows with slightly lower average sales (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[1,1]/1000:.2f}k) but still high unit volume (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[1,2]/1000000:.2f}M).
                                            - {self.eda.top_ns(column_name = 'Sub-channel').iloc[2,0]} achieves a similar average sale (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[2,1]/1000:.2f}k) and {self.eda.top_ns(column_name = 'Sub-channel').iloc[2,2]/1000000:.2f}M units sold, competing closely with {self.eda.top_ns(column_name = 'Sub-channel').iloc[1,0]}s.
                                            - {self.eda.top_ns(column_name = 'Sub-channel').iloc[3,0]} has the lowest average sale (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[3,1]/1000:.2f}k) and lowest volume (~{self.eda.top_ns(column_name = 'Sub-channel').iloc[3,2]/1000000:.2f}M units).
                                            - Insight: {self.eda.top_ns(column_name = 'Sub-channel').iloc[0,0]} remains the strongest channel both in unit sales and value, while {self.eda.top_ns(column_name = 'Sub-channel').iloc[3,0]} is the weakest contributor.
                                            """)
                            with subcol2:
                                st.subheader('Top 4 Sales Team')
                                try:
                                    st.dataframe(self.eda.top_ns(column_name = 'Sales Team'))
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {self.eda.top_ns(column_name = 'Sales Team').iloc[0,0]} has the highest average sale (~{self.eda.top_ns(column_name = 'Sales Team').iloc[0,1]/1000:.2f}k), though its total units sold (~{self.eda.top_ns(column_name = 'Sales Team').iloc[0,2]/1000000:.2f}M) are lower than {self.eda.top_ns(column_name = 'Sales Team').iloc[2,0]}’s.
                                            - {self.eda.top_ns(column_name = 'Sales Team').iloc[1,0]} performs steadily with ~{self.eda.top_ns(column_name = 'Sales Team').iloc[1,1]/1000:.2f}k average sales and ~{self.eda.top_ns(column_name = 'Sales Team').iloc[1,2]/1000000:.2f}M units sold.
                                            - {self.eda.top_ns(column_name = 'Sales Team').iloc[2,0]} shows slightly lower average sales (~{self.eda.top_ns(column_name = 'Sales Team').iloc[2,1]/1000:.2f}k) but sells the most units (~{self.eda.top_ns(column_name = 'Sales Team').iloc[2,2]/1000000:.2f}M).
                                            - {self.eda.top_ns(column_name = 'Sales Team').iloc[3,0]} records the lowest average sale (~{self.eda.top_ns(column_name = 'Sales Team').iloc[3,1]/1000:.2f}k) and unit sales (~{self.eda.top_ns(column_name = 'Sales Team').iloc[3,2]/1000000:.2f}M).
                                            - Insight: {self.eda.top_ns(column_name = 'Sales Team').iloc[0,0]} excels in high-value deals, {self.eda.top_ns(column_name = 'Sales Team').iloc[2,0]} in high-volume sales, while {self.eda.top_ns(column_name = 'Sales Team').iloc[3,0]} lags behind both in value and volume.""")

                        st.subheader('Pie Plots to Determine Percentage of Total Sale')
                        with st.expander('Click to view pie plots for Distributor and Month-wise sale count:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res, chart = self.eda.pie_plot_distributor()
                                    st.plotly_chart(chart, use_container_width = True)   
                                    total = res['Count'].sum()  
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')         
                                st.markdown(f"""
                                            #### Insights:
                                            - {res.iloc[0,0]} dominates the distributor landscape with {res.iloc[0,1]/total*100:.2f}% market share, indicating significant market concentration
                                            - The top three distributors ({res.iloc[0,0]}, {res.iloc[1,0]} at {res.iloc[1,1]/total*100:.2f}%, and {res.iloc[2,0]} at {res.iloc[2,1]/total*100:.2f}%) control nearly 77% of the market
                                            - There's a long tail of smaller distributors with minimal market presence (many under 1%)
                                            - The market shows high consolidation with potential barriers to entry for new distributors
                                            """)
                                
                            with subcol2:
                                try:
                                    res1, plot = self.eda.pie_plot_categories(column_name = 'Month')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res1['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - Sales show relatively even distribution throughout the year with slight seasonal variations
                                            - {res1.iloc[0,0]}, {res1.iloc[1,0]} and {res1.iloc[1,0]} show marginally higher activity (around {res1.iloc[0,1]/total*100:.0f}% each)
                                            - No significant seasonal peaks or troughs, indicating stable year-round demand
                                            - The consistent monthly distribution suggests predictable revenue patterns
                                            """)
                            
                        with st.expander('Click to view pie plots for Country and Year-wise sale count:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Country')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total     = res1['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - {res.iloc[0,0]} represents the overwhelming majority at {res.iloc[0,1]/total*100}%, suggesting heavy geographic concentration
                                            - {res.iloc[1,0]} accounts for only {res.iloc[1,1]/total*100}%, indicating limited international diversification
                                            - The business appears to be primarily European-focused with minimal global presence
                                            - There may be untapped opportunities in other international markets
                                            """)

                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Year')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total     = res1['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                # Safeguard: Check how many rows are in the result
                                num_rows = len(res)

                                # Total for percentage calculations
                                total = res[res.columns[1]].sum()

                                # Build markdown content based on available data
                                insights = "#### Insights\n"
                                if num_rows >= 1:
                                    insights += (
                                        f"- **{res.iloc[0, 0]}** leads with **{res.iloc[0, 1]}** records, making up "
                                        f"**{res.iloc[0, 1]/total*100:.2f}%** of the total. This suggests it may have been a **peak year** "
                                        f"or that **data collection** was more comprehensive during this period.\n"
                                    )

                                if num_rows >= 2:
                                    insights += (
                                        f"- **{res.iloc[1, 0]}** ranks second with **{res.iloc[1, 1]}** records "
                                        f"(**{res.iloc[1, 1]/total*100:.2f}%**). While lower than {res.iloc[0, 0]}, it still indicates "
                                        f"a **significant level of activity** or data availability.\n"
                                    )

                                if num_rows >= 4:
                                    insights += (
                                        f"- **{res.iloc[2, 0]}** and **{res.iloc[3, 0]}** both show moderate presence with "
                                        f"**{res.iloc[2, 1]}** and **{res.iloc[3, 1]}** records respectively, each contributing "
                                        f"roughly **{res.iloc[2, 1]/total*100:.0f}%** and **{res.iloc[3, 1]/total*100:.0f}%**. "
                                        f"This suggests a **stabilization phase** or possibly **reduced data coverage**.\n"
                                    )
                                    insights += (
                                        f"- The **recent years** between **{res.iloc[2, 0]} and {res.iloc[3, 0]}** display a more **consistent but lower volume**, "
                                        f"indicating either **normalized operations**, **shifts in business focus**, or **changes in data recording practices** compared to {res.iloc[0, 0]}.\n"
                                    )

                                elif num_rows == 3:
                                    insights += (
                                        f"- **{res.iloc[2, 0]}** holds the third position with **{res.iloc[2, 1]}** records "
                                        f"(**{res.iloc[2, 1]/total*100:.0f}%**), showing a drop from the top years. "
                                        f"This could suggest **deceleration**, **stabilization**, or evolving data patterns.\n"
                                    )
                                    insights += (
                                        f"- Recent data from **{res.iloc[2, 0]}** shows lower representation compared to "
                                        f"the peak in **{res.iloc[0, 0]}**, potentially due to external factors or strategic shifts.\n"
                                    )

                                elif num_rows == 2:
                                    insights += (
                                        f"- Only two years are available. **{res.iloc[0, 0]}** remains dominant over **{res.iloc[1, 0]}**, "
                                        f"highlighting a clear **disparity**. This could reflect data availability or varying business intensity.\n"
                                    )

                                elif num_rows == 1:
                                    insights += (
                                        f"- With only **{res.iloc[0, 0]}** available, we can't compare across years. "
                                        f"This could be due to filtering or limited data. Consider selecting more years to analyze trends.\n"
                                    )

                                else:
                                    insights += "- No data available for the selected years. Please select at least one year to view insights.\n"

                                # Display
                                st.markdown(insights)

                        with st.expander('Click to view pie plots for Product Class and Channel-wise sale count:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Product Class')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total     = res1['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - Product portfolio is relatively balanced across therapeutic categories
                                            - {res.iloc[0,0]} lead at {res.iloc[0,1]/total*100:.2f}%, followed closely by {res.iloc[1,0]} ({res.iloc[1,1]/total*100:.2f}%) and {res.iloc[2,0]} ({res.iloc[2,1]/total*100:.2f}%)
                                            - All six product classes maintain reasonable market representation ({res.iloc[5,1]/total*100:.2f}-{res.iloc[0,1]/total*100:.2f}% range)
                                            - The diversified portfolio provides stability against category-specific market fluctuations
                                            """)
                                
                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Channel')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res1['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - Distribution is nearly evenly split between {res.iloc[0,0]} ({res.iloc[0,1]/total*100:.2f}%) and {res.iloc[1,0]} ({res.iloc[1,1]/total*100:.2f}%) channels
                                            - The balanced channel mix reduces dependency risk on either distribution method
                                            - Both channels show strong representation, suggesting effective multi-channel strategy
                                            - The near 50-50 split indicates successful market penetration in both retail and institutional segments
                                            """)
                                
                        with st.expander('Click to view pie plots for Sales Manager and Sales Team-wise sale count:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res1, plot = self.eda.pie_plot_categories(column_name = 'Sales Manager')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total     = res['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                
                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Sales Team')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                            st.markdown(f"""
                                        #### Insights
                                        - Teams show identical distribution to sales managers, with {res.iloc[0,0]} leading at {res.iloc[0,1]/total*100:.2f}%
                                        - {res.iloc[1,0]}, {res.iloc[2,0]}, and {res.iloc[3,0]} teams each handle {res.iloc[1,1]/total*100:.0f}% of activities
                                        - The pattern mirrors management structure, suggesting teams are directly aligned with managers
                                        - Uneven team utilization may indicate need for resource redistribution
                                        """)
                                
                        with st.expander('Click to view pie plots for Sub-channel and Sales Representative-wise sale count:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Sub-channel')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - Sub-channels are remarkably evenly distributed ({res.iloc[3,1]/total*100:.2f}-{res.iloc[0,1]/total*100:.2f}% each)
                                            - {res.iloc[0,0]} slightly leads at {res.iloc[0,1]/total*100:.2f}%, with {res.iloc[1,0]} close behind at {res.iloc[1,1]/total*100:.2f}%
                                            - The balanced distribution across {res.iloc[0,0]}, {res.iloc[1,0]}, {res.iloc[2,0]}, and {res.iloc[3,0]} suggests diversified customer base
                                            - Even distribution reduces risk from over-reliance on any single customer segment
                                            """)

                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_plot_categories(column_name = 'Sales Representative')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Count'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights
                                            - Sales representatives show remarkably even distribution ({res.iloc[12,1]/total*100:.2f}-{res.iloc[0,1]/total*100:.2f}% each)
                                            - All 13 representatives maintain nearly identical activity levels
                                            - The uniform distribution suggests effective workload management at the individual level
                                            - Consistent representative performance indicates good training and management processes
                                            """)
                                
                        st.subheader('Pie Chart on Sale')
                        with st.expander('Click to view pie charts:', expanded = True):
                            subcol1, subcol2 = st.columns(spec = 2)
                            with subcol1:
                                try:
                                    res, plot = self.eda.pie_chart_on_sale(column_name = 'Country')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Sales'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {res.iloc[0,0]} dominates the market with {res.iloc[0,1]/total*100:.2f}% of total sales, indicating either a highly concentrated geographic strategy or successful market penetration in this region
                                            - {res.iloc[1,0]} represents a minor market at only {res.iloc[1,1]/total*100:.2f}%, suggesting either an emerging opportunity for expansion or challenges in market penetration
                                            - Geographic risk concentration is high with over-reliance on a single country, creating vulnerability to local economic or regulatory changes
                                            - Market expansion opportunity exists in {res.iloc[1,0]} and potentially other European markets to diversify revenue streams
                                            - Resource allocation should consider whether the German market is at saturation point or if Polish operations need strategic investment
                                            """)

                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_chart_on_sale(column_name = 'Channel')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Sales'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {res.iloc[1,0]} channel slightly dominates with {res.iloc[1,1]/total*100:.2f}% of sales, representing the traditional retail pharmaceutical distribution model
                                            - {res.iloc[0,0]} channel accounts for {res.iloc[0,1]/total*100:.2f}%, showing strong institutional relationships and B2B sales capabilities
                                            - Channel balance is nearly even, indicating effective dual-channel strategy and market reach across both retail and institutional segments
                                            - Risk mitigation through diversification - neither channel represents over-dependence, protecting against sector-specific disruptions
                                            - Opportunity for channel optimization exists to potentially grow the higher-margin channel or improve efficiency in both
                                            """)
                            st.markdown('__________________________')
                            subcol1, subcol2 = st.columns(spec = 2)  
                            with subcol1:
                                try:
                                    res, plot = self.eda.pie_chart_on_sale(column_name = 'Product Class')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Sales'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {res.iloc[0,0]} lead product sales at {res.iloc[0,1]/total*100:.2f}%, indicating strong demand for pain management solutions in the target markets
                                            - Product portfolio is well-diversified across six therapeutic categories, reducing dependence on any single drug class
                                            - {res.iloc[4,0]} ({res.iloc[4,1]}%) and {res.iloc[5,0]} ({res.iloc[5,1]/total*100:.2f}%) show strong performance, suggesting opportunities in infection control and mental health segments
                                            - {res.iloc[2,0]} drugs represent the smallest segment at {res.iloc[2,1]/total*100:.2f}%, which may reflect geographic market focus rather than product weakness
                                            - Balanced distribution across categories ({res.iloc[2,1]/total*100:.2f}-{res.iloc[0,1]/total*100:.2f}% range) indicates a mature product portfolio with no significant gaps
                                            """)

                            with subcol2:
                                try:
                                    res, plot = self.eda.pie_chart_on_sale(column_name = 'Sub-channel')
                                    st.plotly_chart(plot, use_container_width = True)
                                    total = res['Sales'].sum()
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {res.iloc[3,0]} leads at {res.iloc[3,1]/total*100:.2f}%, confirming strong consumer-facing distribution network
                                            - {res.iloc[0,0]} procurement represents {res.iloc[0,1]/total*100:.2f}%, indicating significant public sector contracts and tender participation
                                            - {res.iloc[1,0]} sales ({res.iloc[1,1]/total*100:.2f}%) and {res.iloc[2,0]} sales ({res.iloc[2,1]/total*100:.2f}%) show balanced B2B distribution across different customer segments
                                            - Revenue diversification is strong across all sub-channels, reducing customer concentration risk
                                            """)
                            
                        st.subheader('Line Chart on Sale over time')
                        with st.expander('Click to view line charts:', expanded = True):
                            try:
                                res, plot = self.eda.line_chart_on_sale()
                                st.plotly_chart(plot, use_container_width = True)
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - Sales experienced significant volatility from {res.iloc[0,0]}-{res.iloc[47,0]}, with {res.iloc[35,0]} showing a dramatic spike in {res.iloc[31,1]} (reaching around {res.iloc[31,2]/1000000:.0f}M) followed by steep declines, suggesting either seasonal campaigns or market disruptions.
                                        - A rapid decline is seen in {res.iloc[12,0]}'s sale from {res.iloc[33,1]} to {res.iloc[35,1]} going from over {res.iloc[31,2]/1000000:.0f}M to {res.iloc[33,2]/1000000:.0f}M.
                                        - Overall sale is the highest in {res.iloc[16,0]} and lowest in {res.iloc[45,0]}.
                                        - Seasonal changes around {res.iloc[1,1]}, {res.iloc[2,1]}, {res.iloc[5,1]} and {res.iloc[10,1]} are the main cause of sale fluctuations while sale remains almost stable for the rest of the months.
                                        """)

                        st.subheader('Grouped Bar Chart on Sub-Channel on Channels')
                        with st.expander('Click to view grouped bar chart:', expanded = True):
                            try:
                                res, plot = self.eda.grouped_bar_on_subchannel()
                                st.plotly_chart(plot)
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - {res.iloc[2,0]} Channel Dominance: Pharmacy sales significantly outperform {res.iloc[0,0]} channels, with {res.iloc[3,1]} contracts (approximately {res.iloc[3,2]/1000000000:.2f}B) representing the single largest revenue stream, indicating strong public sector relationships.
                                        - {res.iloc[0,1]} vs {res.iloc[1,1]} Hospital Gap: {res.iloc[0,1]} hospital sales exceed {res.iloc[1,1]} hospital sales by roughly {(res.iloc[0,2] - res.iloc[1,2])/1000000:.0f}M, suggesting either preferential {res.iloc[0,1]} contracts, larger order volumes, or more favorable pricing structures in the public sector.
                                        - {res.iloc[2,0]} Channel Balance: {res.iloc[2,1]} and {res.iloc[3,1]} pharmacy segments show relatively equal performance (both around {((res.iloc[3,2] - res.iloc[2,2])/2+res.iloc[2,2])/1000000000:.2f}B), indicating successful dual-channel strategy in the {res.iloc[2,0]} market with no over-dependence on either segment.
                                        - Cross-Channel Revenue Distribution: {res.iloc[0,0]} channels generate approximately {(res.iloc[0,2] + res.iloc[1,2])/1000000000:.2f}B total revenue compared to {res.iloc[2,0]} channels' {(res.iloc[2,2] + res.iloc[3,2])/1000000000:.2f}B, showing the {res.iloc[2,0]} sector as the slightly larger overall market despite individual transaction sizes being smaller.
                                        - Strategic Implications: The balanced performance across four distinct sub-channels ({res.iloc[0,1]} hospital, {res.iloc[1,1]} hospital, {res.iloc[2,1]}al pharmacy, {res.iloc[3,1]} pharmacy) provides strong risk diversification and multiple growth opportunities.
                                        - Market Penetration Opportunities: The relatively close performance between {res.iloc[2,1]}al and {res.iloc[3,1]} pharmacy suggests potential for targeted campaigns to capture greater market share in the slightly underperforming retail segment.
                                        - Revenue Concentration Risk: While diversified across channels, the heavy reliance on {res.iloc[0,1]} hospital contracts creates potential vulnerability to policy changes or budget cuts in public healthcare spending.
                                        """)
                        
                        st.subheader('Sunburst on Profit of Channel')
                        with st.expander('Click to view sunburst plot:', expanded = True):
                            try:
                                res = self.filtered_data.groupby(['Channel', 
                                                                'Sub-channel', 
                                                                'Product Class'])['Year'].unique().reset_index()
                                st.plotly_chart(self.eda.sunburst_profit_in_channel())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - **Channel-Level Market Share**: {res.iloc[12,0]} and {res.iloc[0,0]} channels show roughly equal market presence in the outer ring, indicating balanced dual-channel strategy without over-dependence on either healthcare delivery system.
                                        - **Sub-Channel Segmentation**: Each main channel splits into distinct sub-segments ({res.iloc[0, 1]}/{res.iloc[7, 1]} for {res.iloc[0, 0]}, {res.iloc[12, 1]}/{res.iloc[18, 1]} for {res.iloc[12, 0]}), demonstrating clear market differentiation and targeted customer approaches.
                                        - **Product Category Concentration**: {res.iloc[1, 2]} dominate the innermost segments across all channels, reflecting the core business focus on infectious disease treatment and essential medicine portfolio.
                                        - **Therapeutic Area Distribution**: The sunburst reveals diversified product mix including {res.iloc[0,2]}, {res.iloc[2, 2]}, and {res.iloc[3, 2]}, suggesting comprehensive coverage of primary healthcare needs rather than narrow specialization.
                                        - **Cross-Channel Product Consistency**: Similar therapeutic categories appear across both {res.iloc[0, 0]} and {res.iloc[12, 0]} channels, indicating standardized product portfolio strategy that leverages economies of scale in manufacturing and procurement.
                                        - **Market Penetration Depth**: The hierarchical structure shows successful penetration at multiple levels - from broad channel access down to specific therapeutic niches within each segment.
                                        """)

                        st.subheader('Line Chart on Sale over Time for Channels')
                        with st.expander('Click to view line chart:', expanded = True):
                            try:
                                res, plot = self.eda.channel_sale()
                                st.plotly_chart(plot)
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown(f"""
                                        #### Insights
                                        - A maximum drawdown was witnessed in both channels in the month of January and a spike in the month of August in 2019.
                                        - The hospital channel consistently outperformed pharmacy channels across all years, indicating stronger institutional relationships and bulk purchasing patterns.
                                        - A review of December 2020 data indicates a significant decline in the hospital channel's performance, contrasted by a substantial spike in the pharmacy channel. This disparity raises the hypothesis that market factors, such as increased consumer reliance on retail pharmacies and potentially growing competitive pressure in the hospital sector, were at play.
                                        """)

                    with tab3:
                        st.subheader('Top Performing Products')
                        with st.expander('Click to view Top Performance:', expanded = True):
                            try:
                                df = self.salesperf.top_product_by_rev()
                                st.dataframe(df)
                            except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - {df.iloc[0,0]} dominates performance with the highest average sale value ({df.iloc[0,2]/1000:.2f}k) and units sold ({df.iloc[0,3]:.2f}), making it the clear revenue leader
                                        - Premium pricing strategy works - higher-priced products like {df.iloc[4,0]} ({df.iloc[4,1]:.2f}) and {df.iloc[5,0]} ({df.iloc[5,1]:.2f}) still achieve strong sales volumes
                                        - Top 3 products drive significant volume - {df.iloc[0,0]}, {df.iloc[1,0]}, and {df.iloc[2,0]} together represent substantial market share
                                        - Price-performance correlation exists - most top performers maintain prices between 600-800 range
                                        """)

                        st.subheader('Sales Representative Leaderboard')
                        with st.expander('Click to view leaderboard:', expanded = True):
                            try:
                                df = self.eda.top_ns(column_name = 'Sales Representative', top = 10)
                                st.dataframe(df)
                            except Exception as e:
                                self.log.error(f'Could not load dataframe: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - Performance gaps are narrow - top performers like {df.iloc[0,0]} ({df.iloc[0,1]/1000:.2f}k avg sale) only marginally outperform others, suggesting consistent team capability
                                        - High absolute sales volumes - all representatives achieve {df['Total_Units_Sold'].sum()/1000000:.0f}+ million total units sold, indicating strong overall market demand
                                        - Top 4 representatives cluster together - minimal difference between {df.iloc[0,0]}, {df.iloc[1,0]}, {df.iloc[2,0]}, and {df.iloc[3,0]}
                                        - Team consistency is strong - even lowest performers maintain respectable averages around {df.iloc[7,1]/1000:.0f}k""")

                        st.subheader('Most Sold Product/Product Type')
                        with st.expander('Click to view most sold product:', expanded = True):
                            subtab1, subtab2 = st.tabs(['Product', 'Product Type'])

                            with subtab1:
                                try:
                                    st.subheader('Most Sold Product')
                                    df = self.salesperf.top_sold_product(column_name = 'Product Name')
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {df.iloc[0,0]} leads in both metrics - highest total sales ({df.iloc[0,1]/1000000:.2f}M) and units sold ({df.iloc[0,2]}), confirming its market dominance
                                            - Volume vs. value alignment - top revenue products generally match top volume products, indicating healthy pricing
                                            - {df.iloc[1,0]} shows strong performance - second in both sales ({df.iloc[1,1]/1000000:.2f}M) and units ({df.iloc[1,2]}), making it a key product
                                            - Long tail of products - significant drop-off after top 3 products suggests portfolio concentration""")

                            with subtab2:
                                try:
                                    st.subheader('Most Sold Product Type')
                                    df = self.salesperf.top_sold_product(column_name = 'Product Class')
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {df.iloc[0,0]} dominate the market - highest total sales ({df.iloc[0,1]/1000000000:.2f}B) and units sold ({df.iloc[0,2]/1000000:.2f}M), representing the largest therapeutic category
                                            - {df.iloc[1,0]} show strong second position - {df.iloc[1,1]/1000000000:.2f}B in sales with {df.iloc[1,2]/1000000:.2f}M units, nearly matching {df.iloc[0,0]}
                                            - {df.iloc[2,0]} rank third - {df.iloc[2,1]/1000000000:.2f}B sales with {df.iloc[2,2]/1000000:.2f}M units, indicating significant mental health market
                                            - {df.iloc[3,0]} and {df.iloc[4,0]} underperform - lower sales despite important therapeutic roles""")

                        st.subheader('Higest Performing Manager')
                        with st.expander('Click to view manager performance chart:', expanded = True):
                            try:
                                df = self.salesperf.manager_performance()
                                st.dataframe(df)
                            except Exception as e:
                                self.log.error(f'Could not load dataframe: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - Minimal performance variation - all three managers achieve similar average sales ({df.iloc[2,1]/1000:.0f}K-{df.iloc[0,1]/1000:.0f}K)
                                        - {df.iloc[0,0]} leads slightly - highest average sale ({df.iloc[0,1]:.0f}) but lowest units sold, suggesting premium focus
                                        - Consistent pricing strategies - all managers maintain similar average pricing, indicating coordinated approach
                                        - Team management effectiveness - similar performance suggests effective management practices across teams""")

                        st.subheader('Countries/Cities Contributing to Business Performance')
                        with st.expander('Click to view Business Performance Tables:', expanded = True):
                            subtab1, subtab2 = st.tabs(['Countries', 'Cities'])
                            with subtab1:
                                try:
                                    st.subheader('Business Performance by Country')
                                    df = self.eda.top_ns(column_name = 'Country')
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - {df.iloc[0,0]} significantly outperforms {df.iloc[1,0]} - average sales of {df.iloc[0,1]:.0f} vs {df.iloc[1,1]:.0f}, indicating stronger market conditions
                                            - Volume disparity is substantial - {df.iloc[0,0]}'s {df.iloc[0,2]/1000000:.1f}M units vs {df.iloc[1,0]}'s {df.iloc[1,2]/1000000:.1f}M units shows major market size difference
                                            """)

                            with subtab2:
                                try:
                                    st.subheader('Business Performance by City')
                                    df = self.eda.top_ns(column_name = 'City', top = 10)
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown(f"""
                                            #### Insights:
                                            - German cities dominate the top-performing real estate markets, with Polish cities notably absent due to lower average sale prices. For instance, {df.iloc[0,0]} leads with an average sale price of {df.iloc[0,1]/1000:.2f}k and a total of {df.iloc[0,2]/1000:.2f}k units sold, signaling a highly active and premium property market.
                                            - {df.iloc[1,0]} and {df.iloc[2,0]} follow with average sale prices of {df.iloc[1,1]/1000:.2f}k and {df.iloc[2,1]/1000:.2f}k respectively, while still maintaining strong transaction volumes of {df.iloc[1,2]/1000:.2f}k and {df.iloc[2,2]/1000:.2f}k units. This suggests these cities offer a more affordable entry point without sacrificing market activity.
                                            - In contrast, cities like {df.iloc[8,0]} ({df.iloc[8,1]/1000:.2f}k, {df.iloc[8,2]/1000:.2f}kunits sold) and {df.iloc[9,0]} ({df.iloc[9,1]/1000:.2f}k, {df.iloc[9,2]/1000:.2f}k units sold) show lower values on both metrics but still outperform Polish cities, emphasizing how average sale price heavily influences visibility in this dataset.
                                            - Overall, the data reflects a clear trend: higher property values correlate strongly with market prominence, even when transaction volumes are comparable.""")

                        st.subheader('Chart for Best Performing Channels/Sub-channels')
                        with st.expander('Click to view best performance:', expanded = True):
                            try:
                                df = self.salesperf.best_sales_channel()
                                st.dataframe(df)
                            except Exception as e:
                                self.log.error(f'Could not load dataframe: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - {df.iloc[0,0]}–{df.iloc[0,1]} shows the highest average sales ({df.iloc[0,2]:.0f}) and units sold ({df.iloc[0,3]:.0f}) among all channels.
                                        - {df.iloc[1,0]}–{df.iloc[1,1]} has slightly lower sales ({df.iloc[1,2]:.0f}) and units ({df.iloc[1,3]:.0f}) than {df.iloc[0,1]} but still performs close.
                                        - {df.iloc[2,0]}–{df.iloc[2,1]} records the lowest sales ({df.iloc[2,2]:.0f}), though its average units sold ({df.iloc[2,3]:.0f}) are higher than {df.iloc[1,0]}–{df.iloc[1,1]}.
                                        - Sales values across all three segments are very close (~{df.iloc[2,2]/1000:.0f}K–{df.iloc[0,2]/1000:.0f}K), suggesting a competitive balance between channels.
                                        """)

                        st.subheader('Price Variation')
                        with st.expander('Click to view price variation:', expanded = True):
                            subtab1, subtab2 = st.tabs(['By Country', 'By Market'])
                            with subtab1:
                                try:
                                    df = self.salesperf.price_variation_by_country()
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown("""
                                            #### Insights:
                                            - Analgesics and Antibiotics are more expensive in Poland than in Germany, with Poland's prices being slightly higher.
                                            - Antimalarials and Mood Stabilizers are cheaper in Poland, with noticeable price drops.
                                            - Antipyretics show almost no difference, with only a marginal increase in Poland, indicating stable pricing across both countries.
                                            - Antiseptics are moderately more expensive in Poland than in Germany, suggesting a possible difference in demand or regulation.
                                            """)
                            with subtab2:
                                try:
                                    df = self.salesperf.price_variation_by_market()
                                    st.dataframe(df)
                                except Exception as e:
                                    self.log.error(f'Could not load dataframe: {e}')
                                st.markdown("""
                                            #### Insights:
                                            - Antipyretics have the highest prices in both Hospital (468.07) and Pharmacy (469.97).
                                            - Antimalarial drugs are the lowest priced across both settings (~337.6–337.7).
                                            - Antibiotics show a small but notable premium in Pharmacies (420.82) compared to Hospitals (418.48).
                                            - Price differences between Hospital and Pharmacy are minimal overall (<3 units difference), indicating consistent pricing across channels.""")

                        st.subheader('Sales Team Performance')
                        with st.expander('Click to view sales team performance:', expanded = True):
                            try:
                                res, plot = self.salesperf.team_performance()
                                st.plotly_chart(plot)
                            except Exception as e:
                                self.log.error(f'Could not load plot and dataset: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - {res.iloc[2,0]} team outperforms with approximately {res.iloc[3,1]/1000:.2f}k in sales, showing 7-16% higher performance than other teams
                                        - Performance variation exists across teams ({(res.iloc[0,1])/1000 - 1:.0f}k-{(res.iloc[3,1]+1)/1000 + 1:.0f}k range), indicating potential for best practice sharing and training opportunities
                                        - {res.iloc[1,0]} and {res.iloc[3,0]} teams show similar performance levels around {(res.iloc[3,1]+1)/1000:.0f}k, suggesting consistent baseline performance
                                        - {res.iloc[0,0]} team underperforms slightly at {(res.iloc[0,1])/1000:.0f}k, requiring investigation into territory, resources, or skill gaps
                                        - Overall team performance is relatively consistent, indicating effective management but room for optimization to bring all teams to top performer levels
                                        """)

                        st.subheader('Cross Market Product Performance')
                        with st.expander('Click to view market performance:', expanded = True):
                            try:
                                res, plot = self.salesperf.cross_market_performance()
                                st.plotly_chart(plot)
                            except Exception as e:
                                self.log.error(f'Could not load plot and dataset: {e}')
                            st.markdown(f"""
                                        #### Insights:
                                        - {res.iloc[0,1]} channel consistently outperforms {res.iloc[2,1]} channel across all product categories, suggesting better margins or market penetration in retail
                                        - {res.iloc[0,0]} show the largest channel gap ({res.iloc[0,2]/1000:.2f}k {res.iloc[0,1]} vs {res.iloc[4,2]/1000:.2f}k {res.iloc[4,1]}), indicating strong consumer demand for fever-reducing medications
                                        - {res.iloc[1,0]} perform best overall with highest combined sales across both channels, confirming market leadership in pain management
                                        - {res.iloc[10,0]} drugs show smallest performance difference between channels, possibly due to specialized distribution requirements
                                        - Channel strategy optimization opportunity exists, particularly for products showing large performance gaps between {res.iloc[10,1]} and {res.iloc[11,1]} sales
                                        """)
                            
                    with tab4:
                        st.subheader('Overall Sales Trend in Four Years')
                        with st.expander('Click to view sales trend:', expanded = True):
                            try:
                                st.plotly_chart(self.tsa.sale_trend())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Over the four years, the sales of the company has seen fluctuations throughout with maximum drawdown witnessed in the month of January 2019 and a sudden spike in August of the same year.
                                        - Months with the highest sales are March 2018 with 384.45M sale, June 2018 with 367.93M sale, October 2018 with 362.18M sale and August 2019 with 485.87M sale.
                                        - There is no positive trend followed by the sale over time. Sale is fluctuating around a midpoint indicating that the sale is oscillating around the mean.
                                        """)

                        st.subheader('Seasonal Decomposition')
                        with st.expander('Click to view seasonal decomposition:', expanded = True):
                            try:
                                st.plotly_chart(self.tsa.decompose_revenue())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Trend (Long-term Movement): The trend component (blue line) shows a gradual increase in revenue until around mid-series, after which it slightly declines and stabilizes. This suggests the business experienced growth initially, followed by a plateau and mild decline in recent months.
                                        - Seasonality (Recurring Patterns): The seasonal component (green line) shows repeating fluctuations across the months, with revenue consistently rising in some months (peaks above 1.2) and falling in others (dips near 0.8). This indicates strong seasonal effects - likely tied to periodic demand cycles (e.g., holidays, annual events, or industry-specific cycles).
                                        - Residual (Irregular Effects): The residual component (red line at the bottom) fluctuates around 1 with occasional spikes, meaning unexpected shocks or anomalies exist (e.g., sudden revenue jumps or drops). However, since the deviations aren’t extreme most of the time, the majority of variation is well explained by trend and seasonality.
                                        """)

                        st.subheader('Monthly Sales Trend of Product Class')
                        with st.expander('Click to view monthly sales trend:', expanded = True):
                            try:
                                st.plotly_chart(self.tsa.monthly_sales_trend_product())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Analgesics Show Extreme Volatility: The analgesics category exhibits the most dramatic fluctuations, with peaks over 200k in mid-2019. This suggests sensitivity to external factors like health crises or supply disruptions, making it the most unpredictable revenue stream.
                                        - Antimalarial Sales Follow Seasonal Cycles: Antimalarial sales show clear annual spikes reaching ~125k, particularly in 2018-2020. This cyclical pattern aligns with malaria seasons and provides predictable demand for inventory planning.
                                        - Core Categories Remain Stable: Antibiotics, antipyretics, antiseptics, and mood stabilizers consistently fluctuate within 25k-75k range, indicating steady baseline demand for these essential medications.
                                        - 2019 Marks a Major Market Event: Mid-to-late 2019 shows synchronized spikes across multiple categories. This suggests a significant health event or policy change that broadly impacted pharmaceutical demand and could inform future crisis preparedness.
                                        """)

                        st.subheader('Growth Rate Analysis')
                        with st.expander('Click to view monthly sales trend:', expanded = True):
                            subtab1, subtab2, subtab3 = st.tabs(['Growth Rate Analysis for Product', 
                                                                'Growth Rate Analysis for Channel', 
                                                                'Growth Rate Analysis for Sub-channel'])
                            with subtab1:
                                try:
                                    st.plotly_chart(self.tsa.growth_rate_analysis(category = 'Product Class')) 
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - Analgesics had the most sales in 2017 and 2019 followed by Antipyretics which surpassed the sale of Analgesics in 2018 and 2020. 
                                        - Throughout, Antimalarial has made the least amount of sales suggesting its requirement comes only during the rainy season which are accompanied by waterlogging (main cause of malaria infection).
                                        - Antibiotics, Antiseptics and mood stabilizers remain almost consistent in their sale compared to other categories.
                                        - The highest sale of all product types was made in the year 2019 with overall lowest seen in 2018.
                                        """)                   

                            with subtab2:
                                try:
                                    st.plotly_chart(self.tsa.growth_rate_analysis(category = 'Channel'))
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - Both Hospital and Pharmacy channels saw the highest sale in the year 2019 followed by 2020, considering the onset of COVID-19.
                                        - The significant decrease in sales from hospitals suggests the shortage of products caused by the increased rate of patient admission in the hospitals.
                                        - The lowest sale was seen in 2018 with hospital sales of 39.14k and pharmacy sales of 38.69k.
                                        """)

                            with subtab3:
                                try:
                                    st.plotly_chart(self.tsa.growth_rate_analysis(category = 'Sub-channel'))
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - Overall, the lowest sale has been made by private hospitals compared to other sub-channels.
                                        - The highest is made by Institutional Pharmacies in 2017, Retail Pharmacies in 2018 and 2020 and government pharmacies in 2019.
                                        - Each sub-channel sale is close to each other suggesting no sub-channel has a strong influence in their sale and has a nearly similar distribution.
                                        """)

                        st.subheader('Sales Growth of Sales Team (Yearly)')
                        with st.expander('Click to view yearly sales growth chart:', expanded = True):
                            try:
                                st.plotly_chart(self.tsa.sales_team_yearly_growth())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - **Alpha**: The team has the second lowest sale in 2017, consistently having lowest sales in 2018-2019 and again going back to being second lowest in 2020.
                                        - **Bravo**: This team had the second highest sale throughout, except in 2018 where it surpassed Delta only slightly to be the highest revenue generating team.
                                        - **Charlie**: Having the lowest sale in 2017, this team’s sales slowly rose in 2018 to be the highest selling team from 2019 to 2020.
                                        - **Delta**: This team followed an opposite path to Charlie, going from the highest selling team to being the lowest in 2020.
                                        """)

                        st.subheader('Customer Behaviour Trend')
                        with st.expander('Click to view customer behavior analysis:', expanded = True):
                            try:
                                st.plotly_chart(self.tsa.customer_trend())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Monthly customer count fluctuates throughout. Since the total number of actual customers is 751, the customer count suggests spikes and drops in the frequency of purchase by customers.
                                        - Customers in Poland bought products from the company for only a year (2018). Purchasing behavior of the customers does not exceed over 4000, compared to Germany which reaches as much as 6000.
                                        """)

                        st.subheader("Moving Average Analysis")
                        with st.expander("Click to view forecasting for moving average:", expanded = True):
                            try:
                                lag_by         = [2, 5, 10]
                                all_ma_results = {}

                                for window in lag_by:
                                    ma_result = self.tsa.moving_average_analysis(window = window)

                                    for country, df in ma_result.items():
                                        # Rename the column dynamically here
                                        df = df.rename(columns={"Moving_Average" : f"Moving_Average{window}"})

                                        if country not in all_ma_results:
                                            all_ma_results[country] = df.copy()
                                        else:
                                            all_ma_results[country][f"Moving_Average{window}"] = df[f"Moving_Average{window}"]

                                for country, df in all_ma_results.items():
                                    y_cols = ["Sales"] + [col for col in df.columns if col.startswith("Moving_Average")]

                                    figure = px.line(data_frame = df,
                                                    x          = df.index,
                                                    y          = y_cols,
                                                    title      = f"Actual Sales vs Moving Averages of {country}")
                                    st.plotly_chart(figure, use_container_width = True)
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - The sales trend of Germany is smoothed out using the Moving Average method.
                                        - The delay in three moving average plots indicate the size of the window which helps select the number of data points to calculate the average of. The larger the window size the smoother the trend line gets.
                                        - Overall the trend shows a stagnant trend, neither moving up nor moving down. 
                                        - For Poland, since the size of the dataset is small (12 months of data), it is difficult to understand its trend. 
                                        - Through the data, it can be seen the trend remains stagnant for Poland as well slightly increasing at the end of the year.
                                        """)
                    
                        st.subheader("Forecast Prophet")
                        with st.expander("Click to view forecasting:", expanded = True):
                            poland_data, germany_data = self.forecaster.data_organization()
                            poland_data  = poland_data.rename(columns  = {"Date"  : "ds", 
                                                                        "Sales" : "y"})
                            germany_data = germany_data.rename(columns = {"Date"  : "ds", 
                                                                        "Sales" : "y"})

                            subtab1, subtab2 = st.tabs(['Germany Data', 'Poland Data'])
                            with subtab1:
                                try:
                                    self.forecaster.fit_prophet_model(germany_data)
                                    forecast                 = self.forecaster.forecast_sales(germany_data, 
                                                                                            horizon_months = 12)
                                    st.plotly_chart(self.forecaster.plot_forecast(historical_data = germany_data, 
                                                                                country_name    = "Germany"))
                                    summary, future_forecast = self.forecaster.get_forecast_summary(germany_data, 
                                                                                                    perioDate = 12)
                                    st.dataframe(summary)
                                except Exception as e:
                                    self.log.error(f'Could not forecast model: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - **Strong Seasonality**: There is a clear and consistent seasonal pattern in sales, with peaks typically occurring in the summer months (around July) and troughs in the winter months (around January). This seasonality is evident throughout the historical sales data and is captured well by the Prophet Forecast.
                                        - **Overall Upward Trend (Pre-2021)**: From January 2017 to early 2021, while fluctuating due to seasonality, the general trend of historical sales shows a gradual increase, indicating growth over this period.
                                        - **Significant Spike and Volatility in Mid-2021**: The graph shows an exceptionally large and sharp peak in sales around July 2021, far exceeding previous historical peaks. This is followed by a steep decline, indicating a period of high volatility and an unusual event or change in the market during that time.
                                        - **Prophet Forecast Accuracy**: The Prophet Forecast generally aligns closely with the Historical Sales data, particularly in capturing the seasonal patterns and overall trends, suggesting a good fit for the model. The forecast also predicts the sharp rise in mid-2021 and the subsequent drop, although the magnitude of the forecast peak is slightly lower than the actual historical sales peak in July 2021.
                                        - **Confidence Interval**: The confidence interval (shaded blue area) provides a range within which future sales are expected to fall with a certain probability. The historical sales mostly remain within this interval, indicating the reliability of the forecast. However, the actual sales peak in July 2021 significantly exceeds the upper bound of the confidence interval, highlighting an unforeseen event or a limitation of the model in predicting extreme outliers.
                                        - **Post-Peak Normalization**: Following the dramatic spike and decline in mid-2021, the forecast suggests a return to a more typical seasonal pattern, albeit at a slightly higher baseline than pre-2021 levels.
                                        """)
                            with subtab2:
                                try:
                                    self.forecaster.fit_prophet_model(poland_data)
                                    forecast                 = self.forecaster.forecast_sales(poland_data, 
                                                                                            horizon_months = 3)
                                    st.plotly_chart(self.forecaster.plot_forecast(historical_data = poland_data, 
                                                                                country_name    = "Poland"))
                                    summary, future_forecast = self.forecaster.get_forecast_summary(poland_data, 
                                                                                                    perioDate = 3)
                                    st.dataframe(summary)
                                except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                                st.markdown("""
                                        #### Insights:
                                        - Due to the lack of sufficient data for Poland (only 1 year data is present) the Prophet model has memorized the training data resulting in poor forecasting results. So, no insights could be drawn from the data.
                                        """)

                    with tab5:
                        st.subheader('Geographic Sales Distribution')             
                        st.subheader('Concentration Analysis')
                        with st.expander('Click to view concentration of sales over map:', expanded = True):
                            try:
                                st.plotly_chart(self.geo.revenue_concentration_by_city())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Sales activity is concentrated in Germany, with several hotspots in western and central regions.
                                        - Poland shows very low sales intensity compared to Germany, with minimal hotspots.
                                        - The highest sales volumes (darkest blue) are around regions close to Belgium, the Netherlands, and central Germany.
                                        - The data indicates a strong imbalance in market penetration between Germany and Poland.
                                        """)

                        st.subheader('Performance Analysis across Cities')
                        with st.expander('Click to view performance comparison:', expanded = True):
                            try:
                                st.plotly_chart(self.geo.performance_analysis())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Germany: Butzbach leads by a large margin (~90M sales), followed by Baesweiler and Cuxhaven.
                                        - Other German cities such as Berlin, Trier, and Bottrop also perform strongly but with lower volumes compared to Butzbach.
                                        - Poland: The bottom 20 cities show sales figures mostly around 1.7M–2.2M, much lower than Germany’s top cities.
                                        - A clear contrast is visible — German cities dominate top performance, while Polish cities cluster at the bottom with lower market penetration.
                                        """)

                        st.subheader('Market Penetration Analysis')
                        with st.expander('Click to view market penetration analysis:', expanded = True):
                            try:
                                st.plotly_chart(self.geo.market_penetration())
                            except Exception as e:
                                self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                        #### Insights:
                                        - Germany accounts for 73.4% of the total market penetration represented in this chart, as shown by the larger, dark blue segment.
                                        - Poland accounts for 26.6% of the total market penetration, as shown by the smaller, light blue segment.
                                        """)

                        st.subheader('Territory Optimization')
                        with st.expander('Click to view territory optimization analysis:', expanded = True):
                            try:
                                result , _= self.geo.optimize_territories()
                                st.plotly_chart(self.geo.visualize_territories(clustered_data = result))
                                st.subheader("Territory Summary")
                                summary = result.groupby('Territory').agg({'Sales'         : 'sum',
                                                                        'Customer Name' : 'nunique',
                                                                        'City'          : 'nunique'}).reset_index()
                                summary.columns = ['Territory', 
                                                'Total Sales', 
                                                'Unique Customers', 
                                                'Unique Cities']
                                st.dataframe(summary)
                            except Exception as e:
                                    self.log.error(f'Could not load plot: {e}')
                            st.markdown("""
                                    #### Insights:
                                    The majority of optimized territories are clustered within Germany, indicating higher density of customers/sales there.
                                    - Territories are divided into 3 groups, with darker blue indicating higher concentration.
                                    - Very few territories extend into Poland, confirming weaker demand or sales distribution there.
                                    - This optimization highlights a need for better coverage or targeted strategies in Poland, while Germany already has dense and optimized regions.
                                    """)
                
                else:
                    print(type(self.filtered_data))
                    st.markdown(self.filtered_data)

if __name__ == '__main__':
    app = App()
    app.main_contents()

