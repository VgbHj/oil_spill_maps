import os
import shutil
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
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
        result_image_name = file.filename.rsplit('.', 1)[0] + '.jpg'
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
@app.route('/<path:filename>')
def result_file(filename):
    return send_from_directory('', filename)

# Map route
@app.route('/map')
def map_page():
    return render_template('map.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
