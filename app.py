import os
import subprocess
import json

from flask import (
    Flask,
    request,
    jsonify,
)

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)

REPO_URL = (
    "https://"
    f"{GITHUB_TOKEN}"
    "@github.com/"
    "geocyril63/"
    "lezoux-referents-data.git"
)

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


def push_to_github():

    try:

        print("")
        print("===================================")
        print("PUSH GITHUB...")
        print("===================================")

        subprocess.run(

            [
                "git",
                "config",
                "--global",
                "user.email",
                "lezouxreferents@gmail.com",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "config",
                "--global",
                "user.name",
                "Lezoux Referents",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "remote",
                "set-url",
                "origin",
                REPO_URL,
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "add",
                ".",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "commit",
                "-m",
                "Ajout signalement",
            ],

            check=False,
        )

        subprocess.run(

            [
                "git",
                "push",
                "origin",
                "main",
            ],

            check=True,
        )

        print("")
        print("PUSH GITHUB OK")
        print("===================================")

    except Exception as e:

        print("")
        print("ERREUR PUSH GITHUB")
        print(e)
        print("===================================")


@app.route("/")
def home():

    return "Lezoux Referents API OK"


@app.route(
    "/report",
    methods=["POST"],
)
def report():

    print("")
    print("===================================")
    print("NOUVEAU SIGNALEMENT RECU")
    print("===================================")

    try:

        data = request.json

        print("DONNEES RECUES :")
        print(data)

        category = data["category"]

        file_path = CATEGORY_FILES[
            category
        ]

        print(
            f"FICHIER CIBLE : {file_path}"
        )

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

        print(
            "POINT GEOJSON AJOUTE"
        )

        push_to_github()

        print("===================================")
        print("FIN TRAITEMENT")
        print("===================================")

        return jsonify({

            "success": True,
        })

    except Exception as e:

        print("ERREUR BACKEND :")
        print(e)

        return jsonify({

            "success": False,

            "error": str(e),
        }), 500


if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000,
    )