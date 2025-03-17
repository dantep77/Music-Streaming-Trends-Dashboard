import pandas as pd
import streamlit as st
import sqlalchemy
import plotly.express as px

path = "Global_Music_Streaming_Listener_Preferences.csv"
engine = sqlalchemy.create_engine('sqlite:///music_streaming.db')
pd.read_csv(path).to_sql("data", con=engine, if_exists='replace', index=False)
conn = engine.connect()

st.title("Music Listener Insights")

# Show Top 5 Artists by how many people they are the most played artist for
country = st.selectbox("Country", pd.read_sql_query("SELECT Country from data GROUP BY Country", conn))
col1, col2 = st.columns(2)
query_result = pd.read_sql_query("SELECT [Most Played Artist], COUNT([Most Played Artist]) as Count from data WHERE Country = '" + country + "' GROUP BY [Most Played Artist] ORDER BY Count LIMIT 5", conn)
col1.write("Top 5 Most Played Artists in " + country)
col1.dataframe(query_result.set_index("Most Played Artist"))

pieChart = px.pie(data_frame=query_result, names="Most Played Artist", values="Count", color_discrete_sequence=px.colors.sequential.Blackbody)
col2.plotly_chart(pieChart)

# Show amount of listeners by country filtered by age
age = st.slider("Select an age", 13, 60, step=1)
query_result = pd.read_sql_query("SELECT Country, COUNT(*) as Count FROM data WHERE Age = "+ str(age) + " GROUP BY Country", conn)
bar = st.bar_chart(query_result.set_index("Country"), x_label="Country", y_label="# of " + str(age) + "year old listeners")

