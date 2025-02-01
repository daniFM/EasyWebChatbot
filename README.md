# EasyWebChatbot
This is just a python and web envelope for the Ollama API, to allow for chatting to different AI models in your local network.

## Setup
Install dependencies.
In the project folder, open a command prompt and run:
```
pip install flask
```

## Usage
Just run the python script by double clicking it.
Connect to it via a web browser on the address that gets displayed at the beginning.
![Screenshot](Screenshot%202025-02-01%20103553.png){ width=50% }
You can change the model from the list at any time, the AI will do its best to continue the conversation.
To close the server, press `CTRL+C`, this will ensure the loaded model stops running.

## Features
- Change AI model on the fly
- Formatting for "think" flag
- Markdown support
- AI response streaming