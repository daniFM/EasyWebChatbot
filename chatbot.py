import os
import re
import json
import requests
import subprocess
import atexit
import threading
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)
API_URL = "http://localhost:11434/api/chat"
messages = []  # Global conversation messages

MEMORY_FILE = "memory.txt"

def get_models():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    models = result.stdout.splitlines()
    if models:
        models.pop(0)  # remove header
        models = [model.split()[0] for model in models]
    print(f"Available models: {models}")
    return models

def load_memory():
    """Load persistent memory from MEMORY_FILE (if it exists)."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            mem = f.read().strip()
        return mem
    return ""

def save_memory_fact(fact):
    """Save a new fact if it doesn't already exist (simple check)."""
    fact = fact.strip()
    if not fact:
        return
    current_mem = set()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                current_mem.add(line.strip().lower())
    if fact.lower() not in current_mem:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(fact + "\n")
        print(f"Memory updated with: {fact}")
    else:
        print("Fact already stored.")

def extract_fact(text):
    """
    Extract a fact from user messages if they include phrases like "remember" or "note that".
    Returns the content following the trigger word.
    """
    match = re.search(r"(?:remember|note that)\s+(.*)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

@app.route("/")
def home():
    models = get_models()
    return render_template("index.html", models=models)

@app.route("/chat", methods=["GET"])
def chat():
    user_message = request.args.get("message")
    # Get the model from the GET parameter; fall back to default if not provided.
    selected_model = request.args.get("model") or "deepseek-r1:latest"
    
    if not messages:
        mem = load_memory()
        if mem:
            messages.append({"role": "system", "content": mem})
            print("Loaded persistent memory into context.")
    
    new_fact = extract_fact(user_message)
    if new_fact:
        save_memory_fact(new_fact)
    
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
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
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
    print(f"Updated messages: {json.dumps(messages, indent=2)}")

def stop_all_models():
    try:
        models = get_models()
        for model in models:
            threading.Thread(target=subprocess.run, args=(["ollama", "stop", model],)).start()
    except Exception as e:
        print(f"Error stopping models: {e}")

atexit.register(stop_all_models)

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://localhost:5000")
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
