# Heilmeier Catechism — Draft
ECE 410/510 Spring 2026 | Saleh Sabti

## Q1: What are you trying to do?
Build a hardware chiplet that listens to voice audio in real time and decides whether an echo is present. It takes two inputs: the far-end reference signal (what the speaker is playing out) and the near-end microphone signal. It outputs one bit: echo present or not. A downstream cancellation stage uses that decision to know when to act.

## Q2: How is it done today, and what are the limits of current practice?
Echo detection today runs in software on a CPU or DSP, using adaptive correlation filters like LMS or NLMS, sometimes a small ML classifier. Three problems come up consistently.

First, latency. Software adds milliseconds of detection delay, which is audible in a live call. Second, CPU load. The detection loop runs continuously and competes with other audio tasks, causing jitter when the system is busy. Third, power. Keeping a CPU core active for correlation burns far more energy than a dedicated circuit would, which matters for earbuds, hearing aids, and smart speakers running on battery.

## Q3: What is new in your approach and why do you think it will work?
The idea is a fixed-function chiplet that does nothing but compute the normalized cross-correlation between the two audio streams and compare it to a threshold. The CPU is not involved in the detection path at all.

This works for a specific reason: cross-correlation echo detection is a regular, predictable computation. Every sample window is the same operation: a dot product, a normalization, a compare. That regularity is exactly what makes a problem a good fit for custom hardware. There is no branching to handle, no variable-length input, no memory access pattern that changes at runtime. The hardware can be small, fast, and cheap to run.
