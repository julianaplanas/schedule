from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global variables
shifts = []
day_numbers = []

def process_excel(filepath):
    try:
        # Read the Excel file
        df = pd.read_excel(filepath, dtype=str, header=None)
        df.fillna("", inplace=True)

        # Extract the month from the "MES" row
        month_row = df.iloc[0].values.tolist()
        month = month_row[1] if len(month_row) > 1 else ""

        # Extract day numbers from the "DÍA" row
        day_numbers_row = df.iloc[1].values.tolist()
        day_numbers = [x for x in day_numbers_row if x.isdigit()]  # Filter only numeric values

        # Extract shifts for each name
        shifts = []
        for _, row in df.iloc[3:].iterrows():  # Adjust starting row based on your file
            name = row[0].strip()  # First column is the name
            days = row[1:].tolist()  # Rest of the columns are shifts
            if name:  # Skip empty names
                shifts.append({"name": name, "days": days})

        return {
            "month": month,
            "dayNumbers": day_numbers,
            "shifts": shifts
        }
    except Exception as e:
        print(f"Error processing Excel: {e}")
        return {
            "month": "",
            "dayNumbers": [],
            "shifts": []
        }

# Preload the Excel file during initialization
file_path = "uploads/schedule-febrero.xlsx"  # Update with your file path
data = process_excel(file_path)

if data["month"] and data["shifts"]:  # Check if data was successfully extracted
    shifts = data
else:
    shifts = {"month": "No data", "dayNumbers": [], "shifts": []}

print(f"Shifts preloaded: {shifts}")

@app.route("/shifts", methods=["GET"])
def get_shifts():
    """Return the preloaded shift data."""
    return jsonify(shifts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
