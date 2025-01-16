from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Welcome to ai pr reviewer app")
    print(f"Webhook received: {data}")
    return "Webhook received", 200

if __name__ == '__main__':
    app.run(port=5000)