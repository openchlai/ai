#!/bin/bash
# Install and setup ngrok for local MLflow access

# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin

# Authenticate (get token from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000 &

# Start ngrok tunnel
ngrok http 5000