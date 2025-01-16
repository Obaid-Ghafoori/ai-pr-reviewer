from flask import Flask, request, jsonify
from webhook_handler import is_pull_request_event, parse_pull_request_payload, fetch_pr_diff
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
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
        diff_content = fetch_pr_diff(pr_details["diff_url"], GITHUB_TOKEN)
        # Placeholder for AI review logic integration
        return jsonify({"message": "Pull request processed.", "pr_details": pr_details}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)


@app.route("/webhook", methods=["GET"])
def test_webhook():
    return jsonify({"message": "Webhook endpoint is live!"}), 200

