import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json


# Load JSON data from the file
# @st.cache_data
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

# Create a 2x2 grid for the plots
fig, axs = plt.subplots(2, 2, figsize=(20, 20))  # Adjust the figure size as needed

# Plot 1: Bar Chart of ATP Points
top_players = df.sort_values(by="points", ascending=False).head(100).tail(20)
axs[0, 0].bar(top_players["lastname"], top_players["points"], color="skyblue")
axs[0, 0].set_title("Points of Top Players")
axs[0, 0].set_xticklabels(top_players["lastname"], rotation=45, ha="right")
axs[0, 0].set_xticks(range(len(top_players["lastname"])))

# Plot 2: Pie Chart of Federation Nicknames
fed_counts = df["fedNickname"].value_counts()
axs[0, 1].pie(fed_counts, labels=fed_counts.index, autopct="%1.1f%%", startangle=90)
axs[0, 1].set_title("Distribution of Players by Federation Nickname")
axs[0, 1].axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

# Plot 3: Line Chart of Points by Birth Year
avg_points_by_year = df.groupby("birthYear")["points"].mean()
axs[1, 0].plot(avg_points_by_year.index, avg_points_by_year, marker="o", linestyle="-")
axs[1, 0].set_title("Total Points by Birth Year")
axs[1, 0].set_xlabel("Birth Year")
axs[1, 0].set_ylabel("Average Points")

# Plot 4: Scatter Plot of ATP Points vs Total Points
sns.scatterplot(data=df, x="atpPoints", y="points", ax=axs[1, 1])
axs[1, 1].set_title("ATP Points vs Total Points")

# Adjust layout and show the plots in Streamlit
plt.tight_layout()
st.pyplot(fig)
