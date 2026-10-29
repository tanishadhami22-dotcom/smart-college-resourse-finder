from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Get the project folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "resources.json")


# Load resources from the JSON file
def load_resources():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("resources.json must contain a JSON list")

    return data


# Open the website homepage
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# Check backend status
@app.route("/api/status")
def status():
    return jsonify({
        "message": "Welcome to Smart Resources Finder Backend!",
        "status": "Backend is running",
        "available_api": "/api/resources"
    })


# Search and filter resources
@app.route("/api/resources", methods=["GET"])
def get_resources():
    try:
        resources = load_resources()

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("Resource loading error:", error)
        return jsonify({"error": str(error)}), 500

    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "All").strip().lower()

    results = []

    for resource in resources:
        # Check that each resource has the required information
        if not all(key in resource for key in ("name", "category", "location")):
            continue

        matches_query = (
            query in resource["name"].lower()
            or query in resource["category"].lower()
            or query in resource["location"].lower()
        )

        matches_category = (
            category == "all"
            or resource["category"].lower() == category
            or (
                category == "labs"
                and resource["category"].lower() == "laboratory"
            )
        )

        if matches_query and matches_category:
            results.append(resource)

    return jsonify(results)


# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)