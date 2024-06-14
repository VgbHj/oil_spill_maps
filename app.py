import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from ultralytics import YOLO

# Initialize the Flask app
app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

        # Path to the result image
        result_image_name = file.filename.rsplit('.', 1)[0] + '_pred.jpg'
        result_image_path = os.path.join(app.config['UPLOAD_FOLDER'], result_image_name)

        # Rename the result image to ensure it can be accessed
        saved_image_path = filename.rsplit('.', 1)[0] + '_0.jpg'
        os.rename(saved_image_path, result_image_path)

        return redirect(url_for('show_result', filename=result_image_name))

# Display the result image
@app.route('/result/<filename>')
def show_result(filename):
    print(filename)
    return render_template('result.html', filename=filename)

# Serve the uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
