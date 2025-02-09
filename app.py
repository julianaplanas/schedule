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
    try:
        print("File upload request received")
        # Existing code...
        print(f"Processing file: {filename}")
        
        if filename.endswith('.xlsx'):
            data = process_excel(filepath)
        elif filename.endswith('.pdf'):
            data = process_pdf(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        print("File processed successfully")
        return jsonify(data), 200
    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up file: {filepath}")

def process_excel(filepath):
    """Process an Excel file and extract data."""
    df = pd.read_excel(filepath)
    shifts = []
    for index, row in df.iterrows():
        name = row.get('Name', 'Unknown')
        days = row[1:].tolist()  # Assuming shifts start from the second column
        shifts.append({'name': name, 'days': days})
    return shifts


def process_pdf(filepath):
    """Process a PDF file and extract text."""
    reader = PdfReader(filepath)
    text = ''
    for page in reader.pages:
        text += page.extract_text()

    # Parse the text into structured data (example logic)
    shifts = [{'name': 'Example', 'days': ['morning', 'off', 'late']}]
    return shifts


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
