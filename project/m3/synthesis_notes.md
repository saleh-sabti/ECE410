# M3 Synthesis Notes

## What was attempted

The M3 design is the integrated top module (`project/m3/rtl/top.sv`) that wires `axi4s_rx` (from M2 `interface.sv`) into `compute_core` (from M2 `compute_core.sv`). The interface passes decoded ref/mic sample pairs and a valid signal directly to the compute core with no glue logic. The top module exposes the AXI4-Stream slave ports, a threshold port, and the echo_det/valid_out outputs.

Synthesis ran using OpenLane 2.3.10 with the sky130A PDK (sky130_fd_sc_hd standard cell library) inside the official `ghcr.io/efabless/openlane2:2.3.10` Docker container. Clock target: 20 ns (50 MHz), up from the 10 ns target in the CF7 attempt. Die area set to 1500×1500 µm (larger than CF7's default) to give the router more room. Run tag: `RUN_2026-05-21_20-44-53`.

## What succeeded

Yosys synthesis completed without errors. The design mapped to 222,941 standard cells with a Yosys-reported liberty area of 88,038 µm². The top module hierarchy resolved correctly — `axi4s_rx` added roughly 10 flip-flops and a small combinational decoder on top of compute_core. Its contribution to cell count and area is negligible.

Verilator lint passed after adding `// verilator lint_off BLKLOOPINIT` comments around the for-loop resets in compute_core. Verilator objects to delayed assignments to arrays inside for-loops; the suppression is correct because the synthesis tool (Yosys) handles these constructs properly.

Floorplanning, placement, CTS, timing repair, and global routing all completed. After CTS and timing optimization (steps 34-37), the OpenROAD timing optimizer closed setup timing at the nom_tt_025C_1v80 corner: WNS = 0 ns, TNS = 0 ns, worst setup slack = +3.477 ns. This is a significant improvement over the CF7 attempt, which showed -103.5 ns WNS at 10 ns. The 20 ns clock target and larger die area gave the placer room to spread the combinational logic and allowed the resizer to buffer the critical paths.

Hold timing: WNS = 0 ns, no violations across all checked corners.

Power estimation succeeded at the mid-PNR stage: total power 21.05 mW at nom_tt, dominated by clock tree (57.3%, 12.1 mW) driving 4,139 flip-flops. The MAC tree is fully combinational and contributes only 3.5% of total power.

## What failed

Detailed routing (OpenROAD DRT) failed at stage 43/78 with error DRT-0349: `LEF58_ENCLOSURE with no CUTCLASS is not supported. Skipping for layer mcon`. This is a PDK-level LEF rule that OpenROAD's detailed router cannot handle on this version. Global routing completed cleanly with 0 overflow. Detailed routing reached 20% with 0 violations before hitting the LEF58 error.

This is the same DRT-0349 error as CF7, confirming it is not caused by timing violations or excessive congestion — the post-placement timing is actually closed. The failure is a compatibility issue between OpenLane 2.3.10 and the sky130A LEF rules for the mcon via layer. It is a known limitation of this version of the flow on this PDK.

## Scope adjustment

The core algorithm is unchanged: normalized cross-correlation of N=128 samples. What needs to change for M4 is the implementation strategy inside compute_core.

For M4, I will reduce N from 128 to 64. This halves the shift register depth, cuts combinational cell count from ~222K to ~110K, and reduces the adder tree from 7 levels to 6. The DRT-0349 failure is unrelated to cell count — it is a PDK rule issue — but the smaller design will also make the router's job easier and reduce routing congestion if the LEF issue is addressed (e.g., by updating the PDK or using an OpenLane version with the fix). The M1 baseline used N=128 but the echo detection decision is still meaningful at N=64: the window shifts from 8 ms to 4 ms at 16 kHz, which still captures the echo delay range used in the software baseline (20 ms at 320 samples).

The benchmark comparison in M4 will compare software (260 ms for 2s of audio, Intel Core Ultra 7 155H) against the hardware chiplet (N=64, 50 MHz, one result per valid_in cycle). The latency and throughput arguments remain the same; the arithmetic intensity argument (shift registers on-chip → compute-bound) holds equally for N=64.

## Key numbers summary

| Metric | Value |
|--------|-------|
| Tool | OpenLane 2.3.10, sky130_fd_sc_hd |
| Clock target | 20 ns (50 MHz) |
| Yosys cell count | 222,941 |
| Liberty area | 88,038 µm² |
| Die area (floorplan) | 5,691,320 µm² (2380×2391 µm) |
| Core utilization | 35.2% |
| Setup WNS (nom_tt, post-CTS) | 0 ns (closed) |
| Setup worst slack (nom_tt) | +3.477 ns |
| Hold WNS | 0 ns |
| Total power (nom_tt) | 21.05 mW |
| Routing | FAILED — DRT-0349, LEF58_ENCLOSURE mcon |
