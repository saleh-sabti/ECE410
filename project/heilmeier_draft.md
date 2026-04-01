# Heilmeier Catechism — Draft
ECE 410/510 Spring 2026 | Saleh Sabti

## Q1: What are you trying to do?
Build a hardware chiplet that listens to voice audio in real time and decides whether an echo is present in the microphone signal, so a downstream cancellation system knows when to activate. The chiplet takes two inputs — the far-end reference signal (what the speaker is playing) and the near-end microphone signal — and outputs a single binary decision: echo detected or not.

## Q2: How is it done today, and what are the limits of current practice?
Echo detection today runs in software on a general-purpose CPU or DSP using adaptive correlation algorithms (LMS/NLMS filters) or lightweight ML classifiers. The limits are:
- **Latency:** Software detection adds milliseconds of delay, which is audible and degrades voice quality in real-time calls.
- **CPU load:** The detection loop competes with other audio processing tasks, causing jitter under load.
- **Power:** Running continuous correlation on a CPU consumes far more power than a dedicated fixed-function circuit, a problem for mobile and embedded devices (earbuds, smart speakers, hearing aids).

## Q3: What is new in your approach and why do you think it will work?
A dedicated hardware accelerator chiplet for echo detection: a fixed-function MAC array that continuously computes the normalized cross-correlation between the reference and microphone signals, feeding a threshold comparator that produces the binary decision. This is new relative to software because:
- The detection path is entirely off the CPU — zero CPU cycles consumed.
- Latency drops to tens of clock cycles (microseconds) rather than milliseconds.
- Power consumption is orders of magnitude lower than a CPU running the equivalent loop.
- The operation (dot product + normalization + compare) maps directly to hardware with no control overhead.

The approach will work because cross-correlation echo detection is a well-understood algorithm with a fixed, regular compute pattern — exactly the kind of kernel that benefits most from custom hardware.
