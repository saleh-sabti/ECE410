# Interface Selection
ECE 410/510 Spring 2026 | Saleh Sabti  
Project: Echo Detection Chiplet

---

## Selected Interface: AXI4 Stream

---

## Host Platform

FPGA SoC (e.g., Xilinx Zynq or similar) acting as audio front-end and host controller. The chiplet sits as a co-processor on the same PCB, receiving streaming audio samples and returning 1-bit detection results.

---

## Bandwidth Requirement

Audio input: 2 channels (far-end reference + near-end mic) × 16,000 samples/s × 16 bits/sample

Required bandwidth = 2 × 16,000 × 16 / 8 = **64,000 bytes/s = 0.064 MB/s**

Output: 1 bit per window × (16,000 / 128) windows/s = 125 bits/s ≈ negligible

**Total required interface bandwidth: ~0.064 MB/s**

---

## Interface Bandwidth Comparison

| Interface | Typical bandwidth | Margin over requirement |
|-----------|------------------|------------------------|
| I2C (Fast mode) | 0.05 MB/s | borderline, risky |
| SPI (10 MHz, 8-bit) | 1.25 MB/s | 20× |
| **AXI4 Stream (100 MHz, 32-bit)** | **400 MB/s** | **6,250×** |
| AXI4-Lite | ~100 MB/s | control-plane only, no streaming |
| PCIe Gen3 x1 | ~985 MB/s | overkill for audio |

---

## Bottleneck Analysis

Required bandwidth / AXI4 Stream bandwidth = 0.064 / 400 = **0.016% utilization**

The chiplet is not interface-bound. The interface has orders of magnitude more capacity than the audio data rate. On-chip compute and memory dominate; the interface is idle at this data rate.

---

## Justification

AXI4 Stream fits for three reasons. Audio is a continuous fixed-rate stream; AXI4 Stream has no address phase, and the TVALID/TREADY handshake maps directly to the sample-by-sample shift register input. Zynq and similar SoCs expose AXI4 Stream natively, so no custom glue logic on the host side. At 0.064 MB/s required versus 400 MB/s available, protocol overhead is irrelevant.

I2C Fast mode (0.05 MB/s) is borderline for two-channel 16-bit audio. SPI works on bandwidth but has no native backpressure. AXI4-Lite is control-plane only with no streaming semantics. PCIe adds die area and power that an audio chiplet does not need.
