#!/usr/bin/env python3
"""
Simple Resource Monitoring Script for Local Development
Monitors CPU, Memory, GPU, and API metrics without requiring Prometheus/Grafana
"""

import psutil
import time
import argparse
import sys
import os
from datetime import datetime
import requests
from typing import Optional

# Try to import GPU monitoring
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  GPUtil not installed. GPU monitoring disabled.")
    print("   Install with: pip install gputil")

class ResourceMonitor:
    def __init__(self, interval: int = 5, output_file: Optional[str] = None, api_url: str = "http://localhost:8125"):
        self.interval = interval
        self.output_file = output_file
        self.api_url = api_url
        self.start_time = datetime.now()
        
        if self.output_file:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file) if os.path.dirname(self.output_file) else 'logs', exist_ok=True)
            with open(self.output_file, 'w') as f:
                f.write(f"# Resource Monitoring Started: {self.start_time}\n")
                f.write(f"# Interval: {self.interval} seconds\n")
                f.write(f"# API URL: {self.api_url}\n")
                f.write("=" * 80 + "\n\n")
    
    def get_cpu_info(self):
        """Get CPU usage information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        
        return {
            'percent': cpu_percent,
            'count': cpu_count,
            'frequency': cpu_freq.current if cpu_freq else 0,
            'load_1min': load_avg[0],
            'load_5min': load_avg[1],
            'load_15min': load_avg[2]
        }
    
    def get_memory_info(self):
        """Get memory usage information"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': mem.total / (1024**3),
            'used_gb': mem.used / (1024**3),
            'available_gb': mem.available / (1024**3),
            'percent': mem.percent,
            'swap_percent': swap.percent
        }
    
    def get_gpu_info(self):
        """Get GPU usage information (if available)"""
        if not GPU_AVAILABLE:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None
            
            gpu_info = []
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load_percent': gpu.load * 100,
                    'memory_used_mb': gpu.memoryUsed,
                    'memory_total_mb': gpu.memoryTotal,
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal > 0 else 0,
                    'temperature': gpu.temperature
                })
            return gpu_info
        except Exception as e:
            return None
    
    def get_disk_info(self):
        """Get disk usage information"""
        disk = psutil.disk_usage('/')
        
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent
        }
    
    def get_api_metrics(self):
        """Get metrics from FastAPI /metrics endpoint"""
        try:
            response = requests.get(f"{self.api_url}/metrics", timeout=2)
            if response.status_code == 200:
                metrics_text = response.text
                
                # Parse key metrics
                metrics = {}
                
                # Request count
                for line in metrics_text.split('\n'):
                    if 'api_requests_total' in line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['total_requests'] = float(parts[-1])
                            break
                
                # Queue length
                for line in metrics_text.split('\n'):
                    if 'celery_queue_length' in line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            metrics['queue_length'] = float(parts[-1])
                            break
                
                return metrics
        except Exception as e:
            return {'error': str(e)}
    
    def format_output(self, cpu, memory, gpu, disk, api_metrics):
        """Format monitoring data for display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = datetime.now() - self.start_time
        
        output = []
        output.append("=" * 80)
        output.append(f"⏰ {timestamp} | Uptime: {uptime}")
        output.append("=" * 80)
        
        # CPU
        output.append(f"\n💻 CPU:")
        output.append(f"   Usage: {cpu['percent']:.1f}% | Cores: {cpu['count']} | Freq: {cpu['frequency']:.0f} MHz")
        output.append(f"   Load: {cpu['load_1min']:.2f} (1m) | {cpu['load_5min']:.2f} (5m) | {cpu['load_15min']:.2f} (15m)")
        
        # Memory
        output.append(f"\n🧠 Memory:")
        output.append(f"   Used: {memory['used_gb']:.2f} GB / {memory['total_gb']:.2f} GB ({memory['percent']:.1f}%)")
        output.append(f"   Available: {memory['available_gb']:.2f} GB | Swap: {memory['swap_percent']:.1f}%")
        
        # GPU
        if gpu:
            output.append(f"\n🎮 GPU:")
            for g in gpu:
                output.append(f"   GPU {g['id']} ({g['name']}):")
                output.append(f"      Load: {g['load_percent']:.1f}% | Temp: {g['temperature']}°C")
                output.append(f"      Memory: {g['memory_used_mb']:.0f} MB / {g['memory_total_mb']:.0f} MB ({g['memory_percent']:.1f}%)")
        else:
            output.append(f"\n🎮 GPU: Not available")
        
        # Disk
        output.append(f"\n💾 Disk:")
        output.append(f"   Used: {disk['used_gb']:.2f} GB / {disk['total_gb']:.2f} GB ({disk['percent']:.1f}%)")
        output.append(f"   Free: {disk['free_gb']:.2f} GB")
        
        # API Metrics
        if api_metrics and 'error' not in api_metrics:
            output.append(f"\n📊 API Metrics:")
            if 'total_requests' in api_metrics:
                output.append(f"   Total Requests: {api_metrics['total_requests']:.0f}")
            if 'queue_length' in api_metrics:
                output.append(f"   Queue Length: {api_metrics['queue_length']:.0f}")
        elif api_metrics and 'error' in api_metrics:
            output.append(f"\n📊 API Metrics: ❌ {api_metrics['error']}")
        else:
            output.append(f"\n📊 API Metrics: Not available")
        
        output.append("\n")
        
        return "\n".join(output)
    
    def log_to_file(self, output: str):
        """Write output to log file"""
        if self.output_file:
            with open(self.output_file, 'a') as f:
                f.write(output)
    
    def run(self):
        """Main monitoring loop"""
        print(f"🎯 Starting Resource Monitor")
        print(f"   Interval: {self.interval} seconds")
        print(f"   API URL: {self.api_url}")
        if self.output_file:
            print(f"   Logging to: {self.output_file}")
        print(f"\n   Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Collect metrics
                cpu = self.get_cpu_info()
                memory = self.get_memory_info()
                gpu = self.get_gpu_info()
                disk = self.get_disk_info()
                api_metrics = self.get_api_metrics()
                
                # Format output
                output = self.format_output(cpu, memory, gpu, disk, api_metrics)
                
                # Display
                print(output)
                
                # Log to file
                self.log_to_file(output)
                
                # Wait
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")
            if self.output_file:
                print(f"   Log saved to: {self.output_file}")


def main():
    parser = argparse.ArgumentParser(description='Monitor system resources and API metrics')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds (default: 5)')
    parser.add_argument('--output', type=str, help='Output log file path (optional)')
    parser.add_argument('--api-url', type=str, default='http://localhost:8125', help='API base URL (default: http://localhost:8125)')
    
    args = parser.parse_args()
    
    monitor = ResourceMonitor(
        interval=args.interval,
        output_file=args.output,
        api_url=args.api_url
    )
    
    monitor.run()


if __name__ == '__main__':
    main()
