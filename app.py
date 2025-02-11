from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global variables to store shifts and month name
shifts = []
month_name = ""

def process_excel(filepath):
    """Process an Excel file, clean it, and extract shift data."""
    try:
        # Load the Excel file
        df = pd.read_excel(filepath, dtype=str, header=None)
        df.fillna("", inplace=True)

        # Extract the month name (assume it's in the second column of the first row)
        global month_name
        month_name = df.iloc[0, 1].strip() if len(df.columns) > 1 else "Unknown Month"

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
            # Extract names
            name = row["Name"].strip()
            days = row.iloc[1:].tolist()

            # Handle multiple names in a single cell (split by spaces or commas)
            for individual_name in name.split():
                if individual_name:  # Skip empty names
                    shifts.append({"name": individual_name, "days": days})

        return shifts
    except Exception as e:
        print(f"Error processing Excel: {e}")
        return []

# Preload the Excel file during initialization
file_path = "uploads/schedule-febrero.xlsx"  # Path to the preloaded Excel file
shifts = process_excel(file_path)
print(f"Month: {month_name}")
print(f"Shifts preloaded: {shifts[:5]}")  # Log first 5 entries for debugging

@app.route("/shifts", methods=["GET"])
def get_shifts():
    """Return the preloaded shift data along with the month name."""
    return jsonify({"month": month_name, "shifts": shifts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
