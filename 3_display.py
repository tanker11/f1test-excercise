import requests
import time
import pandas as pd
from flask import Flask, jsonify
from bokeh.plotting import figure, show


class MonitorService:
    def __init__(self, slave_url):
        self.slave_url = slave_url
        self.status = "waiting for transform service"  # Initial status
        self.data = pd.DataFrame()



    def check_slave_status(self):
        """Check the slave service's /health endpoint."""
        try:
            response = requests.get(f"{self.slave_url}/health", timeout=5)
            response.raise_for_status()
            status = response.json().get("status", "unknown")
            return status == "ready"
        except requests.RequestException as e:
            print(f"Failed to reach transform service: {e}")
            return False

    def transfer_data(self):
        """Query the slave API and transfer the data."""
        api_endpoint = f"{self.slave_url}/data"  # Endpoint for fetching data
        try:
            response = requests.get(api_endpoint, timeout=10)
            response.raise_for_status()

            # Parse the data as a DataFrame
            data = pd.DataFrame(response.json())
            if data.empty:
                print("No data returned from slave API.")
                return
            self.status = "ready"  # Update status to ready
            self.data = data
            print(f"Transferred {len(data)} rows to the local database.")
        except Exception as e:
            self.status = "error"  # Update status to error
            print(f"Error during data transfer: {e}")

    def plot_data(self):
        # Create diagram area
        data = self.data
        p = figure(title="Position of drivers", x_axis_label="Events", y_axis_label="Position",
                   x_range=data["events"], y_range=(20, 0), height=400, width=800)  # y range is the possible positions

        # Add lines
        colors = ["blue", "red", "green"]
        for i, racer in enumerate(data.keys() - {"events"}):
            p.line(data["events"], data[racer], line_width=2, color=colors[i], legend_label=racer)

        # Add details
        p.legend.title = "Drivers"
        p.legend.location = "top_left"
        p.yaxis.ticker = list(range(1, len(data) + 1))

        show(p)

    def run(self):
        # Monitor the slave service and transfer data when ready.
        success = False
        print("Starting up")
        while not success:
            time.sleep(5)
            print("Checking loading service status...")
            if self.check_slave_status():
                print("Loading service is ready. Transferring data...")
                self.transfer_data()
                success = True
                #self.plot_data()
            else:
                print("Loading is not ready. Waiting...")


# Flask app for the /health endpoint
app = Flask(__name__)
monitor_service = MonitorService(slave_url="http://localhost:5001")  # Update URL as needed


@app.route('/health', methods=['GET'])
def health():
    """Return the current status of the Monitor Service."""
    return jsonify({"status": monitor_service.status})


if __name__ == "__main__":
    # Start monitoring and run the Flask API
    monitor_service.run()
    app.run(host="0.0.0.0", port=5002)
