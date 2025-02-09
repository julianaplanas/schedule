from flask import Flask, request, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed types: {app.config["ALLOWED_EXTENSIONS"]}'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        if filename.endswith('.xlsx'):
            data = process_excel(filepath)
        elif filename.endswith('.pdf'):
            data = process_pdf(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(filepath)  # Clean up the uploaded file

def process_excel(filepath):
    # Read Excel file
    df = pd.read_excel(filepath)
    # Example processing: convert to JSON-like structure
    shifts = []
    for index, row in df.iterrows():
        name = row.get('Name', 'Unknown')
        days = row[1:].tolist()  # Assuming shifts start from the second column
        shifts.append({'name': name, 'days': days})
    return shifts

def process_pdf(filepath):
    # Read PDF file
    reader = PdfReader(filepath)
    text = ''
    for page in reader.pages:
        text += page.extract_text()

    # Example: Parse text into structured data (implementation varies)
    # Assume names and shifts are formatted in a consistent pattern
    shifts = [{'name': 'Example', 'days': ['morning', 'off', 'late']}]
    return shifts

if __name__ == '__main__':
    app.run(debug=True)
