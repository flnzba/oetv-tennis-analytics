import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Constants
BASE_URL = 'https://www.oetv.at/rangliste/oetv?page='
DB_PATH = 'data.sqlite'

# Function to scrape data across pages
def scrape_data(base_url):
    all_data = []
    page = 1
    while True:
        response = requests.get(f"{base_url}{page}")
        if "no more data" in response.text:  # Adjust this condition based on how the end of data is indicated on the website
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        # You need to modify the next line based on the actual data you want to scrape
        data = [(item.text.strip()) for item in soup.find_all('your_target_element')]
        all_data.extend(data)
        page += 1  # Increment page number
    return all_data

# Function to store data in SQLite
def store_data(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rankings (rank TEXT)''')
    c.executemany('''INSERT INTO rankings (rank) VALUES (?)''', ((d,) for d in data))
    conn.commit()
    conn.close()

# Function to fetch data from SQLite
def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM rankings", conn)
    conn.close()
    return df

# Function to plot data
def plot_data(df):
    df['count'] = df.groupby('rank')['rank'].transform('count')
    plt.figure(figsize=(10, 5))
    plt.bar(df['rank'].unique(), df['count'].unique())
    plt.xlabel('Rank')
    plt.ylabel('Frequency')
    plt.title('Rank Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

# Streamlit app
def main():
    st.title('Data Visualization App')
    data = scrape_data(BASE_URL)
    store_data(data)
    df = fetch_data()
    fig = plot_data(df)
    st.pyplot(fig)

if __name__ == "__main__":
    main()