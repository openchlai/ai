# app/web/monitoring_dashboard.py - Real-time monitoring dashboard

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from utils.live_audio_streamer import get_live_audio_streamer
from utils.call_data_logger import get_call_logger

logger = logging.getLogger(__name__)

# Dashboard router
class MonitoringDashboard:
    """Real-time monitoring dashboard for AI service calls"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.live_streamer = get_live_audio_streamer()
        
        # Register routes
        self._register_routes()
        
        # Create web assets directory if needed
        self.web_dir = Path(__file__).parent / "static"
        self.web_dir.mkdir(exist_ok=True)
        
        logger.info("🌐 Monitoring dashboard initialized")
    
    def _register_routes(self):
        """Register dashboard routes"""
        
        @self.app.get("/monitoring", response_class=HTMLResponse)
        async def monitoring_dashboard(request: Request):
            """Serve the monitoring dashboard HTML"""
            return self._get_dashboard_html()
        
        @self.app.websocket("/monitoring/ws")
        async def monitoring_websocket(websocket: WebSocket):
            """WebSocket endpoint for live monitoring"""
            await self._handle_monitoring_websocket(websocket)
        
        @self.app.websocket("/monitoring/ws/call/{call_id}")
        async def call_monitoring_websocket(websocket: WebSocket, call_id: str):
            """WebSocket endpoint for specific call monitoring"""
            await self._handle_call_websocket(websocket, call_id)
        
        @self.app.get("/monitoring/api/calls")
        async def get_active_calls():
            """API endpoint to get active calls"""
            if self.live_streamer:
                return {
                    "active_calls": self.live_streamer.get_active_streams(),
                    "global_stats": self.live_streamer.get_global_stats(),
                    "timestamp": datetime.now().isoformat()
                }
            return {"active_calls": {}, "global_stats": {}, "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/monitoring/api/call/{call_id}/logs")
        async def get_call_logs(call_id: str):
            """API endpoint to get call logs"""
            call_logger = get_call_logger(call_id, create_if_not_exists=False)
            if not call_logger:
                return {"error": "Call logger not found"}
            
            return {
                "call_id": call_id,
                "log_directory": call_logger.get_call_directory(),
                "audio_files": call_logger.list_audio_files(),
                "tcp_packets": len(call_logger.tcp_packets),
                "audio_segments": len(call_logger.audio_segments),
                "transcriptions": len(call_logger.transcriptions)
            }
    
    async def _handle_monitoring_websocket(self, websocket: WebSocket):
        """Handle global monitoring WebSocket connection"""
        await websocket.accept()
        
        if not self.live_streamer:
            await websocket.send_json({
                "type": "error",
                "message": "Live streaming is not enabled"
            })
            await websocket.close()
            return
        
        # Add to global connections
        self.live_streamer.add_websocket_connection(websocket)
        
        try:
            # Send initial status
            await websocket.send_json({
                "type": "status",
                "data": {
                    "connected": True,
                    "monitoring_type": "global",
                    "active_calls": self.live_streamer.get_active_streams(),
                    "stats": self.live_streamer.get_global_stats()
                }
            })
            
            # Keep connection alive and handle client messages
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    
                    # Handle client requests
                    if data.get("type") == "get_stats":
                        await websocket.send_json({
                            "type": "stats_response",
                            "data": self.live_streamer.get_global_stats()
                        })
                    
                except Exception as e:
                    logger.debug(f"Error handling WebSocket message: {e}")
                    break
                    
        except WebSocketDisconnect:
            logger.info("🔌 Global monitoring WebSocket disconnected")
        except Exception as e:
            logger.error(f"❌ Error in monitoring WebSocket: {e}")
        finally:
            # Remove from connections
            self.live_streamer.remove_websocket_connection(websocket)
    
    async def _handle_call_websocket(self, websocket: WebSocket, call_id: str):
        """Handle call-specific monitoring WebSocket connection"""
        await websocket.accept()
        
        if not self.live_streamer:
            await websocket.send_json({
                "type": "error", 
                "message": "Live streaming is not enabled"
            })
            await websocket.close()
            return
        
        # Add to call-specific connections
        self.live_streamer.add_websocket_connection(websocket, call_id)
        
        try:
            # Send initial status
            active_streams = self.live_streamer.get_active_streams()
            call_info = active_streams.get(call_id, {})
            
            await websocket.send_json({
                "type": "status",
                "data": {
                    "connected": True,
                    "monitoring_type": "call_specific",
                    "call_id": call_id,
                    "call_info": call_info,
                    "active": call_id in active_streams
                }
            })
            
            # Keep connection alive
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    
                    # Handle client requests for this specific call
                    if data.get("type") == "get_call_info":
                        current_streams = self.live_streamer.get_active_streams()
                        await websocket.send_json({
                            "type": "call_info_response",
                            "data": current_streams.get(call_id, {})
                        })
                        
                except Exception as e:
                    logger.debug(f"Error handling call WebSocket message: {e}")
                    break
                    
        except WebSocketDisconnect:
            logger.info(f"🔌 Call monitoring WebSocket disconnected for {call_id}")
        except Exception as e:
            logger.error(f"❌ Error in call monitoring WebSocket: {e}")
        finally:
            # Remove from connections
            self.live_streamer.remove_websocket_connection(websocket, call_id)
    
    def _get_dashboard_html(self) -> str:
        """Generate the monitoring dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service - Live Call Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            line-height: 1.6;
        }
        
        .header {
            background: #2d3748;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            color: #4fd1c7;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #f56565;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.connected {
            background: #48bb78;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .panel {
            background: #2d3748;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .panel h2 {
            color: #4fd1c7;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: #4a5568;
            padding: 1rem;
            border-radius: 6px;
            text-align: center;
        }
        
        .stat-card .label {
            color: #a0aec0;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .value {
            color: #4fd1c7;
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .call-list {
            list-style: none;
        }
        
        .call-item {
            background: #4a5568;
            margin-bottom: 0.5rem;
            padding: 1rem;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .call-item:hover {
            background: #5a6578;
        }
        
        .call-item.active {
            background: #2b6cb0;
            border-left: 4px solid #4fd1c7;
        }
        
        .call-id {
            font-weight: bold;
            color: #4fd1c7;
        }
        
        .call-stats {
            color: #a0aec0;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .audio-player {
            background: #4a5568;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
        
        .audio-controls {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        
        .play-button {
            background: #4fd1c7;
            color: #1a1a1a;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            font-weight: bold;
        }
        
        .play-button:hover {
            background: #38b2ac;
        }
        
        .transcription-area {
            background: #1a202c;
            border: 1px solid #4a5568;
            border-radius: 6px;
            padding: 1rem;
            min-height: 200px;
            font-family: 'Courier New', monospace;
            color: #e2e8f0;
            font-size: 0.9rem;
        }
        
        .transcription-entry {
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-left: 3px solid #4fd1c7;
            background: rgba(79, 209, 199, 0.1);
        }
        
        .timestamp {
            color: #a0aec0;
            font-size: 0.8rem;
        }
        
        .log-panel {
            grid-column: span 2;
        }
        
        .log-output {
            background: #1a202c;
            border: 1px solid #4a5568;
            border-radius: 6px;
            padding: 1rem;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            color: #e2e8f0;
            font-size: 0.8rem;
        }
        
        .log-entry {
            margin-bottom: 0.25rem;
        }
        
        .log-entry.info { color: #4fd1c7; }
        .log-entry.warning { color: #f6ad55; }
        .log-entry.error { color: #f56565; }
        
        .controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .control-button {
            background: #4a5568;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            cursor: pointer;
        }
        
        .control-button:hover {
            background: #5a6578;
        }
        
        .control-button.active {
            background: #4fd1c7;
            color: #1a1a1a;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            🎙️ AI Service - Live Call Monitoring
            <div class="status-indicator" id="connection-status"></div>
        </h1>
    </div>
    
    <div class="container">
        <!-- Statistics Panel -->
        <div class="panel">
            <h2>📊 System Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">Active Calls</div>
                    <div class="value" id="active-calls">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Connected Clients</div>
                    <div class="value" id="connected-clients">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Total Connections</div>
                    <div class="value" id="total-connections">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Audio Format</div>
                    <div class="value" id="audio-format">WAV</div>
                </div>
            </div>
        </div>
        
        <!-- Active Calls Panel -->
        <div class="panel">
            <h2>📞 Active Calls</h2>
            <ul class="call-list" id="call-list">
                <li style="color: #a0aec0; font-style: italic;">No active calls</li>
            </ul>
        </div>
        
        <!-- Audio Monitoring Panel -->
        <div class="panel">
            <h2>🎵 Audio Monitor</h2>
            <div class="controls">
                <button class="control-button" id="start-monitoring">Start Monitoring</button>
                <button class="control-button" id="stop-monitoring">Stop Monitoring</button>
                <button class="control-button" id="clear-audio">Clear Audio</button>
            </div>
            
            <div class="audio-player">
                <div>Latest Audio Chunk</div>
                <audio controls id="audio-player" style="width: 100%; margin-top: 0.5rem;">
                    Your browser does not support audio playback.
                </audio>
                <div class="audio-controls">
                    <button class="play-button" id="play-latest">Play Latest</button>
                    <span id="audio-info" style="color: #a0aec0;"></span>
                </div>
            </div>
        </div>
        
        <!-- Transcription Panel -->
        <div class="panel">
            <h2>📝 Live Transcriptions</h2>
            <div class="transcription-area" id="transcription-area">
                <div style="color: #a0aec0; font-style: italic;">Waiting for transcriptions...</div>
            </div>
        </div>
        
        <!-- Log Panel -->
        <div class="panel log-panel">
            <h2>📋 System Logs</h2>
            <div class="controls">
                <button class="control-button active" id="filter-all">All</button>
                <button class="control-button" id="filter-info">Info</button>
                <button class="control-button" id="filter-warning">Warning</button>
                <button class="control-button" id="filter-error">Error</button>
                <button class="control-button" id="clear-logs">Clear</button>
            </div>
            <div class="log-output" id="log-output"></div>
        </div>
    </div>

    <script>
        class MonitoringDashboard {
            constructor() {
                this.ws = null;
                this.isConnected = false;
                this.currentCallId = null;
                this.audioBuffer = [];
                this.logFilter = 'all';
                
                this.initializeUI();
                this.connect();
            }
            
            initializeUI() {
                // Connection status indicator
                this.statusIndicator = document.getElementById('connection-status');
                
                // Statistics elements
                this.statsElements = {
                    activeCalls: document.getElementById('active-calls'),
                    connectedClients: document.getElementById('connected-clients'),
                    totalConnections: document.getElementById('total-connections'),
                    audioFormat: document.getElementById('audio-format')
                };
                
                // Call list
                this.callList = document.getElementById('call-list');
                
                // Audio elements
                this.audioPlayer = document.getElementById('audio-player');
                this.audioInfo = document.getElementById('audio-info');
                
                // Transcription area
                this.transcriptionArea = document.getElementById('transcription-area');
                
                // Log output
                this.logOutput = document.getElementById('log-output');
                
                // Event listeners
                document.getElementById('start-monitoring').onclick = () => this.startMonitoring();
                document.getElementById('stop-monitoring').onclick = () => this.stopMonitoring();
                document.getElementById('clear-audio').onclick = () => this.clearAudio();
                document.getElementById('play-latest').onclick = () => this.playLatest();
                
                // Log filter buttons
                document.getElementById('filter-all').onclick = () => this.setLogFilter('all');
                document.getElementById('filter-info').onclick = () => this.setLogFilter('info');
                document.getElementById('filter-warning').onclick = () => this.setLogFilter('warning');
                document.getElementById('filter-error').onclick = () => this.setLogFilter('error');
                document.getElementById('clear-logs').onclick = () => this.clearLogs();
            }
            
            connect() {
                const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${wsProtocol}//${window.location.host}/monitoring/ws`;
                
                this.log('info', 'Connecting to monitoring server...');
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.updateConnectionStatus(true);
                    this.log('info', 'Connected to monitoring server');
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;
                    this.updateConnectionStatus(false);
                    this.log('warning', 'Connection closed. Reconnecting in 3 seconds...');
                    setTimeout(() => this.connect(), 3000);
                };
                
                this.ws.onerror = (error) => {
                    this.log('error', `WebSocket error: ${error}`);
                };
                
                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                };
            }
            
            handleMessage(message) {
                switch (message.type) {
                    case 'status':
                        this.updateStats(message.data.stats);
                        this.updateCallList(message.data.active_calls);
                        break;
                        
                    case 'audio_chunk':
                        this.handleAudioChunk(message.data, message.metadata);
                        break;
                        
                    case 'transcription_update':
                        this.handleTranscriptionUpdate(message.data);
                        break;
                        
                    case 'stream_end':
                        this.handleStreamEnd(message.call_id, message.summary);
                        break;
                        
                    default:
                        this.log('info', `Received: ${message.type}`);
                }
            }
            
            updateConnectionStatus(connected) {
                this.statusIndicator.className = 'status-indicator' + (connected ? ' connected' : '');
            }
            
            updateStats(stats) {
                if (!stats) return;
                
                this.statsElements.activeCalls.textContent = stats.active_streams || 0;
                this.statsElements.connectedClients.textContent = stats.global_connections || 0;
                this.statsElements.totalConnections.textContent = stats.total_connections || 0;
                this.statsElements.audioFormat.textContent = (stats.audio_format || 'wav').toUpperCase();
            }
            
            updateCallList(activeCalls) {
                if (!activeCalls || Object.keys(activeCalls).length === 0) {
                    this.callList.innerHTML = '<li style="color: #a0aec0; font-style: italic;">No active calls</li>';
                    return;
                }
                
                this.callList.innerHTML = '';
                
                Object.entries(activeCalls).forEach(([callId, callInfo]) => {
                    const callItem = document.createElement('li');
                    callItem.className = 'call-item';
                    if (callId === this.currentCallId) {
                        callItem.classList.add('active');
                    }
                    
                    const duration = callInfo.total_duration || 0;
                    const chunks = callInfo.total_chunks || 0;
                    
                    callItem.innerHTML = `
                        <div class="call-id">${callId}</div>
                        <div class="call-stats">${chunks} chunks • ${duration.toFixed(1)}s • ${callInfo.connected_clients || 0} clients</div>
                    `;
                    
                    callItem.onclick = () => this.selectCall(callId);
                    this.callList.appendChild(callItem);
                });
            }
            
            selectCall(callId) {
                this.currentCallId = callId;
                this.updateCallList(); // Refresh to show selection
                this.log('info', `Selected call: ${callId}`);
            }
            
            handleAudioChunk(chunk, metadata) {
                // Add to audio buffer
                this.audioBuffer.push({
                    ...chunk,
                    metadata: metadata
                });
                
                // Keep only last 10 chunks
                if (this.audioBuffer.length > 10) {
                    this.audioBuffer.shift();
                }
                
                // Update audio info
                this.audioInfo.textContent = `Call: ${chunk.call_id} | Duration: ${chunk.duration_seconds.toFixed(2)}s | Format: ${chunk.format.toUpperCase()}`;
                
                // Auto-play latest if monitoring
                if (this.isMonitoring) {
                    this.playLatest();
                }
                
                this.log('info', `Audio chunk received: ${chunk.call_id} (${chunk.duration_seconds.toFixed(2)}s)`);
            }
            
            handleTranscriptionUpdate(transcription) {
                const entry = document.createElement('div');
                entry.className = 'transcription-entry';
                
                const timestamp = new Date(transcription.timestamp).toLocaleTimeString();
                const confidence = transcription.confidence ? ` (${(transcription.confidence * 100).toFixed(1)}%)` : '';
                
                entry.innerHTML = `
                    <div class="timestamp">${timestamp} • Call: ${transcription.call_id} • Segment: ${transcription.segment_id}${confidence}</div>
                    <div>${transcription.transcript}</div>
                `;
                
                if (this.transcriptionArea.children.length === 1 && this.transcriptionArea.children[0].style.fontStyle === 'italic') {
                    this.transcriptionArea.innerHTML = '';
                }
                
                this.transcriptionArea.appendChild(entry);
                this.transcriptionArea.scrollTop = this.transcriptionArea.scrollHeight;
                
                this.log('info', `Transcription: "${transcription.transcript.substring(0, 50)}..."`);
            }
            
            handleStreamEnd(callId, summary) {
                this.log('info', `Stream ended: ${callId} (${summary.total_chunks} chunks, ${summary.total_duration_seconds.toFixed(1)}s)`);
            }
            
            playLatest() {
                if (this.audioBuffer.length === 0) {
                    this.log('warning', 'No audio chunks available');
                    return;
                }
                
                const latest = this.audioBuffer[this.audioBuffer.length - 1];
                const blob = this.base64ToBlob(latest.audio_b64, `audio/${latest.format}`);
                const url = URL.createObjectURL(blob);
                
                this.audioPlayer.src = url;
                this.audioPlayer.play();
                
                // Clean up old URLs
                setTimeout(() => URL.revokeObjectURL(url), 5000);
            }
            
            base64ToBlob(base64, mimeType) {
                const byteCharacters = atob(base64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: mimeType });
            }
            
            startMonitoring() {
                this.isMonitoring = true;
                document.getElementById('start-monitoring').classList.add('active');
                document.getElementById('stop-monitoring').classList.remove('active');
                this.log('info', 'Started audio monitoring');
            }
            
            stopMonitoring() {
                this.isMonitoring = false;
                document.getElementById('start-monitoring').classList.remove('active');
                document.getElementById('stop-monitoring').classList.add('active');
                this.log('info', 'Stopped audio monitoring');
            }
            
            clearAudio() {
                this.audioBuffer = [];
                this.audioPlayer.src = '';
                this.audioInfo.textContent = '';
                this.log('info', 'Cleared audio buffer');
            }
            
            setLogFilter(filter) {
                this.logFilter = filter;
                
                // Update button states
                document.querySelectorAll('[id^="filter-"]').forEach(btn => btn.classList.remove('active'));
                document.getElementById(`filter-${filter}`).classList.add('active');
                
                // Filter log entries
                const entries = this.logOutput.children;
                for (let entry of entries) {
                    const show = filter === 'all' || entry.classList.contains(filter);
                    entry.style.display = show ? 'block' : 'none';
                }
            }
            
            clearLogs() {
                this.logOutput.innerHTML = '';
            }
            
            log(level, message) {
                const entry = document.createElement('div');
                entry.className = `log-entry ${level}`;
                
                const timestamp = new Date().toLocaleTimeString();
                entry.textContent = `[${timestamp}] ${message}`;
                
                this.logOutput.appendChild(entry);
                this.logOutput.scrollTop = this.logOutput.scrollHeight;
                
                // Keep only last 100 entries
                while (this.logOutput.children.length > 100) {
                    this.logOutput.removeChild(this.logOutput.firstChild);
                }
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new MonitoringDashboard();
        });
    </script>
</body>
</html>
        """

def setup_monitoring_dashboard(app: FastAPI) -> MonitoringDashboard:
    """Setup monitoring dashboard with the FastAPI app"""
    return MonitoringDashboard(app)