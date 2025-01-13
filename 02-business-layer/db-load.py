import sqlite3
from pydantic import BaseModel as basem  # type: ignore


class Player(basem):
    name: str
    rank: str


# def save_to_db(data):
#     conn = sqlite3.connect("data.db")
#     c = conn.cursor()
#     c.execute("""CREATE TABLE IF NOT EXISTS players (name TEXT, rank TEXT)""")
#     for item in data:
#         c.execute(
#             """INSERT INTO players (name, rank) VALUES (?, ?)""",
#             (item["name"], item["rank"]),
#         )
#     conn.commit()
#     conn.close()
