from flask import Flask, request, jsonify
from webhook_handler import is_pull_request_event, parse_pull_request_payload, process_pull_request
from utils import fetch_pr_diff

from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# print(f"GITHUB_TOKEN loaded: {GITHUB_TOKEN}") 
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable not set")


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    headers = request.headers
    payload = request.json

    if not is_pull_request_event(headers):
        return jsonify({"message": "Not a pull request event."}), 400

    pr_details = parse_pull_request_payload(payload)
    if not pr_details:
        return jsonify({"message": "Unsupported pull request action."}), 400

    try:
        analysis_results = process_pull_request(payload, GITHUB_TOKEN)
        return jsonify(analysis_results), 200
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}, {e.__cause__, e.__context__, e.with_traceback}"}), 500


@app.route("/webhook", methods=["GET"])
def test_webhook():
    """
    Test endpoint to verify if the webhook is live.
    """
    return jsonify({"message": "Webhook endpoint is live!"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

