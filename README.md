# gradio_chat
A Gradio Chat App 

## Installation

Dependencies:
- [Python](https://www.python.org/)

Install the Python dependencies using the following commands:
```bash
python -m pip install virtualenv
python -m venv venv
```
If you are using windows:
```bash
venv\Scripts\activate
```
On linux-based systems:
```bash
source venv/bin/activate
```
Install for development:
```bash
python -m pip install -e .
```

## Usage

### Manual Usage

You can start the gradio app manually with the following command:
```bash
python src/frontend/main.py
```

### Docker Compose

You can also use the gradio app with the provided docker compose setup. Just follow the commands below:
```bash
docker compose build
docker compose up
```