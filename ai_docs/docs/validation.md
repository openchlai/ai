# Validation Guide: Latency Measurement for Transcription

## Purpose

The `validation/log_latency.py` script measures **latency (response time)** to validate the performance of the transcription system.
Goal: Verify that requests are processed **in less than 5 seconds**.

---

## Prerequisites

- Python 3.8 or higher
- Recommended: `requests` package (for file uploads)
  ```powershell
  python -m pip install requests
  ```

---

## Quick Start

### 1. Dry-Run (Local Simulation Without Network)

Test script functionality and generate CSV without a server:
```powershell
python .\validation\log_latency.py --dry-run --count 5
```

Output:
```
OK  synthetic_input_1.txt  0.123s
OK  synthetic_input_2.txt  0.087s
OK  synthetic_input_3.txt  0.215s
OK  synthetic_input_4.txt  0.156s
OK  synthetic_input_5.txt  0.095s
Wrote 5 samples to reports/latency_samples.csv
```

View the generated CSV:
```powershell
type .\reports\latency_samples.csv
```

### 2. Run With Live Transcription Server

When a transcription server is running on `http://localhost:8000/transcribe`:
```powershell
python .\validation\log_latency.py --count 5
```

### 3. Specify Custom Server Endpoint

For a server running on a different port/path:
```powershell
python .\validation\log_latency.py --server http://localhost:9000/my-transcribe --count 8
```

---

## Advanced Options

### Complete Command-Line Reference

```
usage: log_latency.py [-h] [--server SERVER] [--inputs INPUTS [INPUTS ...]]
                      [--input-dir INPUT_DIR] [--count COUNT]
                      [--output OUTPUT] [--timeout TIMEOUT] [--dry-run]

Log latency for transcription requests

options:
  -h, --help                Show help message and exit
  --server SERVER, -s SERVER
                           Server endpoint (default: http://localhost:8000/transcribe)
  --inputs INPUTS, -i INPUTS
                           Input file paths (list of audio files)
  --input-dir INPUT_DIR, -d INPUT_DIR
                           Input directory (auto-discovers audio files)
  --count COUNT, -n COUNT  Number of synthetic inputs to generate (default: 5)
  --output OUTPUT, -o OUTPUT
                           CSV output path (default: reports/latency_samples.csv)
  --timeout TIMEOUT        Request timeout in seconds (default: 30.0)
  --dry-run                Simulate requests locally without network
```

### Test With Real Audio Files

If your directory contains .wav, .mp3, .flac, or other audio files:
```powershell
python .\validation\log_latency.py --input-dir .\audio_samples --count 10 --output .\reports\actual_latency.csv
```

### Adjust Timeout (For Slower Servers)

Increase timeout if the default 30 seconds is too short:
```powershell
python .\validation\log_latency.py --timeout 60 --count 5
```

---

## Output File

CSV file: `reports/latency_samples.csv`

**Columns:**
- `input_file`: Input file name
- `latency_seconds`: Response time in seconds (6 decimal places)

**Example:**
```csv
input_file,latency_seconds
synthetic_input_1.txt,0.123456
synthetic_input_2.txt,0.087123
synthetic_input_3.txt,0.215678
```

---

## Interpreting Results

| Latency | Status | Action |
|---------|--------|--------|
| < 2s | ✅ Excellent | No action needed |
| 2-5s | ✅ Good | Target met |
| 5-10s | ⚠️ Warning | Investigate performance degradation |
| > 10s | ❌ Poor | Analyze bottlenecks |

**Python Script to Analyze CSV:**
```python
import csv
import statistics

latencies = []
with open('reports/latency_samples.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        latencies.append(float(row['latency_seconds']))

print(f"Mean: {statistics.mean(latencies):.3f}s")
print(f"Median: {statistics.median(latencies):.3f}s")
print(f"Max: {max(latencies):.3f}s")
print(f"Min: {min(latencies):.3f}s")
```

---

## Troubleshooting

### Connection Refused Error

**Symptom:** `WinError 10061 - Connection refused by target computer`

**Solution:**
1. Verify the transcription server is running
2. Check the port number (default: 8000)
3. Explicitly specify the server URL:
   ```powershell
   python .\validation\log_latency.py --server http://localhost:9000/transcribe
   ```

### Testing With a Mock Server

If you don't have a server, run a simple Flask mock server (in a separate terminal):
```powershell
python -m pip install flask

@'
from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/transcribe', methods=['POST'])
def transcribe():
    return jsonify({'text': 'ok'})
if __name__ == '__main__':
    app.run(port=8000)
'@ > mock_server.py

python .\mock_server.py
```

Then in the original terminal:
```powershell
python .\validation\log_latency.py --count 5
```

### Using Dry-Run Mode

Test quickly without a real server:
```powershell
python .\validation\log_latency.py --dry-run --count 5
```

---

## References

- Python `time` module: https://docs.python.org/3/library/time.html
- Python `csv` module: https://docs.python.org/3/library/csv.html
- `requests` library: https://requests.readthedocs.io/

---

## Next Steps

1. **Initial Run**: Test with `--dry-run` first, then with your live server
2. **Analyze Results**: Review latency data in the CSV file
3. **Optimize Performance**: If needed, optimize your server based on results
4. **Automate**: Integrate into your CI/CD pipeline (e.g., GitHub Actions)
