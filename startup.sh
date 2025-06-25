#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Start the application using Gunicorn
gunicorn main:main_app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
