from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import io
import numpy as np
from PIL import Image
import svgwrite
from skimage import measure

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Vetorfast está online!"

@app.route("/vectorize", methods=["POST"])
def vectorize():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    image_file = request.files['image']
    image = Image.open(image_file).convert("RGB")
    width, height = image.size
    img_array = np.array(image)

    dwg = svgwrite.Drawing(size=(width, height))
    dwg.viewbox(0, 0, width, height)

    # Identifica cores únicas na imagem
    unique_colors = np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0)

    for color in unique_colors:
        # Cria uma máscara onde a cor aparece
        mask = np.all(img_array == color, axis=-1).astype(np.uint8)
        contours = measure.find_contours(mask, 0.5)

        for contour in contours:
            # Inverter eixo Y para coordenadas SVG
            points = [(x, y) for y, x in contour]
            path_data = "M " + " L ".join([f"{x},{y}" for x, y in points]) + " Z"
            rgb = f"rgb({color[0]},{color[1]},{color[2]})"
            dwg.add(dwg.path(d=path_data, fill=rgb, stroke="none"))

    svg_io = io.BytesIO()
    dwg.write(svg_io)
    svg_io.seek(0)

    return send_file(
        svg_io,
        mimetype="image/svg+xml",
        as_attachment=True,
        download_name="vetorfast_output.svg"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
