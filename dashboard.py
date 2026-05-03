# Used to build interactive web dashboard
import streamlit as st 
# Used for loading and manipulating SQL
import pandas as pd
#used to connect Python to SQL Server database
import pyodbc
import plotly.express as px

# Configure dashboard title and wide screen layout

st.set_page_config(
    page_title="Home Energy Grant Dashboard",
    layout="wide"
)

st.title("Home Energy Grant Dashboard")

# SQL Server connection

conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EnergyGrantsDB;"
    "Trusted_Connection=yes;"
)

# Sidebar filter

st.sidebar.header("Filters")

county_filter = st.sidebar.selectbox(
    "Select County",
    ["All", "Mayo", "Galway", "Dublin", "Sligo"]
)

status_filter = st.sidebar.selectbox(
    "Application Status",
    ["All", "Approved", "Pending", "Rejected"]
)

# Dynamic SQL filtering

county_sql = ""

if county_filter != "All":
    county_sql = f" WHERE county = '{county_filter}' "


# KPI Metric cards

query_total_applications = f"""
SELECT COUNT(*) AS total
FROM Application a
JOIN Property p
    ON a.property_id = p.property_id
{county_sql}
"""

query_total_properties = f"""
SELECT COUNT(*) AS total
FROM Property
{county_sql}
"""

query_total_contractors = """
SELECT COUNT(*) AS total
FROM Contractor
"""

query_total_grants = f"""
SELECT SUM(ag.approved_amount) AS total
FROM Application_Grant ag
JOIN Application a
    ON ag.application_id = a.application_id
JOIN Property p
    ON a.property_id = p.property_id
{county_sql}
"""

# Push KPI data into pandas dataframes

df_total_applications = pd.read_sql(query_total_applications, conn)
df_total_properties = pd.read_sql(query_total_properties, conn)
df_total_contractors = pd.read_sql(query_total_contractors, conn)
df_total_grants = pd.read_sql(query_total_grants, conn)

# Displays KPI data side-by-side instead of stacked

col1, col2, col3, col4 = st.columns(4)

# KPI data displayed as high-level business metrics for quick analysis

with col1:
    st.metric(
        "Applications",
        int(df_total_applications["total"][0])
    )

with col2:
    st.metric(
        "Properties",
        int(df_total_properties["total"][0])
    )

with col3:
    st.metric(
        "Contractors",
        int(df_total_contractors["total"][0])
    )

with col4:
    total_grants = df_total_grants["total"][0]
    if pd.isna(total_grants):
        total_grants = 0

    st.metric(
        "Approved Grants",
        f"€{int(total_grants):,}"
    )

# Map Data using property coordinates for an interactive map

map_query = f"""
SELECT
    latitude,
    longitude,
    town,
    county,
    ber_rating
FROM Property
{county_sql}
AND latitude IS NOT NULL
AND longitude IS NOT NULL
"""

if county_filter == "All":

    map_query = """
    SELECT
        latitude,
        longitude,
        town,
        county,
        ber_rating
    FROM Property
    WHERE latitude IS NOT NULL
    AND longitude IS NOT NULL
    """

# Load map data

map_df = pd.read_sql(map_query, conn)

# Uses latitude and longitude coordinates stored in SQL

st.subheader("Property Locations")
st.map(map_df)

# Applications by County chart using plotly

county_query = f"""
SELECT
    county,
    COUNT(*) AS total_properties
FROM Property
{county_sql}
GROUP BY county
"""

if county_filter == "All":
    county_query = """
    SELECT
        county,
        COUNT(*) AS total_properties
    FROM Property
    GROUP BY county
    """

county_df = pd.read_sql(county_query, conn)

# Create interactive bar chart

fig_county = px.bar(
    county_df,
    x="county",
    y="total_properties",
    title="Applications by County",
    labels={
        "county": "County",
        "total_properties": "Total Properties"
    }
)

fig_county.update_layout(
    title_x=0.3
)

st.plotly_chart(
    fig_county,
    use_container_width=True
)

# Create pie chart of application statuses 

status_query = f"""
SELECT
    a.status,
    COUNT(*) AS total
FROM Application a

JOIN Property p
    ON a.property_id = p.property_id
{county_sql}
GROUP BY a.status
"""

if county_filter == "All":
    status_query = """
    SELECT
        status,
        COUNT(*) AS total
    FROM Application
    GROUP BY status
    """

status_df = pd.read_sql(status_query, conn)

fig_status = px.pie(
    status_df,
    names="status",
    values="total",
    title="Application Status Breakdown",
    height=900
)

fig_status.update_layout(

    title_x=0.3,

    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=0.82,
        font=dict(
            size=20
        )
    ),

    font=dict(
        size=18
    )
)


fig_status.update_traces(
    textfont_size=20
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)

# Create recent applications table

recent_query = f"""
SELECT TOP 20
    a.application_id AS [Application ID],
    h.first_name AS [First Name],
    h.last_name AS [Second Name],
    p.county AS [County],
    a.status AS [Status],
    ag.approved_amount AS [Approved Amount]
FROM Application a

JOIN Property p
    ON a.property_id = p.property_id

JOIN Homeowner h
    ON p.homeowner_id = h.homeowner_id

JOIN Application_Grant ag
    ON a.application_id = ag.application_id

{county_sql}

ORDER BY a.application_id DESC
"""

if county_filter == "All":

    recent_query = """
    SELECT TOP 20
        a.application_id AS [Application ID],
        h.first_name AS [First Name],
        h.last_name AS [Second Name],
        p.county AS [County],
        a.status AS [Status],
        ag.approved_amount AS [Approved Amount]
    FROM Application a

    JOIN Property p
        ON a.property_id = p.property_id

    JOIN Homeowner h
        ON p.homeowner_id = h.homeowner_id

    JOIN Application_Grant ag
        ON a.application_id = ag.application_id

    ORDER BY a.application_id DESC
    """

recent_df = pd.read_sql(recent_query, conn)

recent_df["Approved Amount"] = recent_df["Approved Amount"].apply(
    lambda x: f"€{x:,.2f}"
)

st.subheader("Recent Applications")

styled_df = recent_df.style.set_properties(
    **{
        "text-align": "center"
    }
)

styled_df = styled_df.set_table_styles(
    [
        {
            "selector": "th",
            "props": [
                ("text-align", "center")
            ]
        }
    ]
)

st.dataframe(
    styled_df,
    use_container_width=True
)

conn.close()