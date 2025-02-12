from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global variable to store shifts
shifts = []
days = []  # New variable to store the days (row "DIA")

def process_excel(filepath):
    """Process an Excel file, clean it, and extract shift data."""
    try:
        # Load the Excel file
        df = pd.read_excel(filepath, dtype=str, header=None)
        df.fillna("", inplace=True)

        # Extract the month
        month = df.iloc[0, 1].strip()  # Assuming "MES" is in the first row, and the month is in the second column
        print(f"Extracted Month: {month}")

        # Extract day numbers
        dayNumbers_row = df[df.iloc[:, 0].str.contains("DÍA", na=False)].index[0] + 1
        dayNumbers = df.iloc[dayNumbers_row, 1:].tolist()
        print(f"Extracted Day Numbers: {dayNumbers}")

        # Find the start row of the actual schedule
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
        
        # Extract shifts
        shifts = []
        for _, row in df.iterrows():
            name = row["Name"].strip()
            days = row.iloc[1:].tolist()

            if name:  # Skip empty names
                shifts.append({"name": name, "days": days})

        print(f"Extracted Shifts: {shifts[:5]}")  # Log first 5 shifts
        return {"month": month, "dayNumbers": dayNumbers, "shifts": shifts}

    except Exception as e:
        print(f"Error processing Excel: {e}")
        return {"month": "", "dayNumbers": [], "shifts": []}

# Preload the Excel file during initialization
file_path = "uploads/schedule-febrero.xlsx"  # Path to the preloaded Excel file
data = process_excel(file_path)
month = data.get("month", "")
dayNumbers = data.get("dayNumbers", [])
shifts = data.get("shifts", [])

# Add debugging to check preloaded data
print(f"Month: {month}, Day Numbers: {dayNumbers}, Shifts: {shifts[:5]}")

# Ensure shifts and dayNumbers are not empty
if not shifts or not dayNumbers:
    print("Error: No valid shift data received during preloading.")
else:
    print("Preloaded shifts successfully.")

@app.route("/shifts", methods=["GET"])
def get_shifts():
    """Return the preloaded shift data."""
    return jsonify({"month": month, "dayNumbers": dayNumbers, "shifts": shifts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
