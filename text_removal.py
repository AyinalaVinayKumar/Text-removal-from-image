from flask import Flask, render_template, request, send_from_directory
import os
import numpy as np
import cv2
import easyocr
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

reader = easyocr.Reader(['en'], gpu=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file part"
        file = request.files['image']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            image = cv2.imread(filepath)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            results = reader.readtext(image)

            text_mask = np.zeros_like(gray_image)

            for (bbox, text, prob) in results:
                points = np.array(bbox, dtype=np.int32)
                cv2.fillPoly(text_mask, [points], 255)

            inpainted_image = cv2.inpaint(image, text_mask, 3, cv2.INPAINT_TELEA)

            output_path = os.path.join(OUTPUT_FOLDER, filename)
            cv2.imwrite(output_path, inpainted_image)

            return render_template("index.html", filename=filename)

    return render_template("index.html", filename=None)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
