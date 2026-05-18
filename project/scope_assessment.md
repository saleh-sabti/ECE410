# Project Scope Assessment

**Design:** Echo detection chiplet. Normalized cross-correlation, N=128 window, INT16 samples, AXI4-Stream interface.

**Updated after CF7 synthesis (May 2026).**

## Current Status

M2 HDL passes all tests (2/2 compute core, 4/4 interface). CF7 synthesis on sky130A found two physical blockers: the 128-MAC combinational tree produces a 113.5 ns critical path (8.8 MHz max at 10 ns target), and 243,521 cells overflow the default floorplan, causing routing failure.

## Scope Adjustments

Algorithm and interface stay the same. For M3, I will pipeline the adder tree: registering after the first four reduction levels targets a 20 ns clock (50 MHz). At 16 kHz audio, that is 3125x real-time margin.

Sqrt normalization stays deferred. At 243,521 cells the design is already large; adding CORDIC logic pushes the count further. The threshold comparison in compute_core.sv is sufficient for the 1-bit output.

N=128 stays for M3. If pipelining alone does not close routing, N drops to 64.

## Confidence

Algorithm: high. Interface: high. HDL functionality: high. Physical closure at 20 ns with pipelining: medium. The M3 run will confirm.
