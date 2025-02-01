# EasyWebChatbot
This is just a python and web envelope for the Ollama API, to allow for chatting to different AI models in your local network.

## Setup
### Install ollama
This project uses the [Ollama](https://ollama.com) API. It needs to be installed to start using the server.
After Ollama is installed, go ahead and try installing an AI model. For example:
```
ollama pull deepseek-r1:14b
```
This one needs a bit of a beefy PC, you can try a lower distilled model from their [list](https://ollama.com/library/deepseek-r1:8b).

### Install dependencies
In the project folder, open a command prompt and run:
```
pip install flask
```

## Usage
Just run the python script by double clicking it.
Connect to it via a web browser on the address that gets displayed at the beginning.
<div align="center">
    <img src="Screenshot%202025-02-01%20103553.png" width="50%" alt="Screenshot">
</div>
You can change the model from the list at any time, the AI will do its best to continue the conversation.
To close the server, press <kbd>CTRL</kbd>+<kbd>C</kbd>, this will ensure the loaded model stops running.

## Features
- Change AI model on the fly
- Formatting for "think" flag
- Markdown support
- AI response streaming
