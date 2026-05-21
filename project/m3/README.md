# Milestone 3 — Integration and Synthesis

**Simulator:** Icarus Verilog 12.0 (`iverilog -g2012`)
**Synthesis:** OpenLane 2.3.10, Docker image `ghcr.io/efabless/openlane2:2.3.10`, sky130A PDK (sky130_fd_sc_hd)
**OpenLane run tag:** `RUN_2026-05-21_20-44-53`

## Reproduce co-simulation

```bash
iverilog -g2012 -o sim_out \
  project/m3/rtl/top.sv \
  project/m2/rtl/interface.sv \
  project/m2/rtl/compute_core.sv \
  project/m3/tb/tb_top.sv
vvp sim_out
```

Expected output: `PASS: 2/2 tests passed`

## Reproduce synthesis

```bash
docker run --rm \
  -v /home/saleh/ol_run_m3:/home/saleh/ol_run_m3 \
  -v /home/saleh/.volare:/home/saleh/.volare \
  -w /home/saleh/ol_run_m3 \
  ghcr.io/efabless/openlane2:2.3.10 \
  python3 -m openlane \
    --pdk-root /home/saleh/.volare/volare/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af \
    /home/saleh/ol_run_m3/config.json
```

RTL source for synthesis is in `~/ol_run_m3/hdl/` (copies of M2 RTL with Verilator lint suppress comments added to compute_core.sv).

## File catalog

| File | Description |
|------|-------------|
| `README.md` | This file — entry point, reproduction instructions, file index |
| `rtl/top.sv` | Integrated top module: instantiates axi4s_rx and compute_core, wires them together |
| `tb/tb_top.sv` | End-to-end co-simulation testbench; drives AXI4-Stream interface, checks echo_det against software reference |
| `sim/cosim_run.log` | Co-simulation transcript — contains PASS line |
| `sim/cosim_waveform.png` | End-to-end waveform: host AXI-S writes, internal compute, result output |
| `sim/cosim.vcd` | VCD waveform dump from co-simulation |
| `sim/gen_waveform.py` | Script that generated cosim_waveform.png from cosim.vcd |
| `synth/config.json` | OpenLane 2 configuration: clock 20 ns, sky130A, DIE_AREA 1500×1500 µm |
| `synth/openlane_run.log` | Full OpenLane stdout/stderr (flow.log + warning.log + error.log) |
| `synth/timing_report.txt` | Pre-PNR STA summary (all corners) |
| `synth/area_report.txt` | Cell count, die area, core utilization |
| `synth/power_report.txt` | Power estimate at nom_tt corner (21.05 mW total) |
| `synth/critical_path.md` | Critical path identification: start/end registers, logic stages, fix strategy |
| `synthesis_notes.md` | Narrative: what passed, what failed (DRT-0349), scope adjustment for M4 |
