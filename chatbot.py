import requests
from flask import Flask, request, jsonify, render_template, Response
import json
import subprocess
import atexit
import threading
import os

app = Flask(__name__)

API_URL = "http://localhost:11434/api/chat"
CONVERSATIONS_FILE = "conversations.json"

conversations = {}  # Global variable to store conversations

def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, 'r') as file:
            data = json.load(file)
            return data.get("conversations")
    return {}

def save_conversations():
    with open(CONVERSATIONS_FILE, 'w') as file:
        json.dump({"conversations": conversations}, file, indent=2)

conversations = load_conversations()

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
    conversation_name = request.args.get("conversation")
    if conversation_name not in conversations:
        conversation_name = conversation_name[:32]  # Limit conversation name to 32 characters
        conversations[conversation_name] = []
    conversations[conversation_name].append({"role": "user", "content": user_message})
    save_conversations()
    return Response(generate_response(user_message, selected_model, conversation_name), content_type='text/event-stream')

@app.route("/stop_model", methods=["GET"])
def stop_model():
    model_name = request.args.get("model")
    threading.Thread(target=subprocess.run, args=(["ollama", "stop", model_name],)).start()
    return jsonify({"status": "stopped", "model": model_name})

@app.route("/load_conversations", methods=["GET"])
def load_conversations_route():
    return jsonify({"conversations": conversations})

def generate_response(user_message, model_name, conversation_name):
    payload = {
        "model": model_name,
        "messages": conversations[conversation_name],
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
    conversations[conversation_name].append({"role": "assistant", "content": combined_message})
    save_conversations()
    yield "event: close\n\n"
    print(f"Updated conversations: {json.dumps(conversations, indent=2)}")  # Debugging line

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
