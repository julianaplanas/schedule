from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global variables
shifts = []
day_numbers = []

def process_excel(filepath):
    """Process an Excel file, clean it, and extract shift data."""
    try:
        # Load the Excel file
        df = pd.read_excel(filepath, dtype=str, header=None)
        df.fillna("", inplace=True)

        # Extract the month
        month = df.iloc[0, 1].strip()

        # Extract day numbers from the "DÍA" row
        day_row = None
        for i, row in df.iterrows():
            if row.str.contains("DÍA", na=False).any():
                day_row = i + 1
                break

        if day_row is None:
            raise ValueError("Day numbers row not found in the Excel file.")

        # Get the actual day numbers
        day_numbers = df.iloc[day_row, 1:].tolist()

        # Find the start row of the actual schedule (skip metadata like PLANTILLA)
        start_row = None
        for i, row in df.iterrows():
            if row.str.contains("PLANTILLA", na=False).any():
                start_row = i + 2
                break

        if start_row is None:
            raise ValueError("Start row for schedule not found in the Excel file.")

        # Process schedule data
        df = df.iloc[start_row:].reset_index(drop=True)
        df.columns = ["Name"] + [f"Day {i}" for i in range(1, df.shape[1])]

        # Convert to JSON structure
        shifts = []
        for _, row in df.iterrows():
            name = row["Name"].strip()
            days = row.iloc[1:].tolist()

            if name:  # Skip empty names
                shifts.append({"name": name, "days": days})

        return month, day_numbers, shifts
    except Exception as e:
        print(f"Error processing Excel: {e}")
        return "", [], []

# Preload the Excel file during initialization
file_path = "uploads/schedule-febrero.xlsx"  # Path to the preloaded Excel file
month, day_numbers, shifts = process_excel(file_path)
print(f"Shifts preloaded: {shifts[:5]}")  # Log first 5 entries for debugging
print(f"Day Numbers preloaded: {day_numbers}")

@app.route("/shifts", methods=["GET"])
def get_shifts():
    """Return the preloaded shift data."""
    return jsonify({"month": month, "dayNumbers": day_numbers, "shifts": shifts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
