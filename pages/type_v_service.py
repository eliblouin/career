import streamlit as st
import pandas as pd
import scipy.stats as stats

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

def unique_list(df):
    type_list = df.type.unique()
    return type_list

def chisq(df):
    contingency_table = pd.crosstab(df['type'], df['scheduled_service'])
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
    return chi2, p

def p_result(p_value):
    if p_value < 0.05:
        st.header('They ARE significantly associated!')
    else:
        st.header('They ARE NOT significantly associated!')

def website_setup(df, colork = 'yellow'):
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #D5FBFD;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("Chi-Sq. Association Test")
    st.text("What's the deal with a scheduled service?! This page seeks to test whether or not there is a significant association between the airport variable 'type' and 'scheduled_service'.")
    type_list = unique_list(df)
    var1 = st.sidebar.radio('Type 1:', type_list)
    var2 = st.sidebar.radio('Type 2:', type_list)

    # [DA5] Filter data by two or more conditions with AND/OR
    dfchi = df[(df["type"] == var1) | (df["type"] == var2)][['name', 'type', 'scheduled_service']]
    chi, p_value = chisq(dfchi)
    st.markdown(f"_Is a {var1} more likely to have a scheduled service than a {var2}?_")
    st.text(f"Chi-Square Statistic: {round(chi, 4)}")
    st.text(f"P-Value: {p_value}")
    p_result(p_value)
    # Prints data frame of selected types and service
    st.dataframe(dfchi, use_container_width=True)

def main():
    data_file = 'new_england_airports.csv'
    df = clean_data(data_file)
    website_setup(df)

if __name__ == "__main__":
    main()
