import sqlite3
import time
import requests
import pandas as pd

class MonitorService:
    def __init__(self, slave_url, local_db_name="monitor_data.db"):
        self.slave_url = slave_url
        self.local_db_name = local_db_name
        self.init_db()

    def init_db(self):
        """Initialize the local SQLite database."""
        with sqlite3.connect(self.local_db_name) as conn:
            cursor = conn.cursor()
            # Create table for transferred data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_data (
                    location TEXT,
                    session_name TEXT,
                    driver_number INTEGER
                )
            ''')
            conn.commit()

    def check_slave_status(self):
        """Check the slave service's /health endpoint."""
        try:
            response = requests.get(f"{self.slave_url}/health", timeout=5)
            response.raise_for_status()
            status = response.json().get("status", "unknown")
            return status == "ready"
        except requests.RequestException as e:
            print(f"Failed to reach loading service: {e}")
            return False

    def transfer_data(self):
        """Query the slave database and transfer the data."""
        slave_db_path = "/app/slave_data.db"  # Path to the slave DB inside its container
        query = '''
            SELECT m.location, s.name AS session_name, p.driver_number
            FROM meetings m
            JOIN sessions s ON s.meeting_id = m.id
            JOIN positions p ON p.session_id = s.id
        '''
        try:
            # Read data from slave SQLite database
            with sqlite3.connect(slave_db_path) as slave_conn:
                data = pd.read_sql_query(query, slave_conn)

            # Write data to local SQLite database
            with sqlite3.connect(self.local_db_name) as local_conn:
                data.to_sql('session_data', local_conn, if_exists='append', index=False)

            print(f"Transferred {len(data)} rows to the local database.")
        except Exception as e:
            print(f"Error during data transfer: {e}")

    def run(self):
        """Monitor the slave service and transfer data when ready."""
        while True:
            print("Checking loading service status...")
            if self.check_slave_status():
                print("Loading service is ready. Transferring data...")
                self.transfer_data()
            else:
                print("Loading is not ready. Waiting...")
            time.sleep(15)


if __name__ == "__main__":
    monitor = MonitorService(slave_url="http://sqlite_load:5000")
    monitor.run()
