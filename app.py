import os
import io
import numpy as np
from PIL import Image
import cv2
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Vetorfast Online!"

@app.route("/vectorize", methods=["POST"])
def vectorize():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['image']
    image = Image.open(file).convert("L")
    img_np = np.array(image)

    _, thresh = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    svg = io.StringIO()
    svg.write('<?xml version="1.0" standalone="no"?>\n')
    svg.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n')

    for contour in contours:
        svg.write('<path d="M ')
        for point in contour:
            x, y = point[0]
            svg.write(f'{x},{y} ')
        svg.write('Z" stroke="black" fill="black"/>\n')

    svg.write('</svg>')

    return send_file(
        io.BytesIO(svg.getvalue().encode()),
        mimetype='image/svg+xml',
        download_name='vetorizado.svg',
        as_attachment=True
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
