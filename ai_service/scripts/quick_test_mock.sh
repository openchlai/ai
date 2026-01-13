#!/bin/bash
# Quick test script for mock Asterisk system

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "======================================================"
echo "  Mock Asterisk Quick Test"
echo "======================================================"
echo ""

# Check if test_audio folder exists and has files
if [ ! -d "$PROJECT_DIR/test_audio" ]; then
    echo "❌ Error: test_audio folder not found"
    echo "Creating test_audio folder..."
    mkdir -p "$PROJECT_DIR/test_audio"
fi

AUDIO_COUNT=$(find "$PROJECT_DIR/test_audio" -type f \( -name "*.wav" -o -name "*.WAV" -o -name "*.mp3" -o -name "*.gsm" \) | wc -l)

if [ "$AUDIO_COUNT" -eq 0 ]; then
    echo "⚠️  Warning: No audio files found in test_audio/"
    echo "Please add WAV, MP3, or GSM files to test_audio/ folder"
    echo ""
    echo "Example:"
    echo "  cp /path/to/your/audio.wav $PROJECT_DIR/test_audio/"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
else
    echo "✅ Found $AUDIO_COUNT audio file(s) in test_audio/"
    echo ""
    echo "Audio files:"
    ls -lh "$PROJECT_DIR/test_audio/" | grep -E "\.(wav|WAV|mp3|gsm)" || true
    echo ""
fi

# Parse command line arguments
MODE="${1:-realtime}"
COUNT="${2:-1}"
INTERVAL="${3:-15}"
SPEED="${4:-1}"

echo "Test Configuration:"
echo "  Mode:     $MODE"
echo "  Calls:    $COUNT"
echo "  Interval: ${INTERVAL}s"
echo "  Speed:    ${SPEED}x"
echo ""

# Check if server is running
if ! curl -s http://localhost:8123/health > /dev/null 2>&1; then
    echo "❌ Error: Server not running on port 8123"
    echo ""
    echo "Please start the server first:"
    echo "  python -m app.main --enable-streaming"
    echo ""
    exit 1
fi

echo "✅ Server is running"
echo ""

# Run based on mode
case $MODE in
    realtime|real-time|streaming)
        echo "🎙️  Starting real-time streaming test..."
        echo ""
        python "$SCRIPT_DIR/mock_asterisk.py" \
            --audio-folder "$PROJECT_DIR/test_audio" \
            --count "$COUNT" \
            --interval "$INTERVAL" \
            --speed "$SPEED"
        ;;

    fast)
        echo "⚡ Starting fast mode test (10x speed)..."
        echo ""
        python "$SCRIPT_DIR/mock_asterisk.py" \
            --audio-folder "$PROJECT_DIR/test_audio" \
            --count "$COUNT" \
            --interval "$INTERVAL" \
            --speed 10
        ;;

    post-call|postcall)
        echo "📥 Post-call mode requires mock_enabled=true in .env"
        echo "After enabling, run realtime mode - post-call will trigger automatically"
        echo ""
        echo "Enable with:"
        echo "  sed -i 's/MOCK_ENABLED=false/MOCK_ENABLED=true/' .env"
        echo "  # Then restart server"
        echo ""
        ;;

    help|--help|-h)
        echo "Usage: $0 [MODE] [COUNT] [INTERVAL] [SPEED]"
        echo ""
        echo "Modes:"
        echo "  realtime    - Real-time streaming (default)"
        echo "  fast        - Fast mode (10x speed)"
        echo "  post-call   - Information about post-call testing"
        echo ""
        echo "Arguments:"
        echo "  COUNT       - Number of concurrent calls (default: 1)"
        echo "  INTERVAL    - Seconds between calls (default: 15)"
        echo "  SPEED       - Speed multiplier (default: 1.0)"
        echo ""
        echo "Examples:"
        echo "  $0 realtime 1           # Single call"
        echo "  $0 realtime 3 15        # 3 calls, 15s apart"
        echo "  $0 fast 1               # Fast mode"
        echo ""
        ;;

    *)
        echo "❌ Unknown mode: $MODE"
        echo "Use: realtime, fast, post-call, or help"
        exit 1
        ;;
esac

echo ""
echo "======================================================"
echo "  Test Complete"
echo "======================================================"
