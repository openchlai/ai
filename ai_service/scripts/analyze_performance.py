#!/usr/bin/env python3
"""
Performance Analysis Script for AI Service
Analyzes load test results, resource logs, and identifies bottlenecks

Usage:
    python scripts/analyze_performance.py --locust-stats reports/locust_stats.csv --resource-log logs/resources.log
    python scripts/analyze_performance.py --test-dir reports/load_test_20250125_120000
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics


class PerformanceAnalyzer:
    """Analyzes load test and resource monitoring data"""

    def __init__(self, locust_stats_file: Optional[str] = None,
                 resource_log_file: Optional[str] = None,
                 test_directory: Optional[str] = None):
        self.locust_stats_file = locust_stats_file
        self.resource_log_file = resource_log_file
        self.test_directory = test_directory

        # Data storage
        self.locust_data = []
        self.resource_data = []
        self.analysis_results = {}

        # If test directory provided, find files automatically
        if test_directory:
            self._find_test_files(test_directory)

    def _find_test_files(self, test_dir: str):
        """Find locust stats and resource log files in test directory"""
        test_path = Path(test_dir)
        if not test_path.exists():
            print(f"❌ Test directory not found: {test_dir}")
            return

        # Find CSV files (Locust stats)
        csv_files = list(test_path.glob("*stats.csv"))
        if csv_files:
            self.locust_stats_file = str(csv_files[0])
            print(f"📊 Found Locust stats: {self.locust_stats_file}")

        # Find log files (resource monitoring)
        log_files = list(test_path.glob("*resources*.log"))
        if log_files:
            self.resource_log_file = str(log_files[0])
            print(f"📈 Found resource log: {self.resource_log_file}")

    def parse_locust_stats(self) -> bool:
        """Parse Locust CSV statistics file"""
        if not self.locust_stats_file or not os.path.exists(self.locust_stats_file):
            print(f"⚠️  Locust stats file not found: {self.locust_stats_file}")
            return False

        try:
            with open(self.locust_stats_file, 'r') as f:
                reader = csv.DictReader(f)
                self.locust_data = list(reader)

            print(f"✅ Parsed {len(self.locust_data)} Locust records")
            return True
        except Exception as e:
            print(f"❌ Error parsing Locust stats: {e}")
            return False

    def parse_resource_log(self) -> bool:
        """Parse resource monitoring log file"""
        if not self.resource_log_file or not os.path.exists(self.resource_log_file):
            print(f"⚠️  Resource log file not found: {self.resource_log_file}")
            return False

        try:
            with open(self.resource_log_file, 'r') as f:
                lines = f.readlines()

            # Parse resource metrics from log
            for line in lines:
                if "CPU:" in line:
                    # Parse CPU usage
                    match = re.search(r'CPU: ([\d.]+)%', line)
                    if match:
                        cpu = float(match.group(1))
                        self.resource_data.append({
                            'type': 'cpu',
                            'value': cpu,
                            'line': line.strip()
                        })

                if "GPU" in line and "Load:" in line:
                    # Parse GPU usage
                    match = re.search(r'Load: ([\d.]+)%', line)
                    if match:
                        gpu = float(match.group(1))
                        self.resource_data.append({
                            'type': 'gpu',
                            'value': gpu,
                            'line': line.strip()
                        })

                if "Memory:" in line:
                    # Parse memory usage
                    match = re.search(r'Memory: ([\d.]+) GB / ([\d.]+) GB \(([\d.]+)%\)', line)
                    if match:
                        mem_used = float(match.group(1))
                        mem_total = float(match.group(2))
                        mem_percent = float(match.group(3))
                        self.resource_data.append({
                            'type': 'memory',
                            'value': mem_percent,
                            'used': mem_used,
                            'total': mem_total,
                            'line': line.strip()
                        })

                if "Queue Length:" in line:
                    # Parse queue length
                    match = re.search(r'Queue Length: (\d+)', line)
                    if match:
                        queue_len = int(match.group(1))
                        self.resource_data.append({
                            'type': 'queue',
                            'value': queue_len,
                            'line': line.strip()
                        })

            print(f"✅ Parsed {len(self.resource_data)} resource measurements")
            return True
        except Exception as e:
            print(f"❌ Error parsing resource log: {e}")
            return False

    def analyze_locust_data(self):
        """Analyze Locust test results"""
        if not self.locust_data:
            return

        print("\n" + "="*60)
        print("📊 LOCUST TEST RESULTS ANALYSIS")
        print("="*60 + "\n")

        # Find aggregated row
        aggregated = None
        endpoints = []

        for row in self.locust_data:
            if row.get('Name') == 'Aggregated':
                aggregated = row
            else:
                endpoints.append(row)

        # Overall statistics
        if aggregated:
            print("📈 Overall Statistics:")
            print(f"  Total Requests:     {aggregated.get('Request Count', 'N/A')}")
            print(f"  Total Failures:     {aggregated.get('Failure Count', 'N/A')}")
            print(f"  Avg Response Time:  {aggregated.get('Average Response Time', 'N/A')} ms")
            print(f"  Min Response Time:  {aggregated.get('Min Response Time', 'N/A')} ms")
            print(f"  Max Response Time:  {aggregated.get('Max Response Time', 'N/A')} ms")
            print(f"  Requests/sec:       {aggregated.get('Requests/s', 'N/A')}")

            # Calculate error rate
            try:
                total_req = int(aggregated.get('Request Count', 0))
                failures = int(aggregated.get('Failure Count', 0))
                error_rate = (failures / total_req * 100) if total_req > 0 else 0
                print(f"  Error Rate:         {error_rate:.2f}%")

                self.analysis_results['overall'] = {
                    'total_requests': total_req,
                    'failures': failures,
                    'error_rate': error_rate,
                    'avg_response_time': float(aggregated.get('Average Response Time', 0)),
                    'requests_per_sec': float(aggregated.get('Requests/s', 0))
                }
            except (ValueError, TypeError):
                pass

        # Per-endpoint analysis
        if endpoints:
            print("\n📍 Per-Endpoint Analysis:")
            for endpoint in endpoints:
                name = endpoint.get('Name', 'Unknown')
                avg_time = endpoint.get('Average Response Time', 'N/A')
                p95 = endpoint.get('95%', 'N/A')
                p99 = endpoint.get('99%', 'N/A')
                rps = endpoint.get('Requests/s', 'N/A')

                print(f"\n  {name}:")
                print(f"    Avg Response: {avg_time} ms")
                print(f"    p95:          {p95} ms")
                print(f"    p99:          {p99} ms")
                print(f"    Requests/sec: {rps}")

        print()

    def analyze_resources(self):
        """Analyze resource utilization"""
        if not self.resource_data:
            return

        print("\n" + "="*60)
        print("💻 RESOURCE UTILIZATION ANALYSIS")
        print("="*60 + "\n")

        # Group by resource type
        cpu_values = [r['value'] for r in self.resource_data if r['type'] == 'cpu']
        gpu_values = [r['value'] for r in self.resource_data if r['type'] == 'gpu']
        memory_values = [r['value'] for r in self.resource_data if r['type'] == 'memory']
        queue_values = [r['value'] for r in self.resource_data if r['type'] == 'queue']

        # CPU Analysis
        if cpu_values:
            print("🖥️  CPU Usage:")
            print(f"  Average:  {statistics.mean(cpu_values):.1f}%")
            print(f"  Peak:     {max(cpu_values):.1f}%")
            print(f"  Min:      {min(cpu_values):.1f}%")
            print(f"  Median:   {statistics.median(cpu_values):.1f}%")

            self.analysis_results['cpu'] = {
                'avg': statistics.mean(cpu_values),
                'peak': max(cpu_values),
                'min': min(cpu_values),
                'median': statistics.median(cpu_values)
            }

        # GPU Analysis
        if gpu_values:
            print("\n🎮 GPU Usage:")
            print(f"  Average:  {statistics.mean(gpu_values):.1f}%")
            print(f"  Peak:     {max(gpu_values):.1f}%")
            print(f"  Min:      {min(gpu_values):.1f}%")
            print(f"  Median:   {statistics.median(gpu_values):.1f}%")

            self.analysis_results['gpu'] = {
                'avg': statistics.mean(gpu_values),
                'peak': max(gpu_values),
                'min': min(gpu_values),
                'median': statistics.median(gpu_values)
            }

        # Memory Analysis
        if memory_values:
            print("\n🧠 Memory Usage:")
            print(f"  Average:  {statistics.mean(memory_values):.1f}%")
            print(f"  Peak:     {max(memory_values):.1f}%")
            print(f"  Min:      {min(memory_values):.1f}%")
            print(f"  Median:   {statistics.median(memory_values):.1f}%")

            self.analysis_results['memory'] = {
                'avg': statistics.mean(memory_values),
                'peak': max(memory_values),
                'min': min(memory_values),
                'median': statistics.median(memory_values)
            }

        # Queue Analysis
        if queue_values:
            print("\n📊 Queue Length:")
            print(f"  Average:  {statistics.mean(queue_values):.0f}")
            print(f"  Peak:     {max(queue_values)}")
            print(f"  Min:      {min(queue_values)}")
            print(f"  Median:   {statistics.median(queue_values):.0f}")

            self.analysis_results['queue'] = {
                'avg': statistics.mean(queue_values),
                'peak': max(queue_values),
                'min': min(queue_values),
                'median': statistics.median(queue_values)
            }

        print()

    def identify_bottlenecks(self):
        """Identify performance bottlenecks"""
        print("\n" + "="*60)
        print("🔍 BOTTLENECK IDENTIFICATION")
        print("="*60 + "\n")

        bottlenecks = []

        # Check CPU bottleneck
        if 'cpu' in self.analysis_results:
            cpu_peak = self.analysis_results['cpu']['peak']
            cpu_avg = self.analysis_results['cpu']['avg']

            if cpu_peak > 90:
                bottlenecks.append({
                    'type': 'CPU',
                    'severity': 'HIGH',
                    'description': f'CPU usage peaked at {cpu_peak:.1f}%',
                    'recommendation': 'Consider optimizing CPU-intensive operations or adding more CPU resources'
                })
            elif cpu_avg > 80:
                bottlenecks.append({
                    'type': 'CPU',
                    'severity': 'MEDIUM',
                    'description': f'Average CPU usage is {cpu_avg:.1f}%',
                    'recommendation': 'CPU is consistently high. Monitor for sustained load.'
                })

        # Check GPU bottleneck
        if 'gpu' in self.analysis_results:
            gpu_peak = self.analysis_results['gpu']['peak']
            gpu_avg = self.analysis_results['gpu']['avg']

            if gpu_peak > 95:
                bottlenecks.append({
                    'type': 'GPU',
                    'severity': 'HIGH',
                    'description': f'GPU usage peaked at {gpu_peak:.1f}%',
                    'recommendation': 'GPU is fully utilized. Consider batch optimization or additional GPU resources.'
                })
            elif gpu_avg > 85:
                bottlenecks.append({
                    'type': 'GPU',
                    'severity': 'MEDIUM',
                    'description': f'Average GPU usage is {gpu_avg:.1f}%',
                    'recommendation': 'GPU is consistently high. Good utilization but may limit throughput.'
                })

        # Check Memory bottleneck
        if 'memory' in self.analysis_results:
            mem_peak = self.analysis_results['memory']['peak']
            mem_avg = self.analysis_results['memory']['avg']

            if mem_peak > 90:
                bottlenecks.append({
                    'type': 'Memory',
                    'severity': 'HIGH',
                    'description': f'Memory usage peaked at {mem_peak:.1f}%',
                    'recommendation': 'Risk of OOM errors. Add RAM or optimize memory usage.'
                })
            elif mem_avg > 80:
                bottlenecks.append({
                    'type': 'Memory',
                    'severity': 'MEDIUM',
                    'description': f'Average memory usage is {mem_avg:.1f}%',
                    'recommendation': 'Memory usage is high. Monitor for leaks or optimize caching.'
                })

        # Check Queue bottleneck
        if 'queue' in self.analysis_results:
            queue_peak = self.analysis_results['queue']['peak']
            queue_avg = self.analysis_results['queue']['avg']

            if queue_peak > 50:
                bottlenecks.append({
                    'type': 'Queue',
                    'severity': 'HIGH',
                    'description': f'Queue length peaked at {queue_peak}',
                    'recommendation': 'Workers cannot keep up with request rate. Add Celery workers.'
                })
            elif queue_avg > 20:
                bottlenecks.append({
                    'type': 'Queue',
                    'severity': 'MEDIUM',
                    'description': f'Average queue length is {queue_avg:.0f}',
                    'recommendation': 'Queue is building up. Consider adding workers or optimizing task processing.'
                })

        # Check error rate
        if 'overall' in self.analysis_results:
            error_rate = self.analysis_results['overall']['error_rate']

            if error_rate > 5:
                bottlenecks.append({
                    'type': 'Errors',
                    'severity': 'HIGH',
                    'description': f'Error rate is {error_rate:.2f}%',
                    'recommendation': 'High error rate indicates system instability. Check logs for causes.'
                })
            elif error_rate > 1:
                bottlenecks.append({
                    'type': 'Errors',
                    'severity': 'MEDIUM',
                    'description': f'Error rate is {error_rate:.2f}%',
                    'recommendation': 'Some errors occurring. Investigate error patterns.'
                })

        # Display bottlenecks
        if bottlenecks:
            for i, bottleneck in enumerate(bottlenecks, 1):
                severity_color = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                icon = severity_color.get(bottleneck['severity'], '⚪')

                print(f"{icon} Bottleneck #{i}: {bottleneck['type']} ({bottleneck['severity']})")
                print(f"   Description: {bottleneck['description']}")
                print(f"   Recommendation: {bottleneck['recommendation']}")
                print()
        else:
            print("✅ No significant bottlenecks identified!")
            print()

        self.analysis_results['bottlenecks'] = bottlenecks

    def generate_report(self, output_file: Optional[str] = None):
        """Generate performance report"""
        print("\n" + "="*60)
        print("📄 GENERATING PERFORMANCE REPORT")
        print("="*60 + "\n")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = {
            'timestamp': timestamp,
            'analysis': self.analysis_results
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved to: {output_file}")
        else:
            print(json.dumps(report, indent=2))

    def run(self, output_file: Optional[str] = None):
        """Run complete analysis"""
        print("\n🚀 Starting Performance Analysis...")
        print("="*60 + "\n")

        # Parse data
        locust_ok = self.parse_locust_stats()
        resource_ok = self.parse_resource_log()

        if not locust_ok and not resource_ok:
            print("❌ No data files found. Cannot perform analysis.")
            return False

        # Analyze
        if locust_ok:
            self.analyze_locust_data()

        if resource_ok:
            self.analyze_resources()

        # Identify bottlenecks
        self.identify_bottlenecks()

        # Generate report
        self.generate_report(output_file)

        print("\n✅ Analysis complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Analyze AI Service performance test results'
    )
    parser.add_argument(
        '--locust-stats',
        help='Path to Locust CSV statistics file'
    )
    parser.add_argument(
        '--resource-log',
        help='Path to resource monitoring log file'
    )
    parser.add_argument(
        '--test-dir',
        help='Path to test directory (will auto-find files)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON report file',
        default='performance_report.json'
    )

    args = parser.parse_args()

    # Create analyzer
    analyzer = PerformanceAnalyzer(
        locust_stats_file=args.locust_stats,
        resource_log_file=args.resource_log,
        test_directory=args.test_dir
    )

    # Run analysis
    analyzer.run(output_file=args.output)


if __name__ == '__main__':
    main()
