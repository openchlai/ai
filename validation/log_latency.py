#!/usr/bin/env python3
"""
Simple latency logger for transcription requests.

Usage examples are in `docs/validation.md`.

This script will send a series of requests to a transcription endpoint and
record round-trip latency into a CSV file at `reports/latency_samples.csv` by default.

Features:
- Sends either file uploads (if `requests` is installed) or JSON placeholders.
- Measures using `time.perf_counter()` for high-resolution timing.
- Writes CSV with columns: input_file,latency_seconds
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from typing import List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Log latency for transcription requests")
    p.add_argument("--server", "-s", default="http://localhost:8000/transcribe",
                   help="Transcription endpoint URL (default: http://localhost:8000/transcribe)")
    p.add_argument("--inputs", "-i", nargs="*",
                   help="List of input files to send (audio files). If omitted, synthetic text inputs are used.")
    p.add_argument("--input-dir", "-d",
                   help="Directory containing input files (will glob common audio extensions)")
    p.add_argument("--count", "-n", type=int, default=5,
                   help="Number of requests to send when generating synthetic inputs (default: 5)")
    p.add_argument("--output", "-o", default="reports/latency_samples.csv",
                   help="CSV output path (default: reports/latency_samples.csv)")
    p.add_argument("--timeout", type=float, default=30.0,
                   help="Per-request timeout in seconds (used for requests library)")
    p.add_argument("--dry-run", action="store_true",
                   help="Simulate requests locally (no network) and sleep random small durations)")
    return p.parse_args()


def find_audio_files(directory: str) -> List[str]:
    exts = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
    results: List[str] = []
    for root, _, files in os.walk(directory):
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                results.append(os.path.join(root, f))
    return sorted(results)


def ensure_reports_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def send_request_requests(server: str, input_path: str, timeout: float) -> None:
    """This is a placeholder to show where requests-based upload logic would be used.
    The actual sending is implemented inline in the main function to avoid import-time failures.
    """
    raise NotImplementedError


def main() -> int:
    args = parse_args()

    inputs: List[str] = []
    if args.inputs:
        inputs = list(args.inputs)
    elif args.input_dir:
        inputs = find_audio_files(args.input_dir)
    else:
        # synthetic placeholder inputs
        inputs = [f"synthetic_input_{i+1}.txt" for i in range(max(1, args.count))]

    if len(inputs) == 0:
        print("No input files found and no inputs provided. Use --input-dir or --inputs, or omit to use synthetic inputs.")
        return 2

    # Try to import requests; if it's unavailable, we'll fallback to JSON POSTs using urllib
    use_requests = False
    try:
        import requests  # type: ignore

        use_requests = True
    except Exception:
        use_requests = False

    results = []
    ensure_reports_dir(args.output)
    import random

    # Run requests and ensure we always capture results and write CSV even on unexpected errors
    try:
        for inp in inputs[: max(1, args.count)]:
            input_label = inp
            start = time.perf_counter()
            latency = None
            try:
                if args.dry_run:
                    # simulate work
                    t = random.uniform(0.05, 0.5)
                    time.sleep(t)
                else:
                    if os.path.exists(inp) and use_requests:
                        import requests  # type: ignore

                        with open(inp, "rb") as f:
                            files = {"file": (os.path.basename(inp), f, "application/octet-stream")}
                            resp = requests.post(args.server, files=files, timeout=args.timeout)
                            resp.raise_for_status()
                    elif os.path.exists(inp) and not use_requests:
                        # No requests lib; send a small JSON indicating a filename (server must support it)
                        import urllib.request
                        import urllib.error

                        payload = json.dumps({"input_file": os.path.basename(inp)}).encode("utf-8")
                        req = urllib.request.Request(args.server, data=payload, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                            _ = resp.read()
                    else:
                        # synthetic input: send JSON with a small text payload
                        if use_requests:
                            import requests  # type: ignore

                            payload = {"text": f"sample transcription request for {inp}"}
                            resp = requests.post(args.server, json=payload, timeout=args.timeout)
                            resp.raise_for_status()
                        else:
                            import urllib.request
                            import urllib.error

                            payload = json.dumps({"text": f"sample transcription request for {inp}"}).encode("utf-8")
                            req = urllib.request.Request(args.server, data=payload, headers={"Content-Type": "application/json"})
                            with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                                _ = resp.read()

                end = time.perf_counter()
                latency = end - start
                print(f"OK  {input_label}  {latency:.3f}s")
            except Exception as e:
                end = time.perf_counter()
                # record latency even on error as the elapsed time until failure
                latency = end - start
                print(f"ERR {input_label}  {latency:.3f}s  ({e})")

            results.append({"input_file": input_label, "latency_seconds": f"{latency:.6f}"})
    except Exception as global_e:
        # Catch any unexpected error during the loop to ensure CSV writing below
        print(f"FATAL: unexpected error during requests loop: {global_e}", file=sys.stderr)

    # write CSV (always attempt to write results)
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["input_file", "latency_seconds"])
            for r in results:
                writer.writerow([r["input_file"], r["latency_seconds"]])
        print(f"Wrote {len(results)} samples to {args.output}")
    except Exception as write_e:
        print(f"ERROR: failed to write CSV {args.output}: {write_e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
