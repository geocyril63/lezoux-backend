import json

from flask import Flask, request, jsonify

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

CATEGORY_FILES = {

    "Voirie":
        "geojson/voirie.geojson",

    "Éclairage":
        "geojson/eclairage.geojson",

    "Dépôts sauvages":
        "geojson/depots_sauvages.geojson",

    "Mobilier urbain":
        "geojson/mobilier_urbain.geojson",

    "Espaces verts":
        "geojson/espaces_verts.geojson",
}

@app.route("/")
def home():

    return "Lezoux Referents API OK"

@app.route("/report", methods=["POST"])
def report():

    data = request.json

    category = data["category"]

    file_path = CATEGORY_FILES[category]

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as f:

        geojson = json.load(f)

    feature = {

        "type": "Feature",

        "geometry": {

            "type": "Point",

            "coordinates": [

                data["longitude"],
                data["latitude"],
            ],
        },

        "properties": {

            "category":
                data["category"],

            "priority":
                data["priority"],

            "description":
                data["description"],

            "author":
                data["author"],

            "status":
                "nouveau",
        },
    }

    geojson["features"].append(
        feature,
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            geojson,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return jsonify({

        "success": True,
    })

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000,
    )