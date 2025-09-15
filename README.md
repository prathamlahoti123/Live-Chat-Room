## About
This project represents a fork of [Joshwen7947](https://github.com/Joshwen7947)'s [repository](https://github.com/Joshwen7947/Live-Chat-Room), which provides a basic implementation of a live chat based on websockets using [Flask-SocketIO](https://github.com/miguelgrinberg/flask-socketio) library.


## What's Added


## System Requirements
* Python 3.12
* UV package manager
* Docker and Docker Compose plugin


## Configuration
The application can be configured using environment variables defined in the `.env` file. Key configurations include:
* settings for Flask application;
* settings Nginx.

Use [.env.example](.env.example) file as a template to create your own `.env` file.


## Deployment
Once the configuration file is set up, you can deploy the application using Docker Compose:
```
docker compose up -d
```

The will start all necessary services including the Flask application and Nginx.

During development it can be more convenient to run the application without Docker. To do so, first install the dependencies using UV:
```bash
uv sync --all-groups
```

Then, run the application:
```bash
export PYTHONPATH="src/:$PYTHONPATH"
uv run python src/app/main.py
```


## Usage


## References
- Original [repository](https://github.com/Joshwen7947/Live-Chat-Room) provided by [Joshwen7947](https://github.com/Joshwen7947)
- [Flask](https://github.com/pallets/flask)
- [Flask-SocketIO](https://github.com/miguelgrinberg/flask-socketio)
