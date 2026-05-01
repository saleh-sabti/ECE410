# M2: Echo Detection Chiplet RTL

## Simulator

Icarus Verilog 12.0

```bash
iverilog --version
```

## Running the Simulations

Run from repo root:

```bash
# Compute core
iverilog -g2012 -o /tmp/cc_sim \
  project/m2/rtl/compute_core.sv \
  project/m2/tb/tb_compute_core.sv
vvp /tmp/cc_sim

# Interface module
iverilog -g2012 -o /tmp/if_sim \
  project/m2/rtl/interface.sv \
  project/m2/tb/tb_interface.sv
vvp /tmp/if_sim
```

Both end with `PASS ...`. VCD files write to `project/m2/sim/` relative to working directory. Run from repo root or update the `$dumpfile` paths in the testbenches if you move things around.

## Modules

### `compute_core.sv`: module `compute_core`

Sliding window cross-correlator. Holds two N=128 shift registers (ref and mic samples). Each clock cycle it multiplies all 128 pairs in parallel and sums them into a 40-bit accumulator. Outputs `echo_det=1` when that sum exceeds threshold. INT16 inputs. First valid output appears N+1 valid_in cycles after reset.

### `interface.sv`: module `axi4s_rx`

`interface` is a reserved keyword in SystemVerilog so the module is named `axi4s_rx`. File stays `interface.sv` per the M2 spec.

AXI4-Stream slave. TREADY is wired high because the required data rate is 0.064 MB/s vs. the protocol's rated 400 MB/s: back-pressure is not needed. TDATA[31:16] = ref sample, TDATA[15:0] = mic sample. Outputs the decoded pair to compute_core with 1-cycle latency.

## Changes from M1

None. Interface stays AXI4-Stream as selected in `project/m1/interface_selection.md`.

## Python dependency (waveform only)

```
matplotlib >= 3.5
```

Logs and waveform are already committed. No need to re-run the waveform script for grading.
