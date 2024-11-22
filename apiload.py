import sqlite3
import pandas as pd
import json
import time
from urllib.request import urlopen
from flask import Flask, jsonify
import threading

class LoadService:
    def __init__(self, db_name="f1_data.db"):
        self.db_name = db_name
        self.status = "init"  # Inicializált állapot
        self.init_db()

    def init_db(self):
        #SQLite adatbázis inicializálása
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # táblák: meetings, sessions, positions, weather
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meetings (
                        id INTEGER PRIMARY KEY,
                        meeting_key TEXT,
                        meeting_name TEXT,
                        date TEXT,
                        location TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY,
                        session_key TEXT,
                        session_name TEXT,
                        meeting_key TEXT,
                        date TEXT,
                        FOREIGN KEY (meeting_key) REFERENCES meetings(meeting_key)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS positions (
                        id INTEGER PRIMARY KEY,
                        session_key TEXT,
                        driver TEXT,
                        position INTEGER,
                        time TEXT,
                        FOREIGN KEY (session_key) REFERENCES sessions(session_key)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weather (
                        id INTEGER PRIMARY KEY,
                        meeting_key TEXT,
                        temperature TEXT,
                        condition TEXT,
                        date TEXT,
                        FOREIGN KEY (meeting_key) REFERENCES meetings(meeting_key)
                    )
                ''')
                conn.commit()
            print("Database initialized.")
        except Exception as e:
            self.status = "error"
            print(f"Error initializing database: {e}")
            raise

    def fetch_and_store(self):
        # Adatlekérés és eltárolás
        self.status = "loading"  # Állapot beállítása adatbetöltés közben
        try:
            # Meeting (hétvége) lista
            print('Accessing meeting list...')
            response = urlopen('https://api.openf1.org/v1/meetings?year=2023')
            mtg_data = json.loads(response.read().decode('utf-8'))
            mtg_df = pd.DataFrame(mtg_data)

            # Hétvége eltárolása adatbázisban
            with sqlite3.connect(self.db_name) as conn:
                mtg_df.to_sql('meetings', conn, if_exists='replace', index=False)
            print(f'{len(mtg_df)} meetings stored.')

            time.sleep(1) #várakozás, hogy ne legyen túl sűrű a hozzáférés

            # Pandas dataframe-ke a session és position adatoknak
            session_df = pd.DataFrame()
            position_df = pd.DataFrame()

            # Session és position adatok lekérése a meeting_key alapján
            for meeting in mtg_data:
                print(f"Fetching {meeting['meeting_name']} session data...")
                response = urlopen(f"https://api.openf1.org/v1/sessions?meeting_key={meeting['meeting_key']}")
                session_data = json.loads(response.read().decode('utf-8'))
                session_actual = pd.DataFrame(session_data)
                session_df = pd.concat([session_df, session_actual], ignore_index=True)

                for session in session_data:
                    print(f"    {session['session_key']} position details...")
                    position_details = urlopen(f"https://api.openf1.org/v1/position?session_key={session['session_key']}")
                    position_data = json.loads(position_details.read().decode('utf-8'))
                    position_actual = pd.DataFrame(position_data)
                    position_df = pd.concat([position_df, position_actual], ignore_index=True)
                    time.sleep(0.2)

            # Session és position letárolása adatbázisban
            with sqlite3.connect(self.db_name) as conn:
                session_df.to_sql('sessions', conn, if_exists='replace', index=False)
                position_df.to_sql('positions', conn, if_exists='replace', index=False)

            time.sleep(1)

            # Időjárásadatok lekérése
            weather_df = pd.DataFrame()
            for meeting in mtg_data:
                print(f"Fetching {meeting['meeting_name']} weather data...")
                response = urlopen(f"https://api.openf1.org/v1/weather?meeting_key={meeting['meeting_key']}")
                weather_data = json.loads(response.read().decode('utf-8'))
                weather_actual = pd.DataFrame(weather_data)
                weather_df = pd.concat([weather_df, weather_actual], ignore_index=True)

            # Időjárásadatok letárolása adatbázisban
            with sqlite3.connect(self.db_name) as conn:
                weather_df.to_sql('weather', conn, if_exists='replace', index=False)

            print("All data successfully fetched and stored.")
            self.status = "ready"  # Állapot beállítása készenléti módba, ha kész 'ready'

        except Exception as e:
            self.status = "error"  # Hiba esetén állapot frissítése 'error'-ra
            print(f"Error fetching or storing data: {e}")
            raise


app = Flask(__name__)
service = LoadService()

@app.route('/health', methods=['GET'])
def health_check():
    #API végpont az aktuális státusz lekérdezésére
    return jsonify({"status": service.status})

def background_task():
    #Háttérfolyamat az adatbetöltéshez
    try:
        service.fetch_and_store()
    except Exception as e:
        print(f"Background task error: {e}")

if __name__ == "__main__":
    # Háttérszál indítása az adatbetöltéshez
    threading.Thread(target=background_task, daemon=True).start()
    # Flask indítása
    app.run(host="0.0.0.0", port=5000)
