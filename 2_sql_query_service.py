import sqlite3
import requests
import pandas as pd
from flask import Flask, jsonify

class MonitorService:
    def __init__(self, slave_url, local_db_name="monitor_data.db"):
        self.slave_url = slave_url
        self.local_db_name = local_db_name
        self.status = "waiting for loading service"  # Initial status
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
        slave_db_path = "/app/f1_data.db"  # Path to the slave DB inside its container
        query = '''
            SELECT m.location, s.session_name, p.driver_number
            FROM meetings m
            JOIN sessions s
            ON s.meeting_key=m.meeting_key
            JOIN positions p
            ON p.session_key=s.session_key
        '''
        try:
            # Read data from slave SQLite database
            with sqlite3.connect(slave_db_path) as slave_conn:
                data = pd.read_sql_query(query, slave_conn)

            # Write data to local SQLite database
            with sqlite3.connect(self.local_db_name) as local_conn:
                data.to_sql('session_data', local_conn, if_exists='append', index=False)

            self.status = "ready"  # Update status to ready
            print(f"Transferred {len(data)} rows to the local database.")
        except Exception as e:
            self.status = "error"  # Update status to error
            print(f"Error during data transfer: {e}")

    def run(self):
        """Monitor the slave service and transfer data when ready."""
        print("Checking loading service status...")
        if self.check_slave_status():
            print("Loading service is ready. Transferring data...")
            self.transfer_data()
        else:
            print("Loading is not ready.")
            self.status = "waiting for loading service"


# Flask app for the /health endpoint
app = Flask(__name__)
monitor_service = MonitorService(slave_url="http://localhost:5000")  # Update URL as needed


@app.route('/health', methods=['GET'])
def health():
    """Return the current status of the Monitor Service."""
    return jsonify({"status": monitor_service.status})


if __name__ == "__main__":
    # Start monitoring and run the Flask API
    monitor_service.run()
    app.run(host="0.0.0.0", port=5001)
