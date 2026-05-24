# CF8 CMAN: AER Bandwidth Analysis

**Parameters:** N = 1024 neurons, f = 50 Hz mean firing rate, 20 bits/packet

---

## Task 1: Mean Aggregate Spike Rate

R = N × f = 1024 × 50 = **51,200 spikes/s**

---

## Task 2: Mean AER Bandwidth

B = R × 20 bits/packet = 51,200 × 20 = 1,024,000 bits/s = **1.024 Mbit/s**

---

## Task 3: Interface Comparison

| Interface | Rated BW | Sustains 1.024 Mbit/s? |
|-----------|----------|------------------------|
| SPI | ≤50 Mbit/s | Y |
| I²C | ≤3.4 Mbit/s | Y |
| AXI4-Lite | ~100 Mbit/s | Y |

All three sustain the mean rate. **I²C is the lowest-complexity interface that suffices**: 1.024 Mbit/s is well within its 3.4 Mbit/s ceiling, and I²C only needs two wires with no dedicated clock line.

---

## Task 4: Burst Peak Bandwidth

25% of 1024 neurons fire within 1 ms: 0.25 × 1024 = 256 spikes in 1 ms.

Peak BW = (256 spikes × 20 bits) / 0.001 s = 5,120,000 bits/s = **5.12 Mbit/s**

Burst-to-mean ratio = 5.12 / 1.024 = **5.0×**

I²C peak rate (3.4 Mbit/s) < burst (5.12 Mbit/s): I²C **cannot absorb the burst** without buffering.

Buffering needed: during the 1 ms burst, I²C drains 3.4 Mbit/s × 0.001 s = 3,400 bits. Incoming = 5,120 bits. Excess = 1,720 bits → ceil(1720 / 20) = **86 packets**. A FIFO of at least 86 entries (20 bits each = ~1,720 bits) is sufficient.

---

## Task 5: Frame-Based Comparison

Frame-based: 1024 neurons × 1 bit/sample × 1000 samples/s = **1.024 Mbit/s**

AER/frame ratio at f = 50 Hz: 1.024 / 1.024 = **1.0** (exactly equal)

Crossover firing rate: set B_AER = B_frame

N × f_crossover × 20 = N × 1000  
f_crossover = 1000 / 20 = **50 Hz**

At f = 50 Hz the two approaches carry identical bandwidth, which is why the ratio is exactly 1.0. AER saves bandwidth whenever mean firing rate is below 50 Hz: in a sparse network, most neurons are silent so AER sends fewer bits.
