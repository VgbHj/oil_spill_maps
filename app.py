import os
import shutil
import sqlite3
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, g
from ultralytics import YOLO

# Initialize the Flask app
app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
RUNS_FOLDER = 'runs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RUNS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RUNS_FOLDER'] = RUNS_FOLDER

# Load the YOLO model
model = YOLO("best.pt")

DATABASE = 'oil_stains.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Upload and inference route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(filename + "!!!!")
        file.save(filename)

        # Perform inference
        results = model.predict(source=filename, save=True)

        # Extract the directory where results are saved
        save_dir = results[0].save_dir
        print(f"Results saved to: {save_dir}")

        # Assuming the result image has a '_0' suffix as saved by YOLO
        result_image_name = file.filename
        result_image_path = os.path.join(save_dir, result_image_name)

        print(result_image_path)

        # Verify the result image exists
        if os.path.exists(save_dir):
            return redirect(url_for('show_result', result_image=result_image_path, uploaded_image=filename))
        else:
            return 'Error: Result image not found.'

# Display the result image
@app.route('/result')
def show_result():
    result_image = request.args.get('result_image')
    uploaded_image = request.args.get('uploaded_image')
    return render_template('result.html', result_image=result_image, uploaded_image=uploaded_image)

# Serve the uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve the result files
@app.route('/results/<path:filename>')
def result_file(filename):
    return send_from_directory('', filename)

# Map route
@app.route('/map')
def map_page():
    db = get_db()
    cur = db.execute('SELECT x, y FROM oil_stains')
    coordinates = cur.fetchall()
    return render_template('map.html', coordinates=coordinates)

# Add coordinates manually
@app.route('/add_coordinates', methods=['POST'])
def add_coordinates():
    x = request.form['x']
    y = request.form['y']
    db = get_db()
    db.execute('INSERT INTO oil_stains (filename, x, y) VALUES (?, ?, ?)', ('manual', x, y))
    db.commit()
    return redirect(url_for('map_page'))

if __name__ == '__main__':
    app.run(debug=True)
