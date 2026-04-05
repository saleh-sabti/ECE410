# echo_detect.py
# Normalized cross-correlation echo detector — pure Python reference
# ECE 410/510 Spring 2026 | Saleh Sabti

import math
import random
import time

# ── Parameters ────────────────────────────────────────────────────────────────
SAMPLE_RATE  = 16000   # samples per second
DURATION_S   = 2.0     # seconds of audio to process
N            = 128     # window size in samples (8 ms at 16 kHz)
ECHO_DELAY   = 320     # how many samples behind the echo arrives (~20 ms)
ECHO_GAIN    = 0.5     # how loud the echo is relative to the original
NOISE_LEVEL  = 0.05    # background noise level
THRESHOLD    = 0.7     # correlation score above this = echo detected


# ── Signal generation ─────────────────────────────────────────────────────────

def generate_reference(n_samples):
    random.seed(42)
    sig = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        s = (math.sin(2 * math.pi * 200 * t) * 0.5 +
             math.sin(2 * math.pi * 440 * t) * 0.3 +
             math.sin(2 * math.pi * 800 * t) * 0.2 +
             random.uniform(-0.05, 0.05))
        sig.append(s)
    return sig


def generate_mic(reference):
    random.seed(7)
    mic = []
    for i in range(len(reference)):
        direct = reference[i]
        echo   = ECHO_GAIN * reference[i - ECHO_DELAY] if i >= ECHO_DELAY else 0.0
        noise  = random.uniform(-NOISE_LEVEL, NOISE_LEVEL)
        mic.append(direct + echo + noise)
    return mic


# ── Core algorithm ────────────────────────────────────────────────────────────

def normalized_xcorr(ref_win, mic_win):
    # 3 accumulators, each runs N MACs — total 3*N MACs per call
    dot        = 0.0
    energy_ref = 0.0
    energy_mic = 0.0

    for r, m in zip(ref_win, mic_win):
        dot        += r * m
        energy_ref += r * r
        energy_mic += m * m

    denom = math.sqrt(energy_ref * energy_mic)
    if denom < 1e-10:
        return 0.0
    return dot / denom


# ── Streaming loop ────────────────────────────────────────────────────────────

def run_streaming(reference, mic):
    decisions = []
    mac_count = 0

    for i in range(N, len(reference)):
        ref_win = reference[i - N : i]
        mic_win = mic[i - N : i]

        corr      = normalized_xcorr(ref_win, mic_win)
        mac_count += 3 * N

        decision = 1 if corr >= THRESHOLD else 0
        decisions.append((i, corr, decision))

    return decisions, mac_count


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    n_samples = int(SAMPLE_RATE * DURATION_S)

    print(f"Signal: {DURATION_S}s @ {SAMPLE_RATE} Hz = {n_samples} samples")
    print(f"Window: N={N} ({1000*N/SAMPLE_RATE:.1f} ms)  |  "
          f"Echo delay: {ECHO_DELAY} samples ({1000*ECHO_DELAY/SAMPLE_RATE:.1f} ms)")
    print()

    reference = generate_reference(n_samples)
    mic       = generate_mic(reference)

    t0 = time.perf_counter()
    decisions, mac_count = run_streaming(reference, mic)
    t1 = time.perf_counter()

    elapsed     = t1 - t0
    n_windows   = len(decisions)
    echo_frames = sum(1 for _, _, d in decisions if d == 1)

    print(f"── Detection results ────────────────────────────────────────────")
    print(f"  Windows processed   : {n_windows:,}")
    print(f"  Echo detected       : {echo_frames:,}  ({100*echo_frames/n_windows:.1f}%)")
    print(f"  No echo             : {n_windows - echo_frames:,}  ({100*(n_windows-echo_frames)/n_windows:.1f}%)")

    print(f"\n── Performance ──────────────────────────────────────────────────")
    print(f"  Total MACs          : {mac_count:,}")
    print(f"  MACs per window     : {3 * N}  (3 × N={N})")
    print(f"  Wall time           : {elapsed*1000:.2f} ms")
    print(f"  Throughput          : {mac_count / elapsed / 1e6:.2f} MMAC/s")

    bytes_per_window = (2 * N + 1) * 4
    total_bytes      = n_windows * bytes_per_window
    flops            = mac_count * 2
    arith_intensity  = flops / total_bytes

    print(f"\n── Roofline inputs ──────────────────────────────────────────────")
    print(f"  FLOPs               : {flops:,}")
    print(f"  Memory traffic      : {total_bytes / 1024:.1f} KB")
    print(f"  Arithmetic intensity: {arith_intensity:.3f} FLOP/byte")


if __name__ == "__main__":
    main()
