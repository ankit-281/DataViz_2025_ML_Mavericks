import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry

# Load the data
@st.cache
def load_data():
    # Update the file paths to your local paths
    climate_df = pd.read_csv("climate_change_data.csv")
    deforestation_df = pd.read_csv("goal15.forest_shares.csv")
    return climate_df, deforestation_df

climate_df, deforestation_df = load_data()

# Function to convert ISO3 codes to country names
def iso3_to_country(iso_code):
    try:
        return pycountry.countries.get(alpha_3=iso_code).name
    except AttributeError:
        return None

# Preprocess the deforestation data
deforestation_df['Country'] = deforestation_df['iso3c'].apply(iso3_to_country)
deforestation_df_updated = deforestation_df.dropna()

# Merge the data
merged_df = climate_df.merge(deforestation_df_updated, on='Country', how='inner')

# Preprocess the climate data
climate_df['Date'] = pd.to_datetime(climate_df['Date']).dt.year

# Streamlit app
st.title("Climate Change and Deforestation Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Filter by Country
country_list = merged_df['Country'].unique()
selected_country = st.sidebar.selectbox("Select Country", country_list)

# Filter by Year
year_list = climate_df['Date'].unique()
selected_year = st.sidebar.selectbox("Select Year", year_list)

# Filter by Temperature Range
min_temp = merged_df['Temperature'].min()
max_temp = merged_df['Temperature'].max()
temp_range = st.sidebar.slider("Select Temperature Range", min_temp, max_temp, (min_temp, max_temp))

# Filter by Deforestation Trend
min_trend = merged_df['trend'].min()
max_trend = merged_df['trend'].max()
trend_range = st.sidebar.slider("Select Deforestation Trend Range", min_trend, max_trend, (min_trend, max_trend))

# Apply filters
filtered_df = merged_df[
    (merged_df['Country'] == selected_country) &
    (merged_df['Date'] == selected_year) &
    (merged_df['Temperature'] >= temp_range[0]) & (merged_df['Temperature'] <= temp_range[1]) &
    (merged_df['trend'] >= trend_range[0]) & (merged_df['trend'] <= trend_range[1])
]

# Display filtered data
st.write("### Filtered Data")
st.write(filtered_df)

# Visualizations
st.write("### Visualizations")

# Temperature vs Deforestation Trend
st.write("#### Temperature vs Deforestation Trend")
fig, ax = plt.subplots()
sns.scatterplot(x=filtered_df['trend'], y=filtered_df['Temperature'], ax=ax)
ax.set_xlabel("Deforestation Trend (Negative = Loss)")
ax.set_ylabel("Temperature (°C)")
ax.set_title("Relationship Between Deforestation and Temperature Increase")
st.pyplot(fig)

# Correlation Heatmap
st.write("#### Correlation Heatmap")
corr = filtered_df[['Temperature', 'trend']].corr()
fig, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("Correlation Heatmap: Forest Cover vs. CO2 Emissions")
st.pyplot(fig)

# Top 10 Countries with Highest Deforestation
st.write("#### Top 10 Countries with Highest Deforestation")
ranked_deforestation = deforestation_df_updated.sort_values(by="trend").head(10)
fig, ax = plt.subplots()
sns.barplot(x=ranked_deforestation['trend'], y=ranked_deforestation['Country'], ax=ax)
ax.set_xlabel("Deforestation Trend")
ax.set_ylabel("Country")
ax.set_title("Top 10 Countries with Highest Deforestation")
st.pyplot(fig)

# Top 10 Countries with Lowest Deforestation
st.write("#### Top 10 Countries with Lowest Deforestation")
ranked_deforestation = deforestation_df_updated.sort_values(by="trend", ascending=False).head(10)
fig, ax = plt.subplots()
sns.barplot(x=ranked_deforestation['trend'], y=ranked_deforestation['Country'], ax=ax)
ax.set_xlabel("Deforestation Trend")
ax.set_ylabel("Country")
ax.set_title("Top 10 Countries with Lowest Deforestation")
st.pyplot(fig)

# Display raw data
if st.checkbox("Show Raw Data"):
    st.write("### Raw Data")
    st.write(merged_df)