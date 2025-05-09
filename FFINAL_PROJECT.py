"""
Name: Alp Gokmen
CS230: Section 5
Data: Word Air Quality Index
URL:
Description:
Using data from the World Air Quality Index, this program offers three primary summaries: Users can view and compare the AQI levels for each country,
filter by values above or below a chosen threshold, compare the AQI averages between the Northern and Southern Hemispheres, and examine PM2.5 levels across nations.
A globe map, bar and pie charts, and interactive tables are all included in the dashboard to make the data easy to understand and navigate.
"""
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pydeck as pdk

# [ST4] Customized page design features (sidebar, fonts, colors)
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

st.markdown("""
<style>
    .main-title {
        color: #2e86c1;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .section-header {
        color: #3498db;
        font-size: 24px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
        margin-top: 25px;
    }
    .dataframe {
        font-size: 14px;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">Global Air Quality Index (AQI) Analysis</p>', unsafe_allow_html=True)
st.markdown("Analyze air quality data from cities worldwide. Explore AQI values and PM2.5 categories.")

# [DA1] clean or manipulate data
def load_data():
    df = pd.read_csv("air_quality_index.csv")
    df.columns = df.columns.str.strip()

    # [DA1] clean or manipulate data
    numeric_cols = ['AQI Value', 'lat', 'lng']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=numeric_cols)

    # [PY5] at least a dictionary where you write a code to case its keys, values, or items
    country_mapping = {
        'United Kingdom of Great Britain and Northern Ireland': 'UK',
        'United States of America': 'USA',
        'Russian Federation': 'Russia'
    }
    df['Country'] = df['Country'].replace(country_mapping)

    # [DA8] iterate through rows of a dataframe with iterrows()
    df['Location_Info'] = ""
    for index, row in df.head(100).iterrows():
        df.at[index, 'Location_Info'] = f"{row['City']} ({row['Country']})"

    # [DA7] add/drop/select/create new/group columns
    df['Hemisphere'] = np.where(df['lat'] >= 0, 'Northern', 'Southern')
    df['East_West'] = np.where(df['lng'] >= 0, 'Eastern', 'Western')

    return df

data = load_data()

st.sidebar.header("Filter Options")
aqi_threshold = st.sidebar.slider("AQI Threshold Value", 0, 500, 50, 10)  # [ST1] at least three streamlit different widgets(1. slider)
min_cities = st.sidebar.slider("Minimum Cities per Country", 1, 50, 5)  # [ST1] at least three streamlit different widgets (1. slider)

st.markdown('<p class="section-header">AQI Value Analysis</p>', unsafe_allow_html=True)

# [DA2] Sort data in ascending or descending order, by one or more columns
country_stats = data.groupby('Country')['AQI Value'].agg(['count', 'mean', 'min', 'max'])
country_stats = country_stats[country_stats['count'] >= min_cities].sort_values('mean')

# [VIZ1] at least three different charts (1. table)

st.subheader("Country-Level AQI Statistics")
search_country = st.text_input("Search for a country:", "")
if search_country:
    filtered_stats = country_stats[country_stats.index.str.contains(search_country, case=False)]
    display_stats = filtered_stats if not filtered_stats.empty else country_stats
    if filtered_stats.empty:
        st.warning(f"No countries found matching '{search_country}'. Showing all countries.")
else:
    display_stats = country_stats

st.dataframe(
    country_stats.style.format({
        'count': '{:.0f}',
        'mean': '{:.1f}',
        'min': '{:.0f}',
        'max': '{:.0f}'
    }).background_gradient(cmap='YlOrRd', subset=['mean']),
    height=400
)

# [DA4] filter data by one condition
st.subheader(f"Cities Relative to AQI {aqi_threshold}")
below = data[data['AQI Value'] < aqi_threshold]['Country'].value_counts()

# [DA5] Filter the data by two or more conditions with (AND or OR)
below = below[below >= min_cities]  # AND condition

# [VIZ2] at least three different charts (2. bar chart)
if not below.empty:
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    below.head(10).plot(kind='barh', color='green', ax=ax1)
    ax1.set_title(f"Countries Below Threshold ({aqi_threshold})")
    ax1.set_xlabel("Number of Cities")
    st.pyplot(fig1)

above = data[data['AQI Value'] > aqi_threshold]['Country'].value_counts()
above = above[above >= min_cities]

if not above.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    above.head(10).plot(kind='barh', color='red', ax=ax2)
    ax2.set_title(f"Countries Above Threshold ({aqi_threshold})")
    ax2.set_xlabel("Number of Cities")
    st.pyplot(fig2)

st.markdown('<p class="section-header">Hemisphere Comparison</p>', unsafe_allow_html=True)

st.subheader("Northern vs Southern Hemisphere")
hemi_stats = data.groupby('Hemisphere')['AQI Value'].agg(['count', 'mean', 'std', 'min', 'max'])
hemi_stats.columns = ['Cities', 'Average', 'Std Dev', 'Minimum', 'Maximum']
st.dataframe(
    hemi_stats.style.format({
        'Cities': '{:.0f}',
        'Average': '{:.1f}',
        'Std Dev': '{:.1f}',
        'Minimum': '{:.0f}',
        'Maximum': '{:.0f}'
    }).background_gradient(cmap='YlOrRd', subset=['Average'])
)

st.subheader("Eastern vs Western Hemisphere")
east_west_stats = data.groupby('East_West')['AQI Value'].agg(['count', 'mean', 'std', 'min', 'max'])
east_west_stats.columns = ['Cities', 'Average', 'Std Dev', 'Minimum', 'Maximum']
st.dataframe(
    east_west_stats.style.format({
        'Cities': '{:.0f}',
        'Average': '{:.1f}',
        'Std Dev': '{:.1f}',
        'Minimum': '{:.0f}',
        'Maximum': '{:.0f}'
    }).background_gradient(cmap='YlOrRd', subset=['Average'])
)

st.markdown('<p class="section-header">PM2.5 Category Analysis</p>', unsafe_allow_html=True)

# [DA1] clean or manipulate data
data['PM2.5 AQI Category'] = data['PM2.5 AQI Category'].str.strip().str.title()

# [DA6] Analyze the data with pivot tables
pm25_pivot = pd.pivot_table(
    data=data,
    index='Country',
    columns='PM2.5 AQI Category',
    values='AQI Value',
    aggfunc='count',
    fill_value=0
)

# [DA3] Find the top largest, or smallest, values of a column
pm25_pivot = pm25_pivot[pm25_pivot.sum(axis=1) >= min_cities]
pm25_pivot['Total'] = pm25_pivot.sum(axis=1)
pm25_pivot = pm25_pivot.sort_values('Total', ascending=False).drop('Total', axis=1)

st.subheader("PM2.5 Categories by Country")
st.dataframe(
    pm25_pivot.head(20).style.format("{:.0f}")
    .background_gradient(cmap='YlOrRd', axis=1)
)

# [VIZ3] at least three different charts (3. pie chart)
# [ST3] at least three different Streamlit widgets (2. type-textbox)
st.subheader("Global PM2.5 Category Distribution")
category_dist = data['PM2.5 AQI Category'].value_counts(normalize=True) * 100

fig3, ax3 = plt.subplots(figsize=(8, 6))
colors = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
wedges, texts, autotexts = ax3.pie(
    category_dist,
    labels=category_dist.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'fontsize': 5}
)
ax3.axis('equal')
plt.title('PM2.5 Category Distribution', pad=20)
st.pyplot(fig3)

# [ST2] at least three different Streamlit widgets (3. selectbox)
st.markdown('<p class="section-header">PM2.5 Category Filter Analysis</p>', unsafe_allow_html=True)
pm25_categories = sorted(data['PM2.5 AQI Category'].unique().tolist())
selected_category = st.selectbox("Select PM2.5 Category to Analyze:", pm25_categories)

# [PY4] at least one list comprehension
pm25_categories = [num for num in data['PM2.5 AQI Category'].unique().tolist() if str(num) != 'nan']

valid_countries = country_stats[country_stats['count'] >= min_cities].index
country_totals = data['Country'].value_counts()
category_counts = data[data['PM2.5 AQI Category'] == selected_category]['Country'].value_counts()
country_percentages = (category_counts / country_totals * 100).dropna()
country_percentages = country_percentages[country_percentages.index.isin(valid_countries)]
country_percentages = country_percentages.sort_values(ascending=False)

st.subheader(f"Top 10 Countries by % of Cities with {selected_category} PM2.5 Levels")
top_10 = country_percentages.head(10).reset_index()
top_10.columns = ['Country', 'Percentage']
top_10['Percentage'] = top_10['Percentage'].round(2)

fig4, ax4 = plt.subplots(figsize=(10, 6))
top_10.plot(kind='barh', x='Country', y='Percentage', color='#3498db', ax=ax4)
ax4.set_title(f"% of Cities with {selected_category} PM2.5 by Country")
ax4.set_xlabel("Percentage of Country's Cities in this Category")
st.pyplot(fig4)

# [PY1] at least a function with two or more parameters, one of which has a default value
def get_color(aqi, alpha=180):
    # [PY3] some error checking using else, elif, if
    if aqi <= 50:
        return [0, 200, 0, alpha]
    elif aqi <= 100:
        return [255, 255, 0, alpha]
    elif aqi <= 150:
        return [255, 126, 0, alpha]
    elif aqi <= 200:
        return [255, 0, 0, alpha]
    elif aqi <= 300:
        return [153, 0, 76, alpha]
    else:
        return [126, 0, 35, alpha]

map_data = data.reset_index()[['City', 'Country', 'lat', 'lng', 'AQI Value', 'PM2.5 AQI Category', 'Hemisphere', 'East_West', 'Location_Info']]
map_data.rename(columns={'lng': 'lon'}, inplace=True)
map_data['color'] = map_data['AQI Value'].apply(get_color)

# [MAP] at least one detailed map (pydeck with hover)
st.markdown('<p class="section-header">Global Air Quality Map</p>', unsafe_allow_html=True)
map_data['radius'] = np.where(
    map_data['AQI Value'] < 100, 2000,
    np.where(
        map_data['AQI Value'] < 200, 3000,
        4000
    )
)

view_state = pdk.ViewState(
    latitude=map_data['lat'].mean(),
    longitude=map_data['lon'].mean(),
    zoom=1,
    pitch=0
)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_color='color',
    get_radius='radius',
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=0.5,
    radius_min_pixels=3,
    radius_max_pixels=30
)

# [PY2] at least a function that returns more than one value
def calculate_hemisphere_stats(df):
    north = df[df['Hemisphere'] == 'Northern']['AQI Value'].mean()
    south = df[df['Hemisphere'] == 'Southern']['AQI Value'].mean()
    return north, south

north_avg, south_avg = calculate_hemisphere_stats(data)

tooltip = {
    "html": "<b>{City}</b>, {Country}<br/>"
            "<b>Location Info:</b> {Location_Info}<br/>"
            "<b>AQI:</b> {AQI Value}<br/>"
            "<b>Category:</b> {PM2.5 AQI Category}<br/>"
            "<b>Hemisphere:</b> {Hemisphere} ({East_West})",
    "style": {
        "backgroundColor": "#2e86c1",
        "color": "white",
        "font-family": "Arial",
        "z-index": "10000"
    }
}

deck = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip=tooltip
)
st.pydeck_chart(deck)