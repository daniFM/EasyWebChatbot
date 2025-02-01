import requests
from flask import Flask, request, jsonify, render_template, Response
import json

app = Flask(__name__)

API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1:8b"

messages = []  # Global variable to store messages

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["GET"])
def chat():
    user_message = request.args.get("message")
    selected_model = request.args.get("model", MODEL_NAME)
    messages.append({"role": "user", "content": user_message})
    return Response(generate_response(user_message, selected_model), content_type='text/event-stream')

def generate_response(user_message, model_name):
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": True
    }
    print(f"Sending payload to API: {json.dumps(payload, indent=2)}")  # Debugging line
    response = requests.post(API_URL, json=payload, stream=True)
    combined_message = ""
    for line in response.iter_lines():
        if line:
            response_data = json.loads(line.decode('utf-8'))
            message_content = response_data.get("message", {}).get("content", "")
            combined_message += message_content
            yield f"data: {json.dumps({'message': {'content': combined_message}})}\n\n"
    messages.append({"role": "assistant", "content": combined_message})
    yield "event: close\n\n"
    print(f"Updated messages: {json.dumps(messages, indent=2)}")  # Debugging line

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
