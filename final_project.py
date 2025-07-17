"""
Name:       Eli Blouin
CS230       Section 006
Data:       New England Airports
URL:        https://airplane-data.streamlit.app/

Description:
This program useful information about airports across New England using filtering, mapping, and data visualization
techniques through python and python packages. Useful variables include name, type, state (derived from 'iso_region'),
municipality, elevation, longitude, latitude, and scheduled service.

A secondary goal of this program is to find out if the 'scheduled service' is dependent on the type of airport it is. [chi-square test]
"""
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
from PIL import Image


# CLEAN_DATA(file_name)
# -- Reads file based on argument given
# -- Splits the variable 'iso_region' to create a new column named 'state'
# -- Sorts dataframe by elevation from high to low
# -- Creates new column named 'near-sealevel'. Elevation > or < 100 feet.
# -- Renames the longitude and latitude column headers
# -- Returns clean dataframe that includes only useful information like name, type, state, longitude, latitude, elevation_ft, near-sealevel, and scheduled service

def clean_data(file_name):
    # [DA1] Clean or manipulate data, lambda function (required)
    df = pd.read_csv(file_name)
    df[['country', 'state']] = df.iso_region.str.split("-", expand=True)
    # [DA2] Sort data in ascending or descending order, by one or more columns,
    df = df.sort_values('elevation_ft', ascending=False)
    # [DA7] Add/drop/select/create new/group columns
    df['near_sealevel'] = df.elevation_ft.apply(lambda x: 'Yes' if x <= 100 else 'No')
    df = df.rename(columns={'longitude_deg': 'longitude', 'latitude_deg': 'latitude'})
    dfair = df[['name', 'type', 'municipality', 'state', 'longitude', 'latitude', 'elevation_ft', 'near_sealevel', 'scheduled_service']]
    return dfair

# UNIQUE_LISTS(df)
# -- Finds and returns both the unique states and unique types in the dataframe as a list

# [PY2] A function that returns more than one value
def unique_lists(df):
    state_list = df.state.unique()
    type_list = df.type.unique()
    return state_list, type_list

# BUILD_DF(df)
# -- Creates and returns a new dataframe based on the selected values from the sidebar menu
# -- Handles 'both' cases with AND (&) statement and else/if statements

def build_df(df, s_types, s_states):
    if len(s_types) == 0:
        dfselected = df[df['state'].isin(s_states)]
    else:
        if len(s_states) == 0:
            dfselected =  df[df['type'].isin(s_types)]
        else:
            dfselected = df[df['state'].isin(s_states) & df['type'].isin(s_types)]
    return dfselected

# CUSTOM_MAP(df)
# -- Builds a slider that adjusts the radius size of the corresponding map's scatterplot values (yellow dots)
# -- Creates a Streamlit and PyDeck map based on Streets style and longitude and latitude of the dataframe

# [MAP] At least one detailed map
def custom_map(df):
    radius = st.slider('Adjust Radius of Pink Airports Below', 200, 2500, 1200, step=50)
    view_state = pdk.ViewState(
        longitude = df["longitude"].mean(),
        latitude = df["latitude"].mean(),
        zoom = 5.9,
        pitch = 0)
    layer = pdk.Layer('ScatterplotLayer',
                      data = df,
                      get_position= ["longitude", "latitude"],
                      get_radius = radius,
                      get_color =[255, 255, 0],
                      pickable = True
                      )
    tool_tip = {"html": "Airport Name:<br/> <b>{name}</b> <br/> <b>{municipality}, {state}</b>",
                "style": { "backgroundColor": "steelblue", "color": "white"}
            }
    map = pdk.Deck(
        map_style = 'mapbox://styles/mapbox/streets-v12',
        initial_view_state = view_state,
        layers = [layer],
        tooltip = tool_tip
    )
    st.pydeck_chart(map)

# DISPLAY_PIE(df)
# -- Creates a customizable pie chart based on the selected dataframe 'type' values in the sidebar menu
# -- E.g. percent of small-airports, large-airports etc.

# [VIZ1] At least two different charts with titles, colors, labels, legends, as appropriate, one can be a table
def display_pie(df):
    fig, ax = plt.subplots()
    df.plot(kind='pie', y='name', ax=ax, legend=False)
    ax.set_ylabel('')  # Remove the y-axis label for a cleaner look
    ax.set_title('Distribution of Airport Types')
    fig.set_size_inches(6, 6)
    st.pyplot(fig)

# DISPLAY_BAR(df)
# -- Incorporates a 'number_input' Streamlit widget to determine amount of 'top cities' requested (e.g. 20 top cities, 10 top cities)
# -- Creates a customizable bar chart based on a pivot table of counted 'top city' amounts (see above)
# -- All based on sidebar menu filter (state and type filters)

# [VIZ2] At least two different charts with titles, colors, labels, legends, as appropriate, one can be a table
def display_bar(df):
    top = st.number_input("Number of Top Cities Desired:", 3, 20, 5)
    df = df.sort_values('name', ascending=False) # sort first
    # [DA3] Find Top largest or smallest values of a column
    df = df.head(top) # output only top values based on 'top' variable
    fig, ax = plt.subplots()
    df.plot(kind='bar', y='name', ax=ax, legend=False)
    ax.set_ylabel('')
    ax.set_xlabel('Cities')
    ax.set_title('Top Cities By # of Airports')
    fig.set_size_inches(7, 7)
    st.pyplot(fig)

# WEBSITE_SETUP(df)
# -- Wraps all functions together to be able to print out a successful website layout
# -- Sets background color, can be changed (colork can be any color listed e.g. yellow, blue, pink, orange, green)
# -- Sets up sidebar values as a list of 'selected_states' and 'selected_types'. Important for visualizations and map
# -- 'build_df()' based on above selected values
# ---- SUMMARY STATS - total airports filtered and average elevation
# ---- MAP - includes filtered states and types, adjustable radius
# ---- TWO DATA VISUALS - pie displays types and bar displays top cities
# ---- TABLE - prints out 'selected df' based on build_df() function and sidebar selections
# -- Includes option to switch to 'type v. service' tab

# [PY1] A function with two or more parameters, one of which has a default value, called at least twice (once with the default value, and once without)
def website_setup(df, colork = 'yellow'):
    # [PY5] A dictionary where you write code to access its keys, values, or items
    colors = {'yellow':'#FEFBD4', 'blue':'#D5FBFD', 'pink':'#FDE9FF', 'orange':'#FEE8D9', 'green':'#E5FED9'}
    # [ST4] Customized page design features (sidebar, fonts, colors, images, navigation)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {colors[colork]};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NE Airports Dashboard")
    img = Image.open("airport_image.png")
    st.image(img, width = 700)
    # [ST1] At least three Streamlit different widgets (sliders, drop-downs, multi-selects, text boxes, etc.)
    st.sidebar.header('Dashboard Filters:')
    s_list, t_list = unique_lists(df)
    # for state in state_list:
    selected_states = st.sidebar.multiselect("Select States", s_list)
    selected_types = st.sidebar.multiselect("Select Types", t_list)
    selected_df = build_df(df, selected_types, selected_states)
    # [PY3] Error checking with try/except
    if selected_df.empty:
        st.warning("Select filter(s) to continue.")
    else:
        # Summary statistics
        # [ST2] At least three Streamlit different widgets (sliders, drop-downs, multi-selects, text boxes, etc.)
        col1, col2 = st.columns(2)
        col1.metric(label="Total Airports", value=len(selected_df))
        col2.metric(label="Average Elevation", value=f"{round(selected_df['elevation_ft'].sum() / len(selected_df),2)} ft.")
        # Filterable map
        custom_map(selected_df)
        # [DA6] Analyze data with pivot tables
        dftypes = selected_df.pivot_table(values='name', index='type', aggfunc = 'count') # used with pie chart below
        dfcity = selected_df.pivot_table(values='name', index=['municipality', 'state'], aggfunc = 'count') # used with bar chart below
        # Charts
        col3, col4 = st.columns(2)
        with col3:
            display_pie(dftypes) # pie chart of 'types'
        with col4:
            display_bar(dfcity) # bar chart of 'top cities'
    st.dataframe(selected_df, use_container_width=True)
    # [ST3] At least three Streamlit different widgets (sliders, drop-downs, multi-selects, text boxes, etc.)
    # st.switch_page("final_project.py")
    # st.switch_page('type_v._service.py')

def main():
    data_file = 'new_england_airports.csv'
    df = clean_data(data_file)
    website_setup(df)

if __name__ == "__main__":
    main()
