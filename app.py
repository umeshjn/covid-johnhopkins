import streamlit as st
import pandas as pd
import altair as alt

# Set the layout to wide mode (this will make the app take the full width)
st.set_page_config(layout="wide")

# Add a title to the app
st.title("COVID-19 Data Dashboard")

# Inject custom CSS to set the width to 80% and center it, and ensure scrollbar appears on the right
st.markdown("""
    <style>
    /* Make the overall page width 100% to ensure scroll bar appears at the far right */
    .stApp {
        width: 100%;  /* Full width of the browser */
        margin-left: auto;
        margin-right: auto;
        padding-left: 0;
        padding-right: 0;
    }

    /* Center the content in the middle of the page with 80% width */
    .main {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 0;
    }

    /* Make the chart container take up 80% of the width, but centered */
    .stAltairChart {
        width: 80% !important;
        max-width: 100%;
        margin-left: auto;
        margin-right: auto;
    }

    /* Scrollbar should now appear at the rightmost end of the page */
    .main {
        overflow-y: auto;
    }

    /* Adjust layout for any other Streamlit widgets */
    .stContainer {
        width: 100% !important;
    }

    .stMarkdown, .stDataFrame, .stImage, .stTable {
        width: 100%;
    }

    </style>
""", unsafe_allow_html=True)

# Step 1: Load the dataset (JHU COVID-19 Global Data for cases and deaths)
@st.cache_data  # Caches the data to optimize the app's performance
def load_data():
    # URL to the JHU COVID-19 confirmed cases dataset
    url_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    # URL to the JHU COVID-19 deaths dataset
    url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    
    # Load the datasets
    df_cases = pd.read_csv(url_cases)
    df_deaths = pd.read_csv(url_deaths)
    
    # Drop unnecessary columns 'Lat' and 'Long' for simplicity
    df_cases = df_cases.drop(columns=['Lat', 'Long'])
    df_deaths = df_deaths.drop(columns=['Lat', 'Long'])
    
    # Reshape the data to have 'Date' and 'Cases'/'Deaths' as columns
    df_cases = df_cases.melt(id_vars=["Province/State", "Country/Region"], var_name="Date", value_name="Cases")
    df_deaths = df_deaths.melt(id_vars=["Province/State", "Country/Region"], var_name="Date", value_name="Deaths")
    
    # Convert the 'Date' column to datetime format
    df_cases['Date'] = pd.to_datetime(df_cases['Date'], errors='coerce')
    df_deaths['Date'] = pd.to_datetime(df_deaths['Date'], errors='coerce')
    
    # Remove rows where 'Date' parsing failed (if any)
    df_cases = df_cases.dropna(subset=['Date'])
    df_deaths = df_deaths.dropna(subset=['Date'])
    
    return df_cases, df_deaths

# Step 2: Load the data
df_cases, df_deaths = load_data()

# Step 3: Filter data to show only USA, India, and UK
countries_to_plot = ['US', 'India', 'United Kingdom']
df_cases_filtered = df_cases[df_cases['Country/Region'].isin(countries_to_plot)]
df_deaths_filtered = df_deaths[df_deaths['Country/Region'].isin(countries_to_plot)]

# Step 4: Line Graph for Cases Over Time (Using Altair)
st.subheader("COVID-19 Confirmed Cases Over Time (USA, India, UK)")

# Aggregate data: Sum up cases across all regions for each country and date
df_cases_grouped = df_cases_filtered.groupby(['Date', 'Country/Region'])['Cases'].sum().reset_index()

# Create the Altair line plot for Cases
line_chart = alt.Chart(df_cases_grouped).mark_line().encode(
    x='Date:T',  # Temporal type for date
    y='Cases:Q',  # Quantitative type for cases
    color='Country/Region:N',  # Different colors for each country
    tooltip=['Date:T', 'Cases:Q', 'Country/Region:N']  # Tooltips to show date, cases, and country
).configure_axis(
    labelAngle=-45  # Rotate x-axis labels for better readability
)

# Display the Altair plot in the Streamlit app (80% width, centered)
st.altair_chart(line_chart, use_container_width=True)

# Step 5: Bar Plot for Total Deaths (Latest Data for USA, India, UK)
st.subheader("Total COVID-19 Deaths (Latest Data - USA, India, UK)")

# Aggregate data: Get the latest deaths data for each country
df_deaths_latest = df_deaths_filtered.groupby('Country/Region')['Deaths'].sum().reset_index()

# Create the Altair **horizontal** bar plot for deaths
bar_chart = alt.Chart(df_deaths_latest).mark_bar().encode(
    x='Deaths:Q',  # Quantitative type for deaths on the x-axis (horizontal axis)
    y='Country/Region:N',  # Categorical type for country on the y-axis (vertical axis)
    color='Country/Region:N',  # Different colors for each country
    tooltip=['Country/Region:N', 'Deaths:Q']  # Tooltips to show country and death count
)

# Display the Altair horizontal bar plot in the Streamlit app (80% width, centered)
st.altair_chart(bar_chart, use_container_width=True)
