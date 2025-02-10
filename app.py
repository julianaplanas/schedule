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


import pandas as pd

def process_excel(filepath):
    """Process an Excel file and extract shift data."""
    try:
        # Load the Excel file
        df = pd.read_excel(filepath, dtype=str)  # Ensure all values are read as strings
        print(f"Excel file loaded successfully with shape {df.shape}", flush=True)

        # Ensure column headers are properly handled
        df.fillna("", inplace=True)  # Replace NaN with empty strings

        shifts = []
        for index, row in df.iterrows():
            name = str(row.iloc[0]).strip()  # First column is expected to be the name
            days = [str(value).strip() for value in row.iloc[1:].tolist()]  # Convert all values to strings

            # Skip rows where the name is empty
            if not name:
                continue  

            shifts.append({'name': name, 'days': days})

        print(f"Extracted shifts from Excel: {shifts}", flush=True)
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
