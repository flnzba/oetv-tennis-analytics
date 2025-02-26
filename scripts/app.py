import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import seaborn as sns
import numpy as np
import math
from matplotlib.colors import LinearSegmentedColormap

# import json

# # Load JSON data
# with open("../test/oetv-rankings.json", "r") as f:
#     data = json.load(f)

# Database path - must match the path used in transform.py
# Get the base directory from environment or use a default
# This allows configuration in Docker environments
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(DATA_DIR, "data.db")

# Streamlit page config
st.set_page_config(page_title="Tennis Rankings Dashboard", layout="wide")

st.sidebar.markdown(f"Database path: {db_path}")

# Check if the database file exists
if not os.path.exists(db_path):
    st.error(f"Database file not found at {db_path}. Please run transform.py first to create the database.")
    st.stop()

# Load data from SQLite database
conn = sqlite3.connect(db_path)
query = "SELECT * FROM players"
data = pd.read_sql_query(query, conn)
conn.close()

df = pd.DataFrame(data)

# Check if we have data
if df.empty:
    st.error("No data found in the database. Please run transform.py to populate the database with player data.")
    st.stop()

# Calculate player age from birth year
current_year = pd.Timestamp.now().year
df['age'] = current_year - df['birthYear']

# Sidebar Filters
st.sidebar.header("🎾 Tennis Rankings Dashboard")
st.sidebar.markdown("---")

st.sidebar.header("Filter Options")

# Player Search
st.sidebar.subheader("Player Search")
search_query = st.sidebar.text_input("Search by player name")

# Rank Filter
st.sidebar.subheader("Ranking")
# Ensure min and max are different for the inputs
rank_min = float(df["fedRank"].min())
rank_max = float(df["fedRank"].max())
if rank_min == rank_max:
    rank_max = rank_min + 1.0  # Ensure they're different
elif rank_max - rank_min < 0.1:
    rank_max = rank_min + 0.1  # Ensure there's at least 0.1 difference

rank_filter_min = st.sidebar.number_input(
    "Min Rank",
    min_value=rank_min,
    max_value=rank_max,
    value=rank_min,
)
rank_filter_max = st.sidebar.number_input(
    "Max Rank",
    min_value=rank_filter_min,
    max_value=rank_max,
    value=min(rank_filter_min + 9.0, rank_max),  # Default to showing a reasonable range
)
rank_filter = (rank_filter_min, rank_filter_max)

# Age filter
st.sidebar.subheader("Age & Birth Year")
# Ensure min and max are different for the slider
birth_year_min = int(df["birthYear"].min())
birth_year_max = int(df["birthYear"].max())
if birth_year_min == birth_year_max:
    birth_year_max = birth_year_min + 1  # Ensure they're different

age_filter = st.sidebar.slider(
    "Filter by Birth Year",
    min_value=birth_year_min,
    max_value=birth_year_max,
    value=(min(1990, birth_year_max), birth_year_max),
)

# Federation Filter
st.sidebar.subheader("Federation")
federations = ['All'] + sorted(df['fedNickname'].unique().tolist())
selected_federation = st.sidebar.selectbox("Select Federation", federations)

# Club Filter
st.sidebar.subheader("Club")
# Get top clubs by player count
top_clubs = df['clubName'].value_counts().head(20).index.tolist()
club_options = ['All'] + ['Top 20 Clubs'] + sorted(top_clubs)
selected_club = st.sidebar.selectbox("Select Club", club_options)

# Points Filter
st.sidebar.subheader("Points")
# Ensure min and max are different for the slider
points_min = int(df["points"].min())
points_max = int(df["points"].max())
if points_min == points_max:
    points_max = points_min + 1  # Ensure they're different

points_range = st.sidebar.slider(
    "Filter by Points Range",
    min_value=points_min,
    max_value=points_max,
    value=(points_min, points_max),
)

st.sidebar.markdown("---")

st.sidebar.header("Personal Comparison")
# User Input Field
user_fed_rank = st.sidebar.number_input(
    "Enter Your ITN",
    min_value=1.0,
    max_value=float(df["fedRank"].max()),
    value=8.2,
)

# Apply all filters
df_filtered = df.copy()

# Apply search filter if provided
if search_query:
    df_filtered = df_filtered[
        df_filtered['firstname'].str.contains(search_query, case=False) | 
        df_filtered['lastname'].str.contains(search_query, case=False)
    ]

# Apply other filters
df_filtered = df_filtered[
    (df_filtered["fedRank"] >= rank_filter[0]) &
    (df_filtered["fedRank"] <= rank_filter[1]) &
    (df_filtered["birthYear"] >= age_filter[0]) &
    (df_filtered["birthYear"] <= age_filter[1]) &
    (df_filtered["points"] >= points_range[0]) &
    (df_filtered["points"] <= points_range[1])
]

# Apply federation filter
if selected_federation != 'All':
    df_filtered = df_filtered[df_filtered['fedNickname'] == selected_federation]

# Apply club filter
if selected_club != 'All':
    if selected_club == 'Top 20 Clubs':
        df_filtered = df_filtered[df_filtered['clubName'].isin(top_clubs)]
    else:
        df_filtered = df_filtered[df_filtered['clubName'] == selected_club]

# Calculate ranking percentile for user comparison
percentile = (df["fedRank"] > user_fed_rank).sum() / len(df) * 100

# Calculate players above and below user's rank
players_above = (df["fedRank"] < user_fed_rank).sum()
players_below = (df["fedRank"] > user_fed_rank).sum()

# Custom styling
st.markdown(
    """
    <style>
    body {font-family: 'Inter', sans-serif;}
    .main-title {font-size: 36px; font-weight: bold; color: #374151;}
    .sub-title {font-size: 20px; color: #6B7280;}
    .chart-container {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);}
    /* Improved tab list styling with more space */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        padding: 0 10px;
        margin-bottom: 10px;
    }
    /* Enhanced tab styling with more padding */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 6px 6px 0px 0px;
        padding: 5px 20px;
        font-weight: 500;
        border: 1px solid #e0e0e0;
        border-bottom: none;
        transition: all 0.2s ease;
    }
    /* Hover effect for inactive tabs */
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover {
        background-color: #f5f5f5;
    }
    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    /* Add padding for tab content */
    .stTabs [data-baseweb="tab-panel"] {padding: 20px 10px;}
    /* Style headers and subheaders in tabs */
    .stTabs h1, .stTabs h2, .stTabs h3 {
        padding: 10px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid #e0e0e0;
    }
    .stTabs .stMarkdown {padding: 5px 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Dashboard Header
st.markdown(
    "<h1 class='main-title'>🎾 Tennis Rankings Analysis Dashboard</h1>", 
    unsafe_allow_html=True
)

# Display filtered records count
st.markdown(f"### Showing {len(df_filtered)} players based on current filters")

# Create tabs for different categories of visualizations
tabs = st.tabs(["Personal Comparison", "Player Rankings", "Federation Analysis", "Age Analysis", "Club Analysis"])

# Tab 1: Personal Comparison
with tabs[0]:
    st.header("Compare Your Ranking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Rank Percentile")
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Define better colors for pie chart
        colors = ['#4CAF50', '#FF5252']
        
        # Create pie chart with better styling
        wedges, texts, autotexts = ax.pie(
            [percentile, 100 - percentile],
            labels=None,  # Remove default labels for custom positioning
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            shadow=True,
            explode=(0.05, 0),  # Slightly explode the first slice
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        # Add a legend with better positioning and styling
        labels = [
            f"Better than {percentile:.1f}% of Players",
            f"Worse than {(100 - percentile):.1f}% of Players",
        ]
        ax.legend(wedges, labels, loc="center", bbox_to_anchor=(0.5, 0.1),
                 frameon=False, fontsize=11)
        
        # Add title with better styling
        ax.set_title("Your Relative Rank Position", fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout(pad=3)
        st.pyplot(fig)

    with col2:
        st.subheader("Players Above and Below Your Rank")
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Define better colors for bar chart
        bar_colors = ['#FF5252', '#4CAF50']
        
        # Create more elegant bars
        bars = ax.bar(
            ["Players Above", "Players Below"],
            [players_above, players_below],
            color=bar_colors,
            width=0.6,
            edgecolor='white',
            linewidth=1.5
        )
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 5,
                f'{int(height):,}',
                ha='center', 
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )
        
        # Improve the styling
        ax.set_ylabel("Number of Players", fontsize=12)
        ax.set_title("Comparison of Players Above and Below Your Rank", 
                    fontsize=14, fontweight='bold', pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Set y-axis to start at 0
        ax.set_ylim(0, max(players_above, players_below) * 1.15)  # Add 15% padding
        
        fig.tight_layout(pad=3)
        st.pyplot(fig)
    
    # Find players with similar ranking to user
    similar_range = 0.5  # Range to consider as "similar"
    similar_players = df[(df['fedRank'] >= user_fed_rank - similar_range) & 
                         (df['fedRank'] <= user_fed_rank + similar_range)]
    
    st.subheader(f"Players with Similar Ranking (±{similar_range} of your ITN)")
    if not similar_players.empty:
        similar_players_display = similar_players.sort_values('fedRank')[
            ['firstname', 'lastname', 'fedRank', 'clubName', 'fedNickname', 'age']
        ].reset_index(drop=True)
        st.dataframe(similar_players_display, use_container_width=True)
    else:
        st.info("No players found with similar ranking.")

# Tab 2: Player Rankings
with tabs[1]:
    st.header("Player Rankings Analysis")
    
    col1, col2 = st.columns(2)
    
    # REPLACEMENT: Ranking vs Points Scatter Plot
    with col1:
        st.subheader("Ranking vs Points Relationship")
        if len(df_filtered) > 0:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Use a different colormap for better differentiation
            scatter = ax.scatter(
                df_filtered["fedRank"], 
                df_filtered["points"],
                alpha=0.7,
                c=df_filtered["age"],  # Color by age
                cmap="viridis",
                s=80,  # Slightly larger markers
                edgecolor='white',
                linewidth=0.5
            )
            
            # Add trend line
            try:
                z = np.polyfit(df_filtered["fedRank"], df_filtered["points"], 1)
                p = np.poly1d(z)
                x_range = np.linspace(df_filtered["fedRank"].min(), df_filtered["fedRank"].max(), 100)
                ax.plot(x_range, p(x_range), "r--", alpha=0.8, 
                      label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")
                ax.legend(loc="upper right")
            except Exception as e:
                st.warning(f"Could not calculate trend line: {e}")
            
            # Add colorbar for age
            cbar = plt.colorbar(scatter)
            cbar.set_label('Age')
            
            # Better styling
            ax.set_xlabel("Ranking (ITN)", fontsize=12)
            ax.set_ylabel("Points", fontsize=12)
            ax.set_title("Relationship Between Ranking and Points", fontsize=14, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Add a helping text annotation
            better_text = "Better players →"
            ax.annotate(better_text, xy=(0.05, 0.95), xycoords='axes fraction',
                       ha='left', va='top', fontsize=10, 
                       bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gold", alpha=0.8))
            
            fig.tight_layout(pad=3)
            st.pyplot(fig)
        else:
            st.info("No data available with current filters")

    # REPLACEMENT: Multi-attribute Analysis for Top Players
    with col2:
        st.subheader("Top Players Multi-attribute Analysis")
        if len(df_filtered) > 0:
            # Get top 5 players by points
            top_players = df_filtered.sort_values("points", ascending=False).head(5)
            
            if len(top_players) > 0:
                # Check if we have enough data to create visualization
                if len(top_players) >= 2:
                    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})
                    
                    # Categories to include in the radar chart
                    categories = ['Points', 'ITN Ranking', 'ATP Points']
                    
                    # Convert ranking to inverse scale (higher is better for visualization)
                    max_rank = df_filtered["fedRank"].max()
                    
                    # Create normalized data for radar chart
                    player_data = []
                    player_names = []
                    
                    for _, player in top_players.iterrows():
                        # Normalize all values to 0-1 range for radar chart
                        points_norm = player['points'] / df_filtered['points'].max() if df_filtered['points'].max() > 0 else 0
                        # Invert ranking so lower numbers show as better on the radar
                        rank_norm = 1 - ((player['fedRank'] - df_filtered['fedRank'].min()) / 
                                      (df_filtered['fedRank'].max() - df_filtered['fedRank'].min())) if df_filtered['fedRank'].max() > df_filtered['fedRank'].min() else 0.5
                        atp_norm = player['atpPoints'] / df_filtered['atpPoints'].max() if df_filtered['atpPoints'].max() > 0 else 0
                        
                        # Ensure we don't have NaN values
                        points_norm = 0 if np.isnan(points_norm) else points_norm
                        rank_norm = 0.5 if np.isnan(rank_norm) else rank_norm
                        atp_norm = 0 if np.isnan(atp_norm) else atp_norm
                        
                        player_data.append([points_norm, rank_norm, atp_norm])
                        player_names.append(f"{player['firstname'][0]}. {player['lastname']}")
                    
                    # Number of categories
                    N = len(categories)
                    
                    # Create angles for each category
                    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
                    
                    # Make the plot circular
                    angles += angles[:1]
                    
                    # Get colormap for players
                    colors = plt.cm.plasma(np.linspace(0, 1, len(player_data)))
                    
                    # Plot each player
                    for i, (data, name) in enumerate(zip(player_data, player_names)):
                        # Close the loop for each player
                        data = data + data[:1]
                        ax.plot(angles, data, 'o-', linewidth=2, color=colors[i], label=name, alpha=0.8)
                        ax.fill(angles, data, color=colors[i], alpha=0.1)
                    
                    # Set category labels
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories)
                    
                    # Remove radial labels and set limits
                    ax.set_yticklabels([])
                    ax.set_ylim(0, 1)
                    
                    # Add legend and title
                    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
                    ax.set_title("Top Players Performance Comparison", fontsize=14, fontweight='bold', pad=20)
                    
                    fig.tight_layout(pad=3)
                    st.pyplot(fig)
                    
                    # Also display the actual data in a table for clarity
                    st.subheader("Top Players Data")
                    display_df = top_players[['firstname', 'lastname', 'fedRank', 'points', 'atpPoints']].copy()
                    # Rename columns for better readability
                    display_df.columns = ['First Name', 'Last Name', 'ITN Ranking', 'Points', 'ATP Points']
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("Not enough players in the current selection for comparison visualization")
            else:
                st.info("No player data available with current filters")
        else:
            st.info("No data available with current filters")

# Tab 3: Federation Analysis
with tabs[2]:
    st.header("Federation Analysis")
    
    col1, col2 = st.columns(2)
    
    # Federation Distribution (Bar Chart)
    with col1:
        st.subheader("Player Distribution by Federation")
        if len(df_filtered) > 0:
            fig, ax = plt.subplots(figsize=(10, 8))
            fed_counts = df_filtered["fedNickname"].value_counts()
            fed_counts.plot(kind="bar", ax=ax, color="darkcyan")
            ax.set_xlabel("Federation")
            ax.set_ylabel("Number of Players")
            ax.set_title("Players per Federation")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No data available with current filters")

    # Federation Average Rankings
    with col2:
        st.subheader("Average Ranking by Federation")
        if len(df_filtered) > 0:
            # Get federations with at least 5 players for meaningful average
            fed_avg = df_filtered.groupby('fedNickname')['fedRank'].agg(['mean', 'count'])
            fed_avg = fed_avg[fed_avg['count'] >= 5].sort_values('mean')
            
            if not fed_avg.empty:
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.barh(fed_avg.index, fed_avg['mean'], color='teal')
                ax.set_xlabel("Average Ranking (ITN)")
                ax.set_ylabel("Federation")
                ax.set_title("Average Player Ranking by Federation")
                
                # Add count annotations
                for i, (idx, row) in enumerate(fed_avg.iterrows()):
                    ax.text(row['mean'] + 0.1, i, f"({int(row['count'])} players)", 
                           va='center', fontsize=9)
                
                ax.invert_xaxis()  # Lower rank is better, so invert the axis
                st.pyplot(fig)
            else:
                st.info("Not enough data to calculate federation averages")
        else:
            st.info("No data available with current filters")
    
    # Federation Performance Analysis
    st.subheader("Federation Performance Analysis")
    if len(df_filtered) > 0:
        try:
            # Calculate average stats by federation
            fed_stats = df_filtered.groupby('fedNickname').agg({
                'fedRank': 'mean',
                'points': 'mean',
                'atpPoints': 'mean',
                'playerId': 'count'
            }).rename(columns={'playerId': 'player_count'}).reset_index()
            
            # Only include federations with significant player count
            fed_stats = fed_stats[fed_stats['player_count'] >= 5]
            
            if not fed_stats.empty and len(fed_stats) > 1:  # Need at least 2 federations for comparison
                # Check for constant values that would break normalization
                has_variation = True
                for col in ['fedRank', 'points', 'atpPoints', 'player_count']:
                    if fed_stats[col].nunique() <= 1:
                        has_variation = False
                        st.warning(f"Not enough variation in {col} across federations for proper normalization")
                
                if has_variation:
                    # Normalize the data for the heatmap
                    cols_to_norm = ['fedRank', 'points', 'atpPoints', 'player_count']
                    
                    # For ranking, lower is better so we invert it
                    fed_stats['fedRank_normalized'] = 1 - ((fed_stats['fedRank'] - fed_stats['fedRank'].min()) / 
                                                        (fed_stats['fedRank'].max() - fed_stats['fedRank'].min()))
                    
                    # For others, higher is better
                    for col in cols_to_norm[1:]:
                        # Check for division by zero
                        if fed_stats[col].max() > fed_stats[col].min():
                            fed_stats[f'{col}_normalized'] = (fed_stats[col] - fed_stats[col].min()) / \
                                                        (fed_stats[col].max() - fed_stats[col].min())
                        else:
                            fed_stats[f'{col}_normalized'] = 0.5  # Neutral value if all values are the same
                    
                    # Display the normalized data in a heatmap
                    fig, ax = plt.subplots(figsize=(12, len(fed_stats)/2 + 3))
                    
                    # Data for heatmap
                    heatmap_data = fed_stats[['fedNickname', 'fedRank_normalized', 
                                            'points_normalized', 'atpPoints_normalized', 
                                            'player_count_normalized']]
                    
                    # Reshape for heatmap
                    heatmap_data = heatmap_data.set_index('fedNickname')
                    heatmap_data.columns = ['Ranking', 'Points', 'ATP Points', 'Player Count']
                    
                    # Create custom colormap from red to green
                    cmap = LinearSegmentedColormap.from_list('RedGreen', ['#ff9999', '#99ff99'])
                    
                    # Plot heatmap
                    sns.heatmap(heatmap_data, cmap=cmap, annot=True, fmt='.2f', 
                              linewidths=.5, ax=ax, cbar_kws={'label': 'Normalized Score'})
                    
                    ax.set_title('Federation Performance Analysis (Normalized Scores)')
                    st.pyplot(fig)
                
                # Display original values in a table (even if heatmap fails)
                st.subheader("Federation Statistics")
                display_stats = fed_stats[['fedNickname', 'fedRank', 'points', 
                                        'atpPoints', 'player_count']].sort_values('player_count', ascending=False)
                display_stats.columns = ['Federation', 'Avg Ranking', 'Avg Points', 
                                      'Avg ATP Points', 'Player Count']
                st.dataframe(display_stats.set_index('Federation'), use_container_width=True)
            else:
                st.info("Not enough federations with sufficient data for performance comparison")
        except Exception as e:
            st.error(f"Error in federation performance analysis: {e}")
    else:
        st.info("No data available with current filters")

# Tab 4: Age Analysis
with tabs[3]:
    st.header("Age and Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    # Birth Year Distribution (Modified from pie to bar chart for better readability)
    with col1:
        st.subheader("Player Distribution by Birth Year")
        if len(df_filtered) > 0:
            fig, ax = plt.subplots(figsize=(10, 8))
            birth_counts = df_filtered["birthYear"].value_counts().sort_index()
            birth_counts.plot(kind="bar", ax=ax, color="purple")
            ax.set_xlabel("Birth Year")
            ax.set_ylabel("Number of Players")
            ax.set_title("Players per Birth Year")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No data available with current filters")

    # Age vs Ranking Scatter Plot
    with col2:
        st.subheader("Age vs. Ranking Correlation")
        if len(df_filtered) > 0:
            try:
                # Filter out any rows with NaN or infinite values
                plot_data = df_filtered.copy()
                plot_data = plot_data[np.isfinite(plot_data['age']) & np.isfinite(plot_data['fedRank']) & np.isfinite(plot_data['points'])]
                
                if len(plot_data) > 1:  # Need at least 2 points for meaningful plot and trend line
                    fig, ax = plt.subplots(figsize=(10, 8))
                    scatter = ax.scatter(plot_data['age'], plot_data['fedRank'], 
                                      alpha=0.6, c=plot_data['points'], cmap='viridis')
                    
                    ax.set_xlabel("Age")
                    ax.set_ylabel("Ranking (ITN)")
                    ax.set_title(f"Correlation between Age and Ranking (n={len(plot_data)})")
                    
                    # Add trend line with proper error handling
                    try:
                        z = np.polyfit(plot_data['age'], plot_data['fedRank'], 1)
                        p = np.poly1d(z)
                        ax.plot(plot_data['age'], p(plot_data['age']), 
                              "r--", alpha=0.8, label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")
                        ax.legend()
                    except Exception as e:
                        st.warning(f"Could not calculate trend line: {e}")
                    
                    # Add colorbar
                    try:
                        cbar = plt.colorbar(scatter)
                        cbar.set_label('Points')
                    except Exception as e:
                        st.warning(f"Could not create colorbar: {e}")
                    
                    st.pyplot(fig)
                else:
                    st.info("Not enough valid data points for age correlation analysis")
            except Exception as e:
                st.error(f"Error creating age correlation plot: {e}")
        else:
            st.info("No data available with current filters")
    
    # Age Group Analysis
    st.subheader("Performance by Age Group")
    if len(df_filtered) > 0:
        try:
            # Create age groups
            df_filtered['age_group'] = pd.cut(
                df_filtered['age'], 
                bins=[0, 18, 25, 35, 45, 55, 100],
                labels=['Under 18', '18-25', '26-35', '36-45', '46-55', 'Over 55']
            )
            
            # Check if we have data in each age group
            if df_filtered['age_group'].nunique() > 1:
                # Calculate stats by age group
                age_stats = df_filtered.groupby('age_group', observed=True).agg({
                    'fedRank': 'mean',
                    'points': 'mean',
                    'atpPoints': 'mean',
                    'playerId': 'count'
                }).rename(columns={'playerId': 'count'})
                
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Create bar positions
                bar_positions = np.arange(len(age_stats.index))
                bar_width = 0.35
                
                # Create bars
                ax.bar(bar_positions - bar_width/2, age_stats['fedRank'], 
                       bar_width, label='Avg. Ranking', color='blue', alpha=0.7)
                
                # Create second axis for points
                ax2 = ax.twinx()
                ax2.bar(bar_positions + bar_width/2, age_stats['points'], 
                        bar_width, label='Avg. Points', color='green', alpha=0.7)
                
                # Add labels and title
                ax.set_xlabel('Age Group')
                ax.set_ylabel('Average Ranking (ITN)')
                ax2.set_ylabel('Average Points')
                
                # Add count annotations
                for i, count in enumerate(age_stats['count']):
                    ax.text(i, age_stats['fedRank'].iloc[i] + 0.2, 
                           f"n={count}", ha='center', fontsize=9)
                
                # Set x-ticks
                ax.set_xticks(bar_positions)
                ax.set_xticklabels(age_stats.index, rotation=45)
                
                # Add legend
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                
                ax.set_title('Performance Metrics by Age Group')
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
                st.pyplot(fig)
                
                # Show the data in a table
                st.subheader("Age Group Statistics")
                age_stats_display = age_stats.copy()
                age_stats_display.columns = ['Avg. Ranking', 'Avg. Points', 'Avg. ATP Points', 'Player Count']
                st.dataframe(age_stats_display, use_container_width=True)
            else:
                st.info("Not enough age variation in the filtered data for group analysis")
        except Exception as e:
            st.error(f"Error in age group analysis: {e}")
            st.info("Try adjusting your filters to include more diverse age ranges")
    else:
        st.info("No data available with current filters")

# Tab 5: Club Analysis
with tabs[4]:
    st.header("Club Analysis")
    
    # Top Clubs by Player Count
    st.subheader("Top Clubs by Player Count")
    if len(df_filtered) > 0:
        top_n = 15  # Show top 15 clubs
        club_counts = df_filtered['clubName'].value_counts().head(top_n)
        
        if not club_counts.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            club_counts.plot(kind='barh', ax=ax, color='darkblue')
            ax.set_xlabel('Number of Players')
            ax.set_ylabel('Club Name')
            ax.set_title(f'Top {top_n} Clubs by Player Count')
            st.pyplot(fig)
        else:
            st.info("No club data available with current filters")
    else:
        st.info("No data available with current filters")
    
    # Club Performance Analysis
    st.subheader("Club Performance Analysis")
    if len(df_filtered) > 0:
        # Get clubs with at least 3 players for meaningful statistics
        club_stats = df_filtered.groupby('clubName').filter(lambda x: len(x) >= 3)
        
        if not club_stats.empty:
            club_metrics = club_stats.groupby('clubName').agg({
                'fedRank': 'mean',
                'points': 'mean',
                'playerId': 'count'
            }).rename(columns={'playerId': 'player_count'})
            
            # Sort by player count and take top clubs
            top_performing_clubs = club_metrics.sort_values('player_count', ascending=False).head(10)
            
            # Create a scatter plot showing relationship between avg rank and points
            fig, ax = plt.subplots(figsize=(12, 8))
            
            scatter = ax.scatter(
                top_performing_clubs['fedRank'], 
                top_performing_clubs['points'],
                s=top_performing_clubs['player_count'] * 20,  # Size by player count
                alpha=0.7,
                c=range(len(top_performing_clubs)),  # Color gradient
                cmap='viridis'
            )
            
            # Add club labels
            for i, (club, row) in enumerate(top_performing_clubs.iterrows()):
                # Check if the coordinates are valid (finite) before adding text
                if (np.isfinite(row['fedRank']) and np.isfinite(row['points'])):
                    ax.text(row['fedRank'], row['points'], club, 
                           fontsize=9, ha='center', va='center',
                           bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
            
            ax.set_xlabel('Average Ranking (ITN)')
            ax.set_ylabel('Average Points')
            ax.set_title('Club Performance Analysis')
            
            # Add a legend for bubble size
            handles, labels = scatter.legend_elements(prop="sizes", alpha=0.5, 
                                                    num=4, func=lambda s: s/20)
            legend = ax.legend(handles, labels, loc="upper right", title="Player Count")
            
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)
            
            # Display the detailed club statistics
            st.subheader("Club Performance Statistics")
            club_stats_display = club_metrics.sort_values('player_count', ascending=False).head(20)
            club_stats_display.columns = ['Avg. Ranking', 'Avg. Points', 'Player Count']
            st.dataframe(club_stats_display, use_container_width=True)
        else:
            st.info("Not enough club data for performance analysis")
    else:
        st.info("No data available with current filters")

# Ranking Distribution Histogram
st.subheader("Distribution of Players by Ranking")
if len(df_filtered) > 0:
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Check if there's enough variation to make a histogram
    unique_ranks = df_filtered["fedRank"].nunique()
    
    if unique_ranks > 1:
        # Create bins for ranking ranges
        min_rank = math.floor(df_filtered["fedRank"].min())
        max_rank = math.ceil(df_filtered["fedRank"].max())
        
        # Ensure we have at least 5 bins for visual clarity
        if max_rank - min_rank < 2.5:
            # Not enough range for 5 bins at 0.5 increments, so we'll make smaller bins
            bins = np.linspace(min_rank, max_rank, 6)
        else:
            bins = np.arange(min_rank, max_rank + 0.5, 0.5)
            
        ax.hist(df_filtered["fedRank"], bins=bins, color="blue", alpha=0.7)
        ax.set_xlabel("Ranking (ITN)")
        ax.set_ylabel("Number of Players")
        ax.set_title(f"Distribution of Players by Ranking Range (n={len(df_filtered)})")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        # Not enough unique values for a meaningful histogram
        # Create a simple bar chart instead
        rank_counts = df_filtered["fedRank"].value_counts().sort_index()
        ax.bar(rank_counts.index.astype(str), rank_counts.values, color="blue", alpha=0.7)
        ax.set_xlabel("Ranking (ITN)")
        ax.set_ylabel("Number of Players")
        ax.set_title(f"Player Count by Ranking (n={len(df_filtered)})")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    st.pyplot(fig)
else:
    st.info("No data available with current filters")

# Correlation between ATP Points and Points
st.subheader("Correlation: ATP Points vs Regular Points")
if len(df_filtered) > 0:
    # Remove players with 0 ATP points for better visualization
    df_nonzero = df_filtered[df_filtered['atpPoints'] > 0].copy()
    if len(df_nonzero) > 5:  # Only show if we have enough data points
        # Check if there's enough variation in the data
        if df_nonzero['atpPoints'].nunique() > 1 and df_nonzero['points'].nunique() > 1:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Use a try-except block to handle potential errors in scatter plot
            try:
                scatter = ax.scatter(df_nonzero['atpPoints'], df_nonzero['points'], 
                                  alpha=0.6, c=df_nonzero['fedRank'], cmap='viridis')
                
                ax.set_xlabel("ATP Points")
                ax.set_ylabel("Regular Points")
                ax.set_title(f"Correlation between ATP Points and Regular Points (n={len(df_nonzero)})")
                
                # Add trend line - protect against polynomial fit errors
                try:
                    z = np.polyfit(df_nonzero['atpPoints'], df_nonzero['points'], 1)
                    p = np.poly1d(z)
                    ax.plot(df_nonzero['atpPoints'], p(df_nonzero['atpPoints']), 
                           "r--", alpha=0.8, label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")
                    ax.legend()
                except Exception as e:
                    st.warning(f"Could not calculate trend line: {e}")
                
                # Add a colorbar to show ranking
                try:
                    from mpl_toolkits.axes_grid1 import make_axes_locatable
                    divider = make_axes_locatable(ax)
                    cax = divider.append_axes("right", size="5%", pad=0.1)
                    cbar = plt.colorbar(scatter, cax=cax)
                    cbar.set_label('Ranking (ITN)')
                except Exception as e:
                    st.warning(f"Could not create colorbar: {e}")
                
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating scatter plot: {e}")
        else:
            st.info("Not enough variation in points data for correlation analysis")
    else:
        st.info("Not enough players with ATP points for correlation analysis")
else:
    st.info("No data available with current filters")

# Footer with data stats
st.markdown("---")
st.markdown(f"**Database Statistics:** {len(df)} total players from {df['fedNickname'].nunique()} federations and {df['clubName'].nunique()} clubs")
st.markdown(f"**Data Range:** Rankings from {df['fedRank'].min():.1f} to {df['fedRank'].max():.1f}, Birth years from {int(df['birthYear'].min())} to {int(df['birthYear'].max())}")

# Footer
st.markdown(
    "<p class='sub-title'>Dashboard built by <a href='https://fzeba.com'> Florian Zeba <a/> 🎾 </p>",
    unsafe_allow_html=True,
)
