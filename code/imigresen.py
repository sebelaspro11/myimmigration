import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="MYEntrance",
    page_icon="🛂", layout="wide"
)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load your CSV data
@st.cache_data(ttl=None)
df = pd.read_csv("data/imigresen.csv")
df['Date'] = pd.to_datetime(df['Date'])  # Ensure the Date column is in datetime64 format

# Drop 'Unnamed: 0' column if it exists
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Streamlit app title
st.title("International Arrivals to Malaysia")
st.subheader("Data from Immigration Department of Malaysia [data.gov.my](https://data.gov.my/data-catalogue/arrivals_soe)")

st.markdown("---")


# Convert Date column to month and year format for display
df['Month-Year'] = df['Date'].dt.strftime('%b %Y')

# Extract unique months and years from the data
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.strftime('%B')

# Define the list of months in correct order
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


# Filter by Origin Country
origin_country_filter = st.multiselect('Select Nationality:', df['Nationality'].unique(), default=[])



# Filter by State
state_filter = st.multiselect('Select State of Entry:', df['State of Entry'].unique(), default=[])






# Create columns layout for selecting filters
col1, col2 = st.columns(2)

# In Column 1: Select Start Date (Month and Year)
with col1:
    st.write("Select Start Year-Month:")
    start_year = st.selectbox('Start Year', df['Year'].unique(), index=0)  # Default to earliest year
    start_month = st.selectbox('Start Month', df[df['Year'] == start_year]['Month'].unique(), index=0)  # Months available for selected year

# In Column 2: Select End Date (Month and Year)
with col2:
    st.write("Select End Year-Month:")
    end_year = st.selectbox('End Year', df['Year'].unique(), index=len(df['Year'].unique()) - 1)  # Default to latest year
    end_month = st.selectbox('End Month', df[df['Year'] == end_year]['Month'].unique(), index=len(df[df['Year'] == end_year]['Month'].unique()) - 1)  # Months available for selected year

# Convert the selected month/year to a datetime object
start_date = pd.to_datetime(f"{start_year}-{months.index(start_month) + 1}-01")
end_date = pd.to_datetime(f"{end_year}-{months.index(end_month) + 1}-01")
end_date = end_date + pd.offsets.MonthEnd(1)  # Ensure end_date is the last day of the selected month

# Apply filters based on user selection
if state_filter:
    filtered_df = df[df['State of Entry'].isin(state_filter)]
else:
    filtered_df = df

if origin_country_filter:
    filtered_df = filtered_df[filtered_df['Nationality'].isin(origin_country_filter)]

# Filter data by date range
filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

st.markdown("---")


# Display totals
st.subheader("Total Arrivals Summary")

# Show overall totals if no filters for state or origin country are selected
if not state_filter and not origin_country_filter:
    total_arrivals = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]['Total Arrivals'].sum()
    st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#21ff46 ;'>Total Arrivals to Malaysia: {total_arrivals:,}</p>", unsafe_allow_html=True)

else:
    # If filters are applied, group by state and origin country as appropriate
    if state_filter and origin_country_filter:
        grouped_data = filtered_df.groupby(['Nationality', 'State of Entry'])['Total Arrivals'].sum().reset_index()
        for _, row in grouped_data.iterrows():
            st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#21ff46;'>Total {row['Nationality']} Citizens Entrance from {row['State of Entry']}: {row['Total Arrivals']:,}</p>", unsafe_allow_html=True)

    elif origin_country_filter:
        grouped_data = filtered_df.groupby('Nationality')['Total Arrivals'].sum().reset_index()
        for _, row in grouped_data.iterrows():
            st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#21ff46;'>Total {row['Nationality']} Citizens Entrance to Malaysia: {row['Total Arrivals']:,}", unsafe_allow_html=True)
            #st.write(f"Total {row['Nationality']} Citizens Entrance to Malaysia: {row['Total Arrivals']:,}")
    elif state_filter:
        grouped_data = filtered_df.groupby('State of Entry')['Total Arrivals'].sum().reset_index()
        for _, row in grouped_data.iterrows():
            st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#21ff46;'>Total Entrance from {row['State of Entry']}: {row['Total Arrivals']:,}", unsafe_allow_html=True)
            #st.write(f"Total Entrance from {row['State of Entry']}: {row['Total Arrivals']:,}")

st.markdown("---")


# Line Chart of Total Arrivals
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Arrivals over Month-Year")

    if not filtered_df.empty:
        # If no state is selected, show data for all states
        if not state_filter:
            # Group by Month_Year and Origin Country for all states
            line_chart_data = filtered_df.groupby(['Month-Year', 'Nationality'])['Total Arrivals'].sum().reset_index()

            # Convert Month_Year to datetime for sorting
            line_chart_data['Month-Year'] = pd.to_datetime(line_chart_data['Month-Year'], format='%b %Y')
            line_chart_data = line_chart_data.sort_values(by='Month-Year')

            # Create line chart using Plotly Express for all states
            fig_line = px.line(line_chart_data, x='Month-Year', y='Total Arrivals', color='Nationality',
                               title='Total Arrivals Over Time for All States')

            # Customize x-axis tick format
            fig_line.update_xaxes(
                tickformat="%Y %b",  # Display format: Year Month (e.g., 2020 Jan)
                tickangle=-45  # Optional: Rotate the ticks for better readability
            )

            st.plotly_chart(fig_line, use_container_width=True)

        else:
            # Loop through each selected state and generate a line chart
            for state in state_filter:
                state_data = filtered_df[filtered_df['State of Entry'] == state]

                if not state_data.empty:
                    # Group by Month_Year and Origin Country, aggregate total arrivals for this state
                    line_chart_data = state_data.groupby(['Month-Year', 'Nationality'])['Total Arrivals'].sum().reset_index()

                    # Convert Month_Year to datetime for sorting
                    line_chart_data['Month-Year'] = pd.to_datetime(line_chart_data['Month-Year'], format='%b %Y')
                    line_chart_data = line_chart_data.sort_values(by='Month-Year')

                    # Create line chart using Plotly Express for the specific state
                    fig_line = px.line(line_chart_data, x='Month-Year', y='Total Arrivals', color='Nationality',
                                       title=f'Total Arrivals Over Time for {state}')

                    # Customize x-axis tick format
                    fig_line.update_xaxes(
                        tickformat="%Y %b",  # Display format: Year Month (e.g., 2020 Jan)
                        tickangle=-45  # Optional: Rotate the ticks for better readability
                    )

                    st.plotly_chart(fig_line, use_container_width=True)



with col2:
    st.subheader("Male and Female Arrivals")
    custom_color = ["#fc112a","#e01cff"]
    if not filtered_df.empty:
        # If no state is selected, show data for all states
        if not state_filter:
            # Group by Month_Year and sum Male and Female arrivals for all states
            pie_chart_data = filtered_df.groupby(['Month-Year'])[['Male Arrivals', 'Female Arrivals']].sum().reset_index()

            # Create pie chart for Male and Female Arrivals using Plotly Express
            fig_pie = px.pie(
                names=['Male Arrivals', 'Female Arrivals'],
                values=[pie_chart_data['Male Arrivals'].sum(), pie_chart_data['Female Arrivals'].sum()],
                title='Total Male and Female Arrivals to Malaysia',
                color_discrete_sequence=custom_color
            )
            fig_pie.update_traces(textinfo='value+percent', textfont=dict(size=18))

            st.plotly_chart(fig_pie, use_container_width=True)

        else:
            # Loop through each selected state and generate a pie chart
            
            
            for state in state_filter:
                state_data = filtered_df[filtered_df['State of Entry'] == state]

                if not state_data.empty:
                    # Group by Month_Year and sum Male and Female arrivals for the specific state
                    pie_chart_data = state_data.groupby(['Month-Year'])[['Male Arrivals', 'Female Arrivals']].sum().reset_index()

                    # Create pie chart for Male and Female Arrivals using Plotly Express
                    fig_pie = px.pie(
                        names=['Male Arrivals', 'Female Arrivals'],
                        values=[pie_chart_data['Male Arrivals'].sum(), pie_chart_data['Female Arrivals'].sum()],
                        title=f'Male and Female Arrivals for {state}',
                        color_discrete_sequence=custom_color
                    )
                    fig_pie.update_traces(textinfo='value+percent', textfont=dict(size=18))

                    st.plotly_chart(fig_pie, use_container_width=True)



st.markdown("---")


# Display filtered data
st.subheader("Raw Data")
# Reset index and start from 1
filtered_df_display = filtered_df[["State of Entry", "Nationality", "Total Arrivals", "Male Arrivals", "Female Arrivals", "Month-Year"]].reset_index(drop=True)
filtered_df_display.index += 1  # Start index from 1

# Display the dataframe with the updated index
st.dataframe(filtered_df_display, use_container_width=True)
