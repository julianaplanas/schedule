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
        # Load the Excel file
        df = pd.read_excel(filepath, dtype=str, header=None)
        df.fillna("", inplace=True)

        # Extract month
        month_row = df.iloc[0]  # Adjust based on actual file structure
        month = month_row[df.columns[1]]  # Assuming "FEBRERO" is in the second column

        # Extract day numbers
        day_numbers_row = df.iloc[1]  # Adjust based on actual file structure
        day_numbers = day_numbers_row[1:].tolist()  # Skip the first column if it's not part of day numbers

        # Extract shifts
        start_row = None
        for i, row in df.iterrows():
            if row.str.contains("PLANTILLA", na=False).any():
                start_row = i + 2
                break

        if start_row is None:
            raise ValueError("Start row for schedule not found in the Excel file.")

        schedule_data = df.iloc[start_row:].reset_index(drop=True)
        schedule_data.columns = ["Name"] + [f"Day {i}" for i in range(1, schedule_data.shape[1])]

        shifts = []
        for _, row in schedule_data.iterrows():
            name = row["Name"].strip()
            days = row.iloc[1:].tolist()

            if name:
                shifts.append({"name": name, "days": days})

        return {"month": month, "dayNumbers": day_numbers, "shifts": shifts}

    except Exception as e:
        print(f"Error processing Excel: {e}")
        return {"month": "", "dayNumbers": [], "shifts": []}

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
