from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json

app = Flask(__name__)
CORS(app, resources={r"/datos/*": {"origins": "*"}})  # Puedes ajustar esto luego

GOOGLE_SHEETS = {
    "registro": "https://docs.google.com/spreadsheets/d/1Tw6frDC-fVMQVakK4GxoKaGl7NigvC-FHrWikSR4TyY/gviz/tq?tqx=out:json",
    "expediente": "https://docs.google.com/spreadsheets/d/1QLDsyLfHi60W8COKfGhQhAFCMcQYKhON19gsdYHoj2o/gviz/tq?tqx=out:json"
}

CAMPOS_SENSIBLES_REGISTRO = {
    "EMAIL", "FECHA ENTRADA",
    "TELÉFONO", "MÓVIL 1", "MÓVIL 2", "OBSERVACIONES"
}

@app.route('/datos')
def obtener_datos():
    tipo = request.args.get("tipo")
    if tipo not in GOOGLE_SHEETS:
        return jsonify({"error": "Tipo no válido"}), 400

    url = GOOGLE_SHEETS[tipo]
    response = requests.get(url)
    match = re.search(r"setResponse\((.*)\);", response.text, re.DOTALL)
    if match:
        json_data = match.group(1)
        try:
            data = json.loads(json_data)
            headers = [col["label"] for col in data["table"]["cols"]]
            result = []

            for row in data["table"]["rows"]:
                obj = {}
                for i, cell in enumerate(row["c"]):
                    key = headers[i]
                    value = cell["v"] if cell else ""

                    if tipo == "registro" and key in CAMPOS_SENSIBLES_REGISTRO:
                        continue
                    
                    obj[key] = value

                result.append(obj)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": "Error procesando JSON", "details": str(e)}), 500
    else:
        return jsonify({"error": "No se pudo interpretar la respuesta de Google"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
