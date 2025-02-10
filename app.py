from flask import Flask, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received a file upload request.")

    if 'file' not in request.files:
        print("Error: No file part in the request.")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        print("Error: No file selected for upload.")
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        print(f"Error: Unsupported file type: {file.filename}")
        return jsonify({'error': f'Invalid file type. Allowed types: {app.config["ALLOWED_EXTENSIONS"]}'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Save the file
        file.save(filepath)
        print(f"File saved at {filepath}")

        # Process the file based on its type
        if filename.endswith('.xlsx'):
            print("Processing Excel file...")
            data = process_excel(filepath)
        elif filename.endswith('.pdf'):
            print("Processing PDF file...")
            data = process_pdf(filepath)
        else:
            print("Error: Unsupported file type.")
            return jsonify({'error': 'Unsupported file type'}), 400

        print("File processed successfully.")
        return jsonify(data), 200
    except Exception as e:
        print(f"Error during file processing: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Ensure cleanup of uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up file: {filepath}")
        else:
            print(f"File not found for cleanup: {filepath}")

def process_excel(filepath):
    """Process an Excel file, clean it, and extract shift data."""
    try:
        # Load the Excel file without guessing column types
        df = pd.read_excel(filepath, dtype=str, header=None)  # Read everything as strings

        # Find the row where actual employee data starts (assuming it starts below 'PLANTILLA')
        start_row = None
        for i, row in df.iterrows():
            if row.str.contains("PLANTILLA", na=False).any():
                start_row = i + 2  # Skip the plantilla row and one extra row if necessary
                break
        
        if start_row is None:
            raise ValueError("Could not find the correct starting row for shift data.")

        # Select only relevant data (from employee names downward)
        df = df.iloc[start_row:].reset_index(drop=True)

        # Rename the first column as 'Name' and the rest as 'Days'
        df.columns = ['Name'] + [f'Day {i}' for i in range(1, df.shape[1])]

        # Drop any rows where 'Name' is missing or empty
        df.dropna(subset=['Name'], inplace=True)

        # Ensure all days are strings to avoid NaN issues
        df.fillna("", inplace=True)

        # Convert to JSON structure
        shifts = []
        for _, row in df.iterrows():
            name = row['Name'].strip()
            days = row.iloc[1:].tolist()  # All other columns are shifts

            # Skip empty names (just in case)
            if not name:
                continue

            shifts.append({'name': name, 'days': days})

        print(f"Extracted shifts from Excel: {shifts[:5]}", flush=True)  # Print first 5 rows for debugging
        return shifts

    except Exception as e:
        print(f"Error while processing Excel file: {e}", flush=True)
        raise


def process_pdf(filepath):
    """Process a PDF file and extract shift data."""
    try:
        # Read the PDF file
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        print(f"Extracted text from PDF: {text[:500]}", flush=True)  # Log the first 500 characters

        # Parse the text into shifts (example logic)
        # Assuming the PDF contains lines like: "Name: John, Shifts: morning, off, late"
        lines = text.splitlines()
        shifts = []
        for line in lines:
            if "Name:" in line and "Shifts:" in line:
                parts = line.split(", Shifts:")
                name = parts[0].replace("Name:", "").strip()
                days = parts[1].strip().split(", ")
                shifts.append({'name': name, 'days': days})

        print(f"Extracted shifts from PDF: {shifts}", flush=True)
        return shifts
    except Exception as e:
        print(f"Error while processing PDF file: {e}", flush=True)
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
