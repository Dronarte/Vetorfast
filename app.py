from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import numpy as np
import svgwrite
import io
from PIL import Image
from skimage import measure
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/vectorize', methods=['POST'])
def vectorize():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    file = request.files['image']
    image = Image.open(file).convert("L")
    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    data = np.array(image, dtype=np.uint8)
    data = np.where(data == 0, 1, 0)

    contours = measure.find_contours(data, 0.8)
    height, width = data.shape
    dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"))

    for contour in contours:
        points = [(x, y) for y, x in contour]
        dwg.add(dwg.polyline(points, stroke='black', fill='none'))

    svg_data = io.BytesIO()
    dwg.write(svg_data)
    svg_data.seek(0)

    return send_file(svg_data, mimetype='image/svg+xml', as_attachment=True, download_name='vetorizado.svg')
