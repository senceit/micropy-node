from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import string
import json
import os, sys

sys.path.append("src")

app = Flask(__name__)
CORS(app)

dirname = os.path.dirname(__file__)
config_file = os.path.join(dirname, "./config.json")


@app.route("/config", methods=["GET", "POST"])
def get_config():
    if request.method == "GET":
        from config import config

        config["networks"] = ["Swart", "Swart-LTE"]
        return jsonify(config)

    elif request.method == "POST":
        print(request)
        print(request.get_json())
        # with open(config_file, "w") as f:
        #     f.write(json.dumps(request.get_json(), indent=2))

        return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
