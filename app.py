from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import numpy as np
from PIL import Image
from skimage import measure
import svgwrite

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Vetorfast Online!"

@app.route("/vectorize", methods=["POST"])
def vectorize():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    image_file = request.files['image']
    image = Image.open(image_file).convert("L")  # escala de cinza
    image = np.array(image)
    image = np.where(image < 128, 1, 0)  # binarização (1 = preto)

    contours = measure.find_contours(image, 0.8)
    
    dwg = svgwrite.Drawing(size=image.shape[::-1])
    for contour in contours:
        points = [(int(p[1]), int(p[0])) for p in contour]
        if len(points) > 2:
            dwg.add(dwg.polygon(points=points, fill='black'))

    svg_io = io.BytesIO()
    dwg.write(svg_io)
    svg_io.seek(0)

    return send_file(svg_io, mimetype='image/svg+xml', as_attachment=True, download_name='vetorfast.svg')
