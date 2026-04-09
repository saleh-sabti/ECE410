# Software Baseline Benchmark
ECE 410/510 Spring 2026 | Saleh Sabti  
Project: Echo Detection Chiplet

---

## Platform

| Field | Value |
|-------|-------|
| CPU | Intel Core Ultra 7 155H (Meteor Lake, 6P+8E cores) |
| OS | Ubuntu 22.04 (WSL2 on Windows 11) |
| Python | 3.12.3 |
| Script | `project/echo_detect.py` |
| Input | Synthetic signals, 2.0 s @ 16 kHz = 32,000 samples |
| Window size | N = 128 samples (8 ms) |
| Batch size | N/A — streaming, one window at a time |

---

## Execution Time

Wall-clock time measured with `time.perf_counter()` around `run_streaming()` only (excludes one-time signal generation). 10 runs, same fixed seed.

| Run | Wall time (ms) |
|-----|----------------|
| 1 | 247 |
| 2 | 249 |
| 3 | 256 |
| 4 | 257 |
| 5 | 258 |
| 6 | 261 |
| 7 | 263 |
| 8 | 269 |
| 9 | 274 |
| 10 | 285 |

**Median wall-clock: 260 ms** (runs 5+6 average)  
Min: 247 ms

---

## Throughput

- Windows processed: 31,872 (one per sample after initial N-sample fill)
- Throughput: 31,872 / 0.260 = **122,585 windows/s**
- Audio real-time factor: 2.0 s audio / 0.260 s wall = **7.7× real-time** (software only, no I/O)
- FLOP throughput: 24,477,696 FLOP / 0.260 s = **94.1 MFLOP/s**

---

## Memory Usage

Peak RSS: **16.8 MB** (measured via `resource.getrusage`)

Breakdown (estimated):
- `reference` list: 32,000 floats × 8 B = 256 KB
- `mic` list: 32,000 floats × 8 B = 256 KB
- `decisions` list: 31,872 tuples × ~56 B = ~1.8 MB
- Python interpreter overhead: ~14 MB
