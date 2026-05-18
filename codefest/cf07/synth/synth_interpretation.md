# Synthesis Interpretation — compute_core

**Tool:** OpenLane 2.3.10, sky130A PDK (sky130_fd_sc_hd), Yosys 0.46 / OpenROAD

## Clock and Slack

Target clock: 10 ns (100 MHz). Worst-case setup slack (nom_ss_100C_1v60 corner): -103.526 ns. The critical path is 113.5 ns; timing closes at 8.8 MHz. Hold slack is +0.057 ns, zero hold violations.

## Critical Path

The critical path is the combinational MAC tree in `always_comb`. 128 parallel 16-bit multipliers feed a 7-level adder reduction (log2(128) = 7). Each level adds carry-propagation delay through sky130 cells. No registers bound either end of this path; the full 128-MAC reduction runs in one combinational stage. Top cell types: ANDNOT (77,655), XOR (66,450), AND (36,340). All three come from the MAC tree: multiplication maps to XOR and AND, the adder reduction maps to ANDNOT and OR.

## Area and Cell Count

Post-synthesis: 243,521 cells, chip area 87,336 µm² (Yosys estimate). ANDNOT (77,655), XOR (66,450), and AND (36,340) account for 74% of all cells. All three are MAC tree cells.

## Warnings and Failures

Detailed routing failed at stage 44/78 (DRT-0349). 243,521 cells exceed what the default floorplan can route without congestion. Pre-PNR STA flagged 104,888 max-slew violations: the unregistered tree drives high fanout at 10 ns, exceeding sky130 drive strength limits. Both failures trace to the same root: a fully unrolled single-cycle MAC tree with no pipeline registers. The logic is correct; the physical implementation needs restructuring.
