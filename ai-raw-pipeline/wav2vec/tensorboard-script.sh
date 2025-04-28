#!/bin/bash

# Set default values
LOG_DIR="wav2vec2-swahili-finetuned/logs"
HOST="0.0.0.0"  # Allow connections from any IP
PORT="6006"     # Default TensorBoard port
CUSTOM_TITLE="Wav2Vec2 Swahili Training Monitor"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --logdir)
      LOG_DIR="$2"
      shift
      shift
      ;;
    --port)
      PORT="$2"
      shift
      shift
      ;;
    --host)
      HOST="$2"
      shift
      shift
      ;;
    --title)
      CUSTOM_TITLE="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--logdir DIR] [--port PORT] [--host HOST] [--title TITLE]"
      exit 1
      ;;
  esac
done

# Check if TensorBoard is installed
if ! command -v tensorboard &> /dev/null; then
    echo "TensorBoard not found. Installing..."
    pip install tensorboard
fi

# Check if log directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo "Log directory $LOG_DIR does not exist."
    echo "Creating directory..."
    mkdir -p "$LOG_DIR"
    echo "Please ensure your training script is configured to log to this directory."
fi

# Get server IP for easier access instructions
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="your-server-ip"
fi

# Print access instructions
echo "========================================================"
echo "Starting TensorBoard for Wav2Vec2 Swahili Training"
echo "========================================================"
echo "Log directory: $LOG_DIR"
echo "Server IP: $SERVER_IP"
echo "Port: $PORT"
echo ""
echo "Access TensorBoard on the server at:"
echo "  http://localhost:$PORT"
echo ""
echo "To access from your local machine, use one of these methods:"
echo ""
echo "1. SSH Port Forwarding (Recommended, most secure):"
echo "   Run this command on your local machine:"
echo "   ssh -L $PORT:localhost:$PORT username@$SERVER_IP"
echo "   Then access in your browser: http://localhost:$PORT"
echo ""
echo "2. Direct Access (If your server allows):"
echo "   http://$SERVER_IP:$PORT"
echo ""
echo "3. For persistent monitoring even after SSH disconnection:"
echo "   Use 'screen' or 'tmux' to keep this session running."
echo "   Example (with screen):"
echo "   screen -S tensorboard"
echo "   ./monitor_tensorboard.sh"
echo "   (Detach with Ctrl+A, D. Reattach with: screen -r tensorboard)"
echo "========================================================"

# Start TensorBoard
echo "Starting TensorBoard... Press Ctrl+C to stop."
tensorboard --logdir="$LOG_DIR" --host="$HOST" --port="$PORT" --window_title="$CUSTOM_TITLE"