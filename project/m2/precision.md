# Precision and Data Format

## Format Choice

Samples use signed 16-bit integer (INT16, Q0.15 convention). Audio PCM at 16 kHz is universally represented in INT16: it covers the full dynamic range of standard codecs (96 dB SNR), and every audio ADC, codec chip, and USB audio class device natively produces this format. Using a narrower format like INT8 would lose 48 dB of dynamic range and introduce quantization noise that degrades echo detection under low-SNR conditions. Using FP32 would cost 2× the accumulator memory with no benefit because the input data is inherently discrete at 16-bit precision.

Internal arithmetic uses 40-bit signed accumulators (ACCW=40). The cross-correlation sum accumulates N=128 products of 16-bit values. Each product is at most 32767² ≈ 1.07 × 10⁹, which fits in 30 bits unsigned. Summing 128 such values gives at most 128 × 1.07 × 10⁹ ≈ 1.37 × 10¹¹, which requires 37 bits. The 40-bit accumulator provides 3 bits of headroom and aligns well to a 5-byte boundary. A 32-bit accumulator would overflow on large-amplitude correlated inputs.

## Normalization Deferral

Full normalized cross-correlation divides by sqrt(ref_energy × mic_energy). This is omitted in the M2 RTL. The comparison is instead: acc_cross ≥ threshold, where threshold is set by the user in accumulated units.

The deferral is intentional. A hardware square-root unit costs significant area and adds multiple pipeline stages. For M2, correctness of the correlation accumulation is the verification goal. The normalization step can be implemented as a sequential Newton-Raphson or CORDIC approximation in M3 once the core accumulation is verified correct.

The practical consequence is that the threshold must be set relative to signal amplitude. For constant-amplitude test signals (as used in the testbench), this is exact. For variable-amplitude audio, the detection threshold would need to be tuned per session, which is acceptable for the use case (real-time echo detection where signal statistics are roughly stationary over a window).

## Error Analysis

Reference: Python float64 computation of acc_cross = Σ ref[i] × mic[i] for 128 samples.

Test 1 (all-ones): float64 result = 128.0; INT16 DUT result = 128. Absolute error = 0.

Test 2 (ref=1, mic=-1): float64 result = -128.0; INT16 DUT result = -128. Absolute error = 0.

For both test cases the INT16 arithmetic is exact because the values (1, -1) have no fractional part and the accumulator sum is well within 40-bit range.

For a broader check: the Python software baseline (`project/echo_detect.py`) runs normalized cross-correlation in float64. The cross-correlation numerator on 100 randomly sampled 128-sample windows of INT16 audio (values drawn uniformly from [-1000, 1000]) shows max absolute error between float64 and INT16 accumulation of 0. This is expected: the sum of 128 products of 16-bit integers is exact in integer arithmetic up to 40 bits. There is no rounding error because no division or sqrt is performed in this module.

## Acceptability Statement

Error is acceptable because the cross-correlation numerator computed in INT16 fixed-point is mathematically exact for the integer inputs. The only precision loss relative to a float reference occurs at normalization, which is explicitly deferred to M3. For the M2 testbench inputs, DUT output matches the Python float64 reference to within 0 LSB.
