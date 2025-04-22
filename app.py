import os
import io
import numpy as np
from PIL import Image
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import potrace

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
    image = image.point(lambda x: 0 if x < 128 else 1, '1')  # binariza

    bmp = np.array(image, dtype=np.uint32)
    bmp = np.where(bmp == 0, 1, 0)  # inverte: 1 = preto, 0 = branco

    bitmap = potrace.Bitmap(bmp)
    path = bitmap.trace()

    svg = io.StringIO()
    for curve in path:
        svg.write('<path d="M ')
        for segment in curve:
            if segment.is_corner:
                c = segment.c
                svg.write(f'L {c[0][0]} {c[0][1]} {c[1][0]} {c[1][1]} ')
            else:
                c = segment.c
                svg.write(f'C {c[0][0]} {c[0][1]}, {c[1][0]} {c[1][1]}, {c[2][0]} {c[2][1]} ')
        svg.write('Z" fill="black"/>\n')
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
