# Synthesis Interpretation — compute_core

**Tool:** OpenLane 2.3.10, sky130A PDK (sky130_fd_sc_hd), Yosys 0.46 / OpenROAD

## Clock and Slack

Target clock: 10 ns (100 MHz). Worst-case setup slack (nom_ss_100C_1v60 corner): -103.526 ns.
That puts the actual critical path at roughly 113.5 ns, meaning the design only closes timing at about 8.8 MHz — far below the 100 MHz target. Hold slack is +0.057 ns with zero hold violations, so hold is clean.

## Critical Path

The critical path runs entirely through the combinational MAC tree in `always_comb`. The design instantiates 128 parallel 16-bit multipliers whose products feed a sequential adder tree. With N=128, the adder tree has 7 reduction levels (log2(128)), and each level adds delay through carry-propagation chains in the sky130 standard cell library. The dominant cell types along this path are ANDNOT (77,655 instances), XOR (66,450), and AND (36,340) — all characteristic of a wide unregistered adder tree. There are no source or sink registers bounding this path; the entire 128-MAC reduction happens in a single combinational stage.

## Area and Cell Count

Post-synthesis cell count: 243,521 cells. Chip area estimate from Yosys: 87,336 µm². The three largest contributors by instance count are ANDNOT (77,655), XOR (66,450), and AND (36,340), together accounting for roughly 74% of all cells. This distribution is consistent with a fully unrolled multiplier-accumulator array — multiplication maps to XOR and AND trees, and the reduction maps to ANDNOT and OR logic.

## Warnings and Failures

Detailed routing failed at stage 44/78 (DRT-0349: routing congestion). With 243,521 cells, the default floorplan area is too small to route all nets without violations. The pre-PNR STA also reported 104,888 max-slew violations, indicating the combinational tree drives enormous fanout loads that exceed sky130 drive strength limits at the 10 ns clock constraint. These are direct consequences of the fully unrolled single-cycle MAC tree — not a correctness issue, but a physical implementation blocker at this clock target.
