from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import io
from PIL import Image
import numpy as np
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
    bmp = np.where(bmp == 0, 1, 0)  # inverte

    bitmap = potrace.Bitmap(bmp)
    path = bitmap.trace()

    svg_io = io.StringIO()
    svg_io.write('<svg xmlns="http://www.w3.org/2000/svg">\n')
    for curve in path:
        svg_io.write('<path d="')
        start = curve.start_point
        svg_io.write(f'M {start[0]} {start[1]} ')
        for segment in curve:
            if segment.is_corner:
                c = segment.c
                end = segment.end_point
                svg_io.write(f'L {c[0]} {c[1]} {end[0]} {end[1]} ')
            else:
                c1, c2 = segment.c1, segment.c2
                end = segment.end_point
                svg_io.write(f'C {c1[0]} {c1[1]} {c2[0]} {c2[1]} {end[0]} {end[1]} ')
        svg_io.write('Z" fill="black"/>\n')
    svg_io.write('</svg>')

    svg_bytes = io.BytesIO(svg_io.getvalue().encode("utf-8"))
    return send_file(svg_bytes, mimetype='image/svg+xml', as_attachment=True, download_name="vetorizado.svg")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
