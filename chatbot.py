import requests
from flask import Flask, request, jsonify, render_template, Response
import json
import subprocess
import atexit
import threading

app = Flask(__name__)

API_URL = "http://localhost:11434/api/chat"

messages = []  # Global variable to store messages

def get_models():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    models = result.stdout.splitlines()
    if models:
        models.pop(0)
    models = [model.split()[0] for model in models]
    print(f"Available models: {models}")  # Debugging line
    return models

@app.route("/")
def home():
    models = get_models()
    return render_template("index.html", models=models)

@app.route("/chat", methods=["GET"])
def chat():
    user_message = request.args.get("message")
    selected_model = request.args.get("model")
    messages.append({"role": "user", "content": user_message})
    return Response(generate_response(user_message, selected_model), content_type='text/event-stream')

@app.route("/stop_model", methods=["GET"])
def stop_model():
    model_name = request.args.get("model")
    threading.Thread(target=subprocess.run, args=(["ollama", "stop", model_name],)).start()
    return jsonify({"status": "stopped", "model": model_name})

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

def stop_all_models():
    try:
        models = get_models()
        for model in models:
            threading.Thread(target=subprocess.run, args=(["ollama", "stop", model],)).start()
    except Exception as e:
        print(f"Error stopping models: {e}")

atexit.register(stop_all_models)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
