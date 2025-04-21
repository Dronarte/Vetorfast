from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import io
from PIL import Image
import potrace# import potrace
import numpy as np

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
    img = Image.open(image_file).convert("L")  # Converte para escala de cinza
    bitmap = np.array(img) < 128  # Binariza

    bmp = potrace.Bitmap(bitmap)
    path = bmp.trace()

    svg_data = io.StringIO()
    svg_data.write('<?xml version="1.0" standalone="no"?>\n')
    svg_data.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n')

    for curve in path:
        svg_data.write('<path d="')
        for segment in curve:
            start = segment.start_point
            if segment.is_corner:
                c = segment.c
                svg_data.write(f'M {start.x},{start.y} L {c.x},{c.y} ')
            else:
                c1, c2, end = segment.c1, segment.c2, segment.end_point
                svg_data.write(f'M {start.x},{start.y} C {c1.x},{c1.y} {c2.x},{c2.y} {end.x},{end.y} ')
        svg_data.write('" stroke="black" fill="none"/>\n')

    svg_data.write('</svg>')
    svg_data.seek(0)

    return send_file(
        io.BytesIO(svg_data.getvalue().encode()),
        mimetype='image/svg+xml',
        as_attachment=True,
        download_name="imagem_vetorizada.svg"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
