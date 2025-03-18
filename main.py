import pandas as pd
import streamlit as st
import sqlalchemy
import plotly.express as px

path = "Global_Music_Streaming_Listener_Preferences.csv"
engine = sqlalchemy.create_engine('sqlite:///music_streaming.db')
pd.read_csv(path).to_sql("data", con=engine, if_exists='replace', index=False)
conn = engine.connect()

st.title("Music Listener Insights")

#Bar Chart: X-axis is age, Y-axis is count. Multiple bars per each age to represent different streaming platforms
container2 = st.container(border=True)
container2.header("Distribution of streaming platform by age")
col1, col2 = container2.columns(2)
ageRange = col1.slider("Select an age range to view", min_value=13, max_value=60, value=(13, 60))
platforms = col2.multiselect("Select platforms to view", pd.read_sql_query("SELECT DISTINCT [Streaming Platform] as Platform FROM data", conn), default="Spotify")
if platforms:
    query2 = '''
    SELECT Age, [Streaming Platform] as Platform, Count([Streaming Platform]) as Count
    FROM data
    WHERE Age Between ? AND ?
    AND Platform in ({})
    GROUP BY Age, Platform
'''.format(",".join(["?"] * len(platforms)))
    query_result = pd.read_sql_query(query2, conn, params=(ageRange[0], ageRange[1], *platforms))
    if not query_result.empty:
        df_pivot = query_result.pivot(index = "Age", columns="Platform", values = "Count");
        container2.bar_chart(df_pivot, stack=False)
    else:
        container2.error("No data found")
else: 
    container2.error("Select at least one platform")

# Show Top 5 Artists by how many people they are the most played artist for
container1 = st.container(border=True)
container1.header("Top artists by country")
country = container1.selectbox("Country", pd.read_sql_query("SELECT Country from data GROUP BY Country", conn))
col1, col2 = container1.columns(2)
if country:
    query1 = '''
    SELECT [Most Played Artist], COUNT([Most Played Artist]) as Count
    FROM data
    WHERE Country = ?
    GROUP BY [Most Played Artist]
    ORDER BY Count
    LIMIT 5
'''
query_result = pd.read_sql_query(query1, conn, params=(country,))
col1.write("Top 5 Most Played Artists in {}".format(country))
col1.dataframe(query_result.set_index("Most Played Artist"))

pieChart = px.pie(data_frame=query_result, names="Most Played Artist", values="Count", color_discrete_sequence=px.colors.sequential.Blackbody)
col2.plotly_chart(pieChart)

# Show amount of listeners by country filtered by age
container3 = st.container(border=True)
container3.header("Listeners in each country by age")
age = container3.slider("Select an age", 13, 60, step=1)
if age:
    query3 = '''
    SELECT Country, COUNT(*) as Count
    FROM data
    WHERE Age = ?
    GROUP BY Country    
'''
    query_result = pd.read_sql_query(query3, conn, params=(age,))
    if not query_result.empty:
        bar = container3.bar_chart(query_result.set_index("Country"), x_label="Country", y_label="# of {} year old listeners".format(age))
    else:
        container3.write("No data found")
else:
    container3.write("Please select an age")


