# Project Scope Assessment

**Design:** Echo detection chiplet — normalized cross-correlation, N=128 window, INT16 samples, AXI4-Stream interface.

**Updated after CF7 synthesis (May 2026).**

## Current Status

M2 HDL is functionally correct and simulates cleanly (2/2 compute core tests, 4/4 interface tests). The CF7 synthesis attempt on sky130A exposed two physical implementation issues: the fully combinational 128-MAC adder tree produces a 113.5 ns critical path (max freq 8.8 MHz at 10 ns target), and 243,521 total cells cause routing congestion that blocks detailed routing.

## Scope Adjustments

The core algorithm and interface remain unchanged. The RTL architecture needs one change for M3: pipeline the adder tree to split the critical path. Registering after the first four reduction levels cuts the setup slack violation from -103.5 ns to approximately -45 ns per stage, targeting a 20 ns clock (50 MHz). At 16 kHz audio with one sample pair per cycle, 50 MHz gives 3125x real-time margin — more than enough.

The sqrt normalization (deferred since M2) stays deferred to M4 or dropped. The synthesis result shows area is already large without it; adding a CORDIC sqrt would push cell count further. The threshold-based comparison in compute_core.sv is sufficient for the binary echo-detected output.

N=128 is kept for M3 unless pipelining alone does not resolve routing. If routing still fails after pipelining, N will be reduced to 64.

## Confidence

Algorithm: high. Interface: high. HDL functionality: high. Physical closure at 20 ns after pipelining: medium — dependent on whether the floorplan area is sufficient. This will be confirmed in the M3 run.
