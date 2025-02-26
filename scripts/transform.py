import sqlite3
import os
import sys
from datetime import datetime

# We'll import specific functions from load instead of main() directly
from load import get_data_batches, setup_api_client

# Determine the correct path for the database
# Get the base directory from environment or use a default
# This allows configuration in Docker environments
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(DATA_DIR, "data.db")

print(f"Using database at: {db_path}")

# Make sure parent directories exist
os.makedirs(os.path.dirname(db_path), exist_ok=True)

def init_database():
    """Initialize the database with the players table"""
    conn = sqlite3.connect(db_path)
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
    
    conn.commit()
    
    return conn, c

def save_batch(batch, conn, cursor):
    """Save a batch of player data to the database"""
    try:
        # Insert data into the table
        for player in batch:
            cursor.execute(
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
        
        # Commit this batch
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving batch to database: {e}")
        # Rollback on error
        conn.rollback()
        return False

def process_data_continuous():
    """Process data continuously as it's fetched, saving in batches"""
    try:
        print(f"Starting data processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize database
        conn, cursor = init_database()
        
        # Set up the API client
        client = setup_api_client()
        
        # Get batches and process them
        total_processed = 0
        for batch_number, batch in enumerate(get_data_batches(client)):
            # Save this batch to the database
            if save_batch(batch, conn, cursor):
                total_processed += len(batch)
                print(f"Batch {batch_number+1} saved. Total records processed: {total_processed}")
            else:
                print(f"Failed to save batch {batch_number+1}")
        
        # Get total record count
        cursor.execute("SELECT COUNT(*) FROM players")
        total_records = cursor.fetchone()[0]
        print(f"Total records in database: {total_records}")
        
        # Close connection
        conn.close()
        
        print(f"Data processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"Fatal error in data processing: {e}")
        if 'conn' in locals():
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    process_data_continuous()
