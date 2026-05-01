# Precision and Data Format

## Format Choice

Samples are signed 16-bit integer (INT16). Standard audio PCM at 16 kHz is INT16 by default: codecs, USB audio class devices, and ADCs all output it directly. It covers 96 dB of dynamic range, which is the full range of a standard audio codec. INT8 drops that to 48 dB and adds quantization noise that hurts detection under low-SNR conditions. FP32 doubles the accumulator memory with no real benefit, because the input is already quantized to 16-bit precision before it reaches the chip.

Accumulators are 40-bit signed (ACCW=40). Each product of two INT16 values is at most 32767² ≈ 1.07 × 10⁹, which fits in 30 bits. Summing 128 of them gives at most 1.37 × 10¹¹, which needs 37 bits. 40 bits adds 3 bits of headroom and aligns to a 5-byte boundary. A 32-bit accumulator overflows on large-amplitude correlated inputs.

## Normalization

Full normalized cross-correlation divides by sqrt(ref_energy × mic_energy). This module skips that step. The comparison is acc_cross ≥ threshold, where threshold is set by the caller in accumulated units.

Hardware square-root costs significant area and adds pipeline stages. The goal at M2 is to verify the accumulation is correct. A Newton-Raphson or CORDIC sqrt unit fits into the M3 synthesis pass once the core is stable.

The practical consequence: threshold must be calibrated to signal amplitude. For constant-amplitude signals (as used in the testbench) this is exact. For variable-amplitude audio, the threshold needs tuning per session. That is acceptable here because real-time echo detection operates on roughly stationary signal statistics over a 128-sample window at 16 kHz (8 ms per window).

## Error Analysis

Reference: Python float64 accumulation of Σ ref[i] × mic[i] for 128 samples.

Test 1 (ref=1, mic=1): float64 = 128.0, DUT = 128. Error = 0.

Test 2 (ref=1, mic=-1): float64 = -128.0, DUT = -128. Error = 0.

For a broader check: 100 random 128-sample windows with INT16 values drawn from [-1000, 1000] show max absolute error of 0 between float64 and INT16 accumulation. Integer multiply-accumulate over a 40-bit register is exact for inputs in this range. No rounding occurs because no division or sqrt runs in this module.

## Acceptability

The cross-correlation numerator computed in INT16 fixed-point is mathematically exact for integer inputs. Precision loss relative to float only enters at normalization, which is deferred to M3. For all M2 test vectors, DUT output matches the Python float64 reference to within 0 LSB.
