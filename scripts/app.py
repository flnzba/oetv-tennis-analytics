import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# import json

# # Load JSON data
# with open("../test/oetv-rankings.json", "r") as f:
#     data = json.load(f)

# Load data from SQLite database
conn = sqlite3.connect("data.db")
query = "SELECT * FROM players"
data = pd.read_sql_query(query, conn)
conn.close()

df = pd.DataFrame(data)

# Streamlit page config
st.set_page_config(page_title="Tennis Rankings Dashboard", layout="wide")

st.sidebar.markdown("### 🎾 Player Rankings")

# Sidebar Filters
st.sidebar.header("Filter Options")
rank_filter_min = st.sidebar.number_input(
    "Min Rank",
    min_value=1.0,
    max_value=float(df["fedRank"].max()),
    value=1.0,
)
rank_filter_max = st.sidebar.number_input(
    "Max Rank",
    min_value=rank_filter_min,
    max_value=float(df["fedRank"].max()),
    value=10.0,
)
rank_filter = (rank_filter_min, rank_filter_max)

age_filter = st.sidebar.slider(
    "Filter by Age Spectrum",
    min_value=int(df["birthYear"].min()),
    max_value=int(df["birthYear"].max()),
    value=(1990, int(df["birthYear"].max())),
)

st.sidebar.markdown("---")

st.sidebar.header("Input Options")
# New User Input Field
user_fed_rank = st.sidebar.number_input(
    "Enter Your ITN",
    min_value=1.0,
    max_value=float(df["fedRank"].max()),
    value=8.2,
)

# Apply filters
df_filtered = df[
    (df["fedRank"] >= rank_filter[0])
    & (df["fedRank"] <= rank_filter[1])
    & (df["birthYear"] >= age_filter[0])
    & (df["birthYear"] <= age_filter[1])
]

# Calculate ranking percentile
percentile = (df["fedRank"] > user_fed_rank).sum() / len(df) * 100

# Calculate ranking percentile
players_above = (df["fedRank"] < user_fed_rank).sum()
players_below = (df["fedRank"] > user_fed_rank).sum()

# Custom TailwindCSS for styling
st.markdown(
    """
    <style>
    body {font-family: 'Inter', sans-serif;}
    .main-title {font-size: 36px; font-weight: bold; color: #374151;}
    .sub-title {font-size: 20px; color: #6B7280;}
    .chart-container {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);}
    </style>
    """,
    unsafe_allow_html=True,
)

# Dashboard Header
st.markdown(
    "<h1 class='main-title'>🎾 Tennis Rankings Dashboard</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p class='sub-title'>Visualizing ATP Player Rankings</p>", unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Rank Percentile")
    fig, ax = plt.subplots(figsize=(10, 10))
    labels = [
        "Better than {:.1f}% of Players".format(percentile),
        "Worse than {:.1f}% of Players".format(100 - percentile),
    ]
    ax.pie(
        [percentile, 100 - percentile],
        labels=labels,
        autopct="%1.1f%%",
        colors=["green", "red"],
        startangle=90,
    )
    ax.set_title("Your Relative Rank Position")

    st.pyplot(fig)

with col2:
    st.subheader("Players Above and Below Your Rank")
    fig, ax = plt.subplots(figsize=(10, 10))
    labels = ["Players Above", "Players Below"]
    ax.bar(
        labels,
        [players_above, players_below],
        color=["red", "green"],
    )
    ax.set_ylabel("Number of Players")
    ax.set_title("Comparison of Players Above and Below Your Rank")
    st.pyplot(fig)

# Another Row for more visualizations
col3, col4 = st.columns(2)

# Visualization 3: ATP Points Distribution (Bar Chart - Fixed)
with col3:
    st.subheader("ATP Points Distribution")
    fig, ax = plt.subplots(figsize=(10, 10))  # Set the figure size
    df_filtered_sorted = df_filtered.sort_values("atpPoints", ascending=False).head(10)
    ax.bar(
        df_filtered_sorted["lastname"], df_filtered_sorted["atpPoints"], color="crimson"
    )
    ax.set_xticks(range(len(df_filtered_sorted["lastname"])))
    ax.set_xticklabels(df_filtered_sorted["lastname"], rotation=45, ha="right")
    ax.set_ylabel("ATP Points")
    ax.set_title("ATP Points by Players")
    st.pyplot(fig)

# Visualization 4: Tournament Points Breakdown (Bar Chart)
with col4:
    st.subheader("Points Distribution")
    fig, ax = plt.subplots(figsize=(10, 10))  # Set the figure size
    df_filtered_sorted = df_filtered.sort_values("points", ascending=False).head(10)
    ax.bar(
        df_filtered_sorted["lastname"], df_filtered_sorted["points"], color="crimson"
    )
    ax.set_xticks(range(len(df_filtered_sorted["lastname"])))
    ax.set_xticklabels(df_filtered_sorted["lastname"], rotation=45, ha="right")
    ax.set_ylabel("Points")
    ax.set_title("Points by Players")
    st.pyplot(fig)

# Another Row for more visualizations
col5, col6 = st.columns(2)

# Visualization 5: Federation Distribution (Bar Chart)
with col5:
    st.subheader("Federation Distribution")
    fig, ax = plt.subplots(figsize=(10, 10))  # Set the figure size
    df_filtered["fedNickname"].value_counts().plot(kind="bar", ax=ax, color="darkcyan")
    ax.set_xlabel("Federation")
    ax.set_ylabel("Number of Players")
    ax.set_title("Players per Federation")
    st.pyplot(fig)

# Visualization 6: Birth Year Distribution (Donut Chart)
with col6:
    st.subheader("Birth Year Distribution")
    fig, ax = plt.subplots(figsize=(10, 10))  # Set the figure size
    df_filtered["birthYear"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90,
        cmap="coolwarm",
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        pctdistance=0.85,
    )
    ax.set_ylabel("")
    st.pyplot(fig)

st.markdown(
    "<p class='sub-title'>Dashboard built by <a href='https://fzeba.com'> Florian Zeba <a/> 🎾 </p>",
    unsafe_allow_html=True,
)
