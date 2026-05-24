# M3 Synthesis Notes

## What was attempted

The M3 design wires `axi4s_rx` (from M2 `interface.sv`) into `compute_core` (from M2 `compute_core.sv`) through a top module. The top exposes the AXI4-Stream slave ports, a threshold input, and the echo_det/valid_out outputs. No glue logic between the two submodules.

Synthesis used OpenLane 2.3.10 with sky130A (sky130_fd_sc_hd). Clock target: 20 ns (50 MHz). Die area: 1500x1500 µm. Run tag: `RUN_2026-05-21_20-44-53`.

## What passed

Yosys mapped the design to 222,941 standard cells, liberty area 88,038 µm². The `axi4s_rx` block adds about 10 flip-flops and a small decoder on top of compute_core; its area share is negligible.

Verilator lint passed after adding `// verilator lint_off BLKLOOPINIT` around the for-loop resets in compute_core. Verilator objects to delayed array assignments in loops; Yosys handles them fine so the suppression is correct.

Floorplan, placement, CTS, and global routing all completed. After timing optimization (steps 34-37), setup timing closed at nom_tt_025C_1v80: WNS = 0 ns, worst setup slack = +3.477 ns. The CF7 attempt had WNS = -103.5 ns at a 10 ns target. Moving to 20 ns and a larger die gave the placer room to spread the logic.

Hold timing: WNS = 0 ns, no violations.

Power at nom_tt: 21.05 mW total. Clock tree is 57.3% (12.1 mW) driving 4,139 flip-flops. The MAC tree is fully combinational, only 3.5% of power.

## What failed

Detailed routing (OpenROAD DRT) failed at stage 43/78:

```
DRT-0349: LEF58_ENCLOSURE with no CUTCLASS is not supported. Skipping for layer mcon
```

Global routing finished clean with 0 overflow. DRT reached 20% before hitting this error. This is a PDK-level LEF rule that this version of OpenROAD's router can't handle. It is the same error as CF7, so it is not caused by timing or congestion. The placement timing is actually closed. This is a known compatibility issue between OpenLane 2.3.10 and sky130A's mcon via rules.

## Plan for M4

For M4 I will drop N from 128 to 64. That halves shift register depth, cuts cell count from ~222K to ~110K, and drops the adder tree from 7 levels to 6. The DRT-0349 failure is not related to cell count, but a smaller design reduces congestion generally. The 4 ms window at 16 kHz (vs 8 ms at N=128) still covers the echo delays used in the software baseline (20 ms peak at 320 samples).

The M4 benchmark will compare: software baseline (260 ms for 2s audio, Intel Core Ultra 7 155H) vs hardware chiplet (N=64, 50 MHz, one result per valid_in cycle).

## Key numbers

| Metric | Value |
|--------|-------|
| Tool | OpenLane 2.3.10, sky130_fd_sc_hd |
| Clock target | 20 ns (50 MHz) |
| Yosys cell count | 222,941 |
| Liberty area | 88,038 µm² |
| Die area (floorplan) | 5,691,320 µm² (2380x2391 µm) |
| Core utilization | 35.2% |
| Setup WNS (nom_tt, post-CTS) | 0 ns (closed) |
| Setup worst slack (nom_tt) | +3.477 ns |
| Hold WNS | 0 ns |
| Total power (nom_tt) | 21.05 mW |
| Routing | FAILED: DRT-0349, LEF58_ENCLOSURE mcon |
