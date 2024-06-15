import os
import shutil
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from ultralytics import YOLO

# Initialize the Flask app
app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static/runs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the YOLO model
model = YOLO("best.pt")

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
        file.save(filename)

        # Perform inference
        results = model.predict(source=filename, save=True)

        # Extract the directory where results are saved
        save_dir = results[0].save_dir
        print(f"Results saved to: {save_dir}")

        # Move the results directory to the static folder
        dest_dir = os.path.join(STATIC_FOLDER, os.path.basename(save_dir))
        shutil.move(save_dir, dest_dir)

        # Assuming the result image has a '_0' suffix as saved by YOLO
        result_image_name = file.filename.rsplit('.', 1)[0] + '_0.jpg'
        result_image_path = os.path.join(dest_dir, result_image_name)

        print(result_image_path)

        # Verify the result image exists
        if os.path.exists(dest_dir):
            return redirect(url_for('show_result', full_filename=result_image_path))
        else:
            return 'Error: Result image not found.'

# Display the result image
@app.route('/result')
def show_result():
    full_filename = request.args.get('full_filename')
    return render_template('result.html', full_filename=full_filename)

# Serve the files from their respective directories
@app.route('/files/<path:filename>')
def result_file(filename):
    directory = os.path.dirname(filename)
    file = os.path.basename(filename)
    return send_from_directory(directory, file)

# Map route
@app.route('/map')
def map_page():
    return render_template('map.html')

# Serve the uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
