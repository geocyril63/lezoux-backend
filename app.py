import os
import shutil
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
        "voirie.geojson",

    "Éclairage":
        "eclairage.geojson",

    "Dépôts sauvages":
        "depots_sauvages.geojson",

    "Mobilier urbain":
        "mobilier_urbain.geojson",

    "Espaces verts":
        "espaces_verts.geojson",
}


def push_to_github(
    file_name,
    geojson,
):

    try:

        print("")
        print("===================================")
        print("CLONAGE REPO GITHUB")
        print("===================================")

        repo_dir = "/tmp/lezoux-data"

        if os.path.exists(repo_dir):

            shutil.rmtree(
                repo_dir
            )

        subprocess.run(

            [
                "git",
                "clone",
                REPO_URL,
                repo_dir,
            ],

            check=True,
        )

        print("REPO CLONE")

        target_file = os.path.join(

            repo_dir,
            file_name,
        )

        with open(
            target_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(

                geojson,
                f,

                ensure_ascii=False,

                indent=2,
            )

        print("FICHIER GEOJSON MIS A JOUR")

        subprocess.run(

            [
                "git",
                "-C",
                repo_dir,
                "config",
                "user.email",
                "lezouxreferents@gmail.com",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "-C",
                repo_dir,
                "config",
                "user.name",
                "Lezoux Referents",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "-C",
                repo_dir,
                "add",
                ".",
            ],

            check=True,
        )

        subprocess.run(

            [
                "git",
                "-C",
                repo_dir,
                "commit",
                "-m",
                "Ajout signalement",
            ],

            check=False,
        )

        subprocess.run(

            [
                "git",
                "-C",
                repo_dir,
                "push",
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

        file_name = CATEGORY_FILES[
            category
        ]

        print(
            f"FICHIER CIBLE : {file_name}"
        )

        repo_dir = "/tmp/local-working-copy"

        if os.path.exists(repo_dir):

            shutil.rmtree(
                repo_dir
            )

        subprocess.run(

            [
                "git",
                "clone",
                REPO_URL,
                repo_dir,
            ],

            check=True,
        )

        target_file = os.path.join(

            repo_dir,
            file_name,
        )

        with open(
            target_file,
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

        print(
            "POINT GEOJSON AJOUTE"
        )

        push_to_github(
            file_name,
            geojson,
        )

        print("===================================")
        print("FIN TRAITEMENT")
        print("===================================")

        return jsonify({

            "success": True,
        })

    except Exception as e:

        print("")
        print("ERREUR BACKEND :")
        print(e)
        print("")

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