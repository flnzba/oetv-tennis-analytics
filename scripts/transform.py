import sqlite3
from load import main

# from pydantic import BaseModel as basem  # type: ignore


# # Load data from JSON file
# with open("../test/oetv-rankings.json", "r") as file:
#     data = json.load(file)

data = main()

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("scripts/data.db")
c = conn.cursor()

# Drop table if it exists
c.execute("DROP TABLE IF EXISTS players")

# Create table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS players (
        playerId TEXT,
        licenceNr TEXT,
        natRank INTEGER,
        natRankFed INTEGER,
        firstname TEXT,
        lastname TEXT,
        nationality TEXT,
        clubName TEXT,
        clubNr TEXT,
        fedNickname TEXT,
        fedRank REAL,
        birthYear INTEGER,
        atpPoints INTEGER,
        points INTEGER
    )
"""
)

# Insert data into the table
for player in data:
    c.execute(
        """
        INSERT INTO players (playerId, licenceNr, natRank, natRankFed, firstname, lastname, nationality, clubName, clubNr, fedNickname, fedRank, birthYear, atpPoints, points) VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            player["playerId"],
            player["licenceNr"],
            player["natRank"],
            player["natRankFed"],
            player["firstname"],
            player["lastname"],
            player["nationality"],
            player["clubName"],
            player["clubNr"],
            player["fedNickname"],
            player["fedRank"],
            player["birthYear"],
            player["atpPoints"],
            player["points"],
        ),
    )

# Commit changes and close connection
conn.commit()
conn.close()
