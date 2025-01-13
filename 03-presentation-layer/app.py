import streamlit as st
import pandas as pd
import json


# Load JSON data from the file
@st.cache_data
def load_data():
    with open("../test/oetv-rankings.json", "r") as file:
        data = json.load(file)
    return data


data = load_data()

# Convert data to DataFrame
df = pd.DataFrame(data)

# Display data in a table
st.title("Tennis Player Rankings")
st.write(
    "This table displays the rankings of tennis players as recorded in the JSON data file."
)
st.dataframe(df)
