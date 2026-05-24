# Milestone 3: Integration and Synthesis

**Simulator:** Icarus Verilog 12.0 (`iverilog -g2012`)
**Synthesis:** OpenLane 2.3.10, Docker image `ghcr.io/efabless/openlane2:2.3.10`, sky130A (sky130_fd_sc_hd)
**Run tag:** `RUN_2026-05-21_20-44-53`

## Run co-simulation

```bash
iverilog -g2012 -o sim_out \
  project/m3/rtl/top.sv \
  project/m2/rtl/interface.sv \
  project/m2/rtl/compute_core.sv \
  project/m3/tb/tb_top.sv
vvp sim_out
```

Expected output: `PASS: 2/2 tests passed`

## Run synthesis

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

RTL source for synthesis is in `~/ol_run_m3/hdl/` (M2 RTL with Verilator lint suppress comments added to compute_core.sv).

## Files

| File | Description |
|------|-------------|
| `rtl/top.sv` | Top module: instantiates axi4s_rx and compute_core |
| `tb/tb_top.sv` | Co-sim testbench: drives AXI4-Stream, checks echo_det against software reference |
| `sim/cosim_run.log` | Co-sim output (PASS line is here) |
| `sim/cosim_waveform.png` | Waveform: AXI-S writes, compute, result output |
| `sim/cosim.vcd` | VCD dump from co-simulation |
| `synth/config.json` | OpenLane 2 config: clock 20 ns, sky130A, die 1500x1500 µm |
| `synth/openlane_run.log` | Full OpenLane log |
| `synth/timing_report.txt` | Pre-PNR STA (all corners) |
| `synth/area_report.txt` | Cell count, die area, utilization |
| `synth/power_report.txt` | Power estimate at nom_tt (21.05 mW) |
| `synth/critical_path.md` | Critical path: start/end registers, logic stages, fix plan |
| `synthesis_notes.md` | What passed, what failed (DRT-0349), plan for M4 |
