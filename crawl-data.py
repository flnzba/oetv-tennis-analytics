import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from matplotlib import pyplot as plt

# Pfad zum Chromedriver (angepasst an dein System)
chromedriver_path = '/Users/florzeba/Library/Mobile Documents/com~apple~CloudDocs/Downloads/chromedriver-mac-x64/chromedriver'
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# Öffne die Webseite
driver.get('https://www.oetv.at/rangliste/oetv')

# Warte, dass die Seite lädt
time.sleep(5)

# Klicke auf "Zeige Mehr" bis alle Einträge geladen sind
while True:
    try:
        more_button = driver.find_element(By.LINK_TEXT, 'Zeige Mehr')
        more_button.click()
        time.sleep(2)  # Kurze Pause, um das Laden der Daten zu ermöglichen
    except Exception as e:
        print("Alle Daten geladen oder ein Fehler ist aufgetreten:", e)
        break

# Extrahiere Daten
players = driver.find_elements(By.CSS_SELECTOR, 'div.player-info')
data = []
for player in players:
    name = player.find_element(By.CSS_SELECTOR, 'h3').text
    ranking = player.find_element(By.CSS_SELECTOR, 'span.rank').text
    data.append((name, ranking))

driver.quit()

# Speichere Daten in SQLite
conn = sqlite3.connect('players.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS players (name TEXT, ranking TEXT)')
c.executemany('INSERT INTO players (name, ranking) VALUES (?, ?)', data)
conn.commit()
conn.close()

# Lese Daten und erstelle ein Plot
conn = sqlite3.connect('players.db')
c = conn.cursor()
c.execute('SELECT ranking, COUNT(*) FROM players GROUP BY ranking')
results = c.fetchall()
conn.close()

rankings = [row[0] for row in results]
counts = [row[1] for row in results]

plt.figure(figsize=(10, 8))
plt.bar(rankings, counts, color='blue')
plt.xlabel('Ranking')
plt.ylabel('Anzahl der Spieler')
plt.title('Anzahl der Spieler pro Ranking')
plt.show()
