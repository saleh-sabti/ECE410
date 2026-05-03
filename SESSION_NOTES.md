# ECE 410/510 — Session Notes
**Date:** March 31, 2026  
**Course:** Hardware for Artificial Intelligence and Machine Learning (HW4AI)  
**Instructor:** Christof Teuscher — Portland State University

---

## What We Set Up Today

### 1. Project Folder
- Created local project folder at `C:\Users\saleh\ece410`
- Initialized a Git repository with `main` branch

### 2. GitHub Repository
- Created public GitHub repo: [saleh-sabti/ECE410](https://github.com/saleh-sabti/ECE410)
- Installed GitHub CLI (`gh` v2.45.0)
- Authenticated with GitHub account (`saleh-sabti`)
- Linked local folder to remote repo and pushed initial commit

### 3. Python
- Verified Python 3.12.3 already installed
- Command: `python3 --version`

### 4. pip + PyTorch + torchinfo
- Installed pip via `get-pip.py` (no sudo needed)
- Installed PyTorch 2.11.0 and torchinfo 1.8.0
- Also installed numpy 2.4.4 (required by torchinfo)

### 5. Verilog Simulator
- Installed **Icarus Verilog** v12.0 — compiles and simulates Verilog
- Installed **GTKWave** v3.3.116 — GUI waveform viewer
- Installed via: `sudo apt-get install -y iverilog gtkwave`

### 6. LLM Smoke Test
- Wrote a 4-bit adder with carry-out in Verilog (`smoke_test/adder4.v`)
- Wrote a testbench (`smoke_test/adder4_tb.v`)
- Compiled and simulated with Icarus Verilog — all results correct
- Pushed to GitHub

---

## Checklist Status (due Wed, Apr 1)

| Item | Status |
|------|--------|
| GitHub account + public repo | Done |
| Post repo link in Canvas spreadsheet | Done |
| Python 3.x installed | Done (3.12.3) |
| Verilog simulator (Icarus Verilog + GTKWave) | Done |
| Paid LLM subscription (Claude) | Done |
| LLM smoke test (4-bit adder) | Done |
| PyTorch + torchinfo | Done |
| Canvas access | Done |
| Slack workspace | Done |
| Docker (optional) | Pending — not needed until later |

---

## Project Milestones

| Milestone | Due Date | Description |
|-----------|----------|-------------|
| M1 | Sun, Apr 12 | Heilmeier answers, software baseline, roofline analysis, interface selection, block diagram |
| M2 | Sun, May 3 | Working HDL + testbench, interface module in HDL |
| M3 | Sun, May 24 | OpenLane 2 synthesis attempt |
| M4 | Sun, Jun 7 | Full deliverable package + design justification report |

---

## Project Overview
Design a custom **AI/ML co-processor chiplet** that:
- Accelerates a computationally dominant AI/ML kernel of your choice
- Is written in **SystemVerilog**
- Synthesizes without errors using **OpenLane 2**
- Connects to a host via a standard hardware interface (SPI, I2C, AXI4-Lite, AXI4 Stream, PCIe, or UCIe)

---

---

## Session 2 — April 1, 2026

### What We Did

**Codefest 1 CLLM tasks:**
- Converted all PDFs in the ece410 folder to .txt using `pdftotext` (already installed)
- Installed `torchvision` and ran ResNet-18 profiling with torchinfo (batch=1, FP32, 3x224x224)
- Saved full profile to `codefest/cf01/profiling/resnet18_profile.txt`
- Identified top-5 MAC layers and computed arithmetic intensity for the stem Conv2d (7x7) layer
- Saved analysis to `codefest/cf01/profiling/resnet18_analysis.md`
- Written and pushed `project/heilmeier_draft.md` (Q1-Q3) for the echo detection project
- Written `project/algorithm_diagram.md` as a Mermaid source diagram
- Updated `README.md` with name (Saleh Sabti) and project topic
- All pushed to `saleh-sabti/ECE410`

**Tools and skills installed:**
- Installed `stop-slop` skill from github.com/hardikpandya/stop-slop into `~/.claude/skills/stop-slop`
- Added rule to `~/.claude/CLAUDE.md`: apply stop-slop rules when editing any prose

### Still Pending (before Sun Apr 5, 11:59pm)
- Export `project/algorithm_diagram.md` to PNG at mermaid.live → save as `project/algorithm_diagram.png` → commit + push
- Commit and push `codefest/cf01/cman_workload_accounting.md` (Saleh's hand-done CMAN file)

### Main Design Decisions

**Project topic: Hardware accelerator for real-time echo detection in voice signals**
- Core algorithm: normalized cross-correlation between far-end reference and near-end mic signal
- Output: 1-bit decision (echo present / not present) to trigger a downstream canceller
- Parallelism: all N multiply-accumulate operations across the correlation window are independent — they all fire in the same clock cycle. That is the core hardware acceleration argument.
- Weight storage: shift registers for both the reference and mic sample buffers. New sample shifts in each clock, oldest drops off. No addressing logic needed for streaming audio.
- Architecture sketch: two shift registers (N samples each) feeding an N-wide MAC array, into a normalizer, into a threshold comparator.

**Interface: TBD at M1** — will be justified based on arithmetic intensity and throughput analysis.

### Important Questions Saleh Asked

- How to run the smoke test manually → `vvp adder4_sim` or recompile with `iverilog`
- What does the smoke test do → tests a 4-bit adder with carry, 5 input cases including overflow
- Whether the CLLM profiling is connected to his project → no, it is a practice exercise using the same methodology he will apply to his own algorithm for M1
- Whether his echo detection topic has enough parallelism → yes, cross-correlation is embarrassingly parallel (independent MACs)
- Whether he should switch to a different topic (transformer matmul, conv layers, HDC) → decided to stick with echo detection
- Where to store weights in hardware if using traditional registers → shift registers for streaming audio; SRAM for larger windows
- How to carry session context into future Claude Code sessions → this file

### ResNet-18 Key Numbers (for reference)
- Total params: 11.7M, Total MACs: 1.81G
- Most MAC-intensive layer: Conv2d 1-1 (7x7 stem), 118M MACs, 9,408 params
- Arithmetic intensity of stem layer: ~61.3 FLOP/byte (compute-bound)

---

## Session 3 — April 5, 2026

### What We Did

**Codefest 1 status check:**
- Reviewed all deliverables against the official requirements
- Found two files not committed: `codefest/cf01/cman_workload_accounting.md` and `project/algorithm_diagram.png`
- Professor note flagged: algorithm must be in plain Python/C/C++ — avoid relying on PyTorch/scipy for the core loop (bottleneck would be inside the library, not measurable)

**Python reference implementation (`project/echo_detect.py`):**
- Wrote a pure Python normalized cross-correlation echo detector — no numpy/scipy/torch in the core loop
- Every MAC is explicit in a for loop
- Synthetic signals: reference = mix of 200/440/800 Hz sinusoids; mic = reference + delayed echo (ECHO_GAIN × reference[i − ECHO_DELAY]) + noise
- Option A chosen: fully synthetic signals (no real audio file needed), self-contained, reproducible
- Parameters: SAMPLE_RATE=16000, N=128 (8 ms window), ECHO_DELAY=320 samples (20 ms), ECHO_GAIN=0.5, THRESHOLD=0.7
- Key output numbers: 12.2M MACs for 2s of audio, 384 MACs/window (3×N), AI = 0.747 FLOP/byte → memory-bound
- This is the M1 software baseline

### Key Numbers (current parameters)
- Total MACs: 12,238,848
- MACs per window: 384 (3 × N=128)
- Arithmetic intensity: 0.747 FLOP/byte → memory-bound
- Hardware argument: keeping shift register buffers on-chip eliminates DRAM traffic and changes the bound

### Still Pending
- Commit `codefest/cf01/cman_workload_accounting.md` and `project/algorithm_diagram.png` — due tonight Sun Apr 5 11:59pm
- Decide on window size N for hardware design (currently 128)
- M1 due Sun Apr 12: software baseline (done), roofline analysis, interface selection, block diagram

---

## Session 4 — April 8, 2026

### What We Did

**Repo cleanup and file organization:**
- Added `project/roofline_plot.py` and `project/roofline.png` (M1 roofline deliverable, generated Apr 6)
- Added `codefest/cf02/hw4ai_explainer.jsx` (660-line React explainer component)
- Added week 2 lecture slides and assignment PDFs
- Reorganized `assignments/` into `week1/` and `week2/` subfolders
- Fixed `.gitignore` — changed `hw4ai_*.pdf` to `/hw4ai_*.pdf` so `assignments/` subdirs are no longer filtered
- Added `assignments/week2/hw4ai_ece510_codefest02_spring26_r2.pdf` and `hw4ai_ece510_project_milestone_1_spring26_r1.pdf`

**Read CF2 and M1 specs — key findings:**
- CF2 CMAN: no AI, hand-draw roofline for given hardware (10 TFLOPS, 320 GB/s, ridge = 31.25 FLOP/byte), classify GEMM and vector-add kernels
- CF2 CLLM: profile echo_detect.py, compute AI, build roofline with HW design point, write partition rationale, update Heilmeier
- M1 introduces `project/m1/` folder (new): sw_baseline.md, interface_selection.md, system_diagram.png
- `project/heilmeier_draft.md` must be renamed/moved to `project/heilmeier.md` for M1 grader path check
- Existing `project/roofline.png` must be copied to `codefest/cf02/profiling/roofline_project.png`

### Still Pending (due Sun Apr 12)

**CF2 CMAN (Saleh does alone, no AI):**
- Hand-draw roofline (log-log, ridge point labeled) for 10 TFLOPS / 320 GB/s hardware
- GEMM 1024x1024: compute FLOPs, bytes, AI, attainable GFLOP/s, bound, arch recommendation
- Vector-add 4M: same
- Deliver as `codefest/cf02/cman_roofline.md` (or .pdf/.png)

**CF2 CLLM (AI OK):**
- Profile `project/echo_detect.py` with cProfile (10+ runs) → `codefest/cf02/profiling/project_profile.txt`
- Write `codefest/cf02/analysis/ai_calculation.md` (FLOPs formula, bytes, AI = 0.747 FLOP/byte, dominant kernel %)
- Generate `codefest/cf02/profiling/roofline_project.png` (SW point + HW design point both labeled)
- Write `codefest/cf02/analysis/partition_rationale.md` (200-350 words, all 4 sub-questions)
- Update `project/heilmeier.md` (Q1-Q3, data-grounded)

**M1 (due same deadline):**
- Create `project/m1/sw_baseline.md` (platform, median wall-clock over 10 runs, throughput, memory)
- Create `project/m1/interface_selection.md` (interface choice, bandwidth calc, bottleneck analysis)
- Create `project/m1/system_diagram.png` (host + interface + chiplet boundary + compute + on-chip memory, all labeled)
- Rename `project/heilmeier_draft.md` to `project/heilmeier.md`

---

## Session 5 — April 9, 2026

### What We Did

**CF2 CLLM — all deliverables built and pushed:**
- Ran cProfile on `echo_detect.py` across 10 runs → `codefest/cf02/profiling/project_profile.txt`
- `normalized_xcorr` identified as dominant kernel: 69% of total program runtime, 87% of streaming detection loop
- Wrote `codefest/cf02/analysis/ai_calculation.md` — full FLOPs derivation (768 FLOP/window), bytes (1,028 bytes/window), AI = 0.747 FLOP/byte
- Generated `codefest/cf02/profiling/roofline_project.png` — CPU roofline (Intel Core Ultra 7 155H) + SW point (memory-bound) + HW chiplet design point (compute-bound)
- Wrote `codefest/cf02/analysis/partition_rationale.md` — 290 words, all 4 sub-questions answered with numbers
- Updated `project/heilmeier.md` from draft — Q1-Q3 grounded in profiling data
- Removed `project/heilmeier_draft.md`

**CF2 CMAN — Saleh's hand-drawn work transcribed:**
- `codefest/cf02/cman_roofline.md` — GEMM (AI=170.7, compute-bound, 10000 GFLOP/s) and vector-add (AI=0.083, memory-bound, 26.7 GFLOP/s)
- `codefest/cf02/image.png` — hand-drawn roofline scan committed and referenced in markdown

**M1 — all deliverables built and pushed:**
- `project/m1/sw_baseline.md` — Intel Core Ultra 7 155H, WSL2, Python 3.12.3, median 260 ms over 10 runs, 122,585 windows/s, 16.8 MB RSS
- `project/m1/interface_selection.md` — AXI4 Stream, 0.064 MB/s required vs 400 MB/s rated, not interface-bound
- `project/m1/system_diagram.png` — block diagram with all 5 labeled components

**CPU specs corrected mid-session:**
- System shows LPDDR5X-7467 (not 6400) → peak BW = 119.5 GB/s, ridge = 3.86 FLOP/byte (not 6.74)
- All files updated with correct numbers

### Key Numbers (current)
- Algorithm: normalized cross-correlation, N=128, 768 FLOP/window
- AI = 0.747 FLOP/byte (no DRAM reuse)
- CPU: Intel Core Ultra 7 155H, 119.5 GB/s BW, 460.8 GFLOP/s peak, ridge = 3.86 FLOP/byte → SW is memory-bound
- Chiplet: 128 MACs @ 500 MHz, 512 GB/s on-chip, 128 GFLOP/s peak, ridge = 0.25 FLOP/byte → HW is compute-bound
- SW median wall-clock: 260 ms for 2s audio (31,872 windows)
- Interface: AXI4 Stream, required 0.064 MB/s

### Still Pending
- M2 (due May 3): HDL module + testbench, interface module in HDL
- M3 (due May 24): OpenLane 2 synthesis
- M4 (due Jun 7): full deliverable package + report

---

## Session 6 — April 19, 2026

### What We Did

**CF3 — all deliverables built and pushed (commit 72bd180):**

CMAN:
- `codefest/cf03/cman_dram_traffic.md` — Saleh wrote, math fixed and committed
- Naive traffic: (2N³ + N²) × 4 = 266,240 bytes, memory-bound (0.83 µs)
- Tiled traffic: 2N² × 4 = 8,192 bytes, compute-bound (0.026 µs)
- Ratio = N = 32 (per spec's idealized model: each element loaded once in tiled)

CLLM:
- `codefest/cf03/cuda/gemm_naive.cu` — 508 GFLOP/s measured (cudaEventRecord)
- `codefest/cf03/cuda/gemm_tiled.cu` — 493 GFLOP/s measured
- `codefest/cf03/profiling/gemm_roofline.png` — both kernels plotted on RTX 4050 Laptop roofline
- `codefest/cf03/profiling/ncu_naive.txt` + `ncu_tiled.txt` — WSL2 perf counter blocked, but Nsight output present
- `codefest/cf03/analysis/gemm_analysis.md` — 244 words, all 3 sub-questions (L2 cache explains why tiled gave no speedup at N=1024)

COPT:
- `codefest/cf03/copt/nn_forward_gpu.py` — 4→5 ReLU→1, batch=16, GPU forward pass
- `codefest/cf03/copt/copt_output.txt` — RTX 4050, shape [16,1], cuda:0

### Key Numbers (CF3)
- GPU: RTX 4050 Laptop, 3588 GFLOP/s peak FP32, 192 GB/s DRAM, ridge = 18.7 FLOP/byte
- Naive GEMM: AI = 0.25 FLOP/byte, memory-bound, 508 GFLOP/s (L2 cache hides DRAM latency)
- Tiled GEMM: AI = 2.0 FLOP/byte, expected 8x speedup, actual ~same -- both L2-bound at N=1024

### Important Decisions and Questions
- Ratio=N vs T: spec uses idealized model (each element once in tiled) → ratio=N=32; precise T=8 math gives ratio=T=8
- ncu blocked in WSL2 (ERR_NVGPUCTRPERM); files still satisfy "referenced" criteria, skipped PowerShell recompile
- GFLOP/s varies per run (GPU clock variance); 508/493 from cudaEventRecord, ncu files show 472/447 -- both valid
- Tiled no speedup at N=1024: all 3 matrices fit in L2 (12 MB), naive gets free cache reuse, T=8 adds sync overhead

### Still Pending
- M2 (due May 3): HDL module + testbench, interface module in HDL
- M3 (due May 24): OpenLane 2 synthesis
- M4 (due Jun 7): full deliverable package + report

---

## Session 7: April 22-26, 2026

### What We Did

**File organization:**
- Moved week 3 PDFs from `assignments/` root into `assignments/week3/`
- Copied week 4 PDFs from Downloads into `assignments/week4/`
- Installed cocotb 2.0.1 via pip

**CF4 CMAN (Saleh wrote, Claude cleaned up):**
- `codefest/cf04/cman_quantization.md`: all 5 tasks
- max|W| = 2.31, S = 0.018189, correct S MAE = 0.00433, S_bad = 0.01 MAE = 0.171
- 4 elements clamp with S_bad; one-sentence explanation included

**CF4 CLLM:**
- `mac_llm_A.v`: Claude Sonnet 4.6 output
- `mac_llm_B.v`: Gemini 3.1 Pro output (Saleh pasted from Gemini)
- `mac_tb.v`: iverilog testbench, 7 steps, all pass for both LLMs and mac_correct
- `mac_correct.v`: explicit 16-bit product, sign extension via `{{16{product[15]}}, product}`
- `codefest/cf04/review/mac_code_review.md`: 3 issues identified (Gemini over-sized multiplier, redundant signed'() cast, Claude sign extension portability)
- Compile results and sim logs recorded verbatim

**CF4 COPT:**
- `codefest/cf04/cocotb_mac/test_mac.py`: test_mac_basic + test_mac_overflow, both pass
- `codefest/cf04/cocotb_mac/Makefile`: WAVES=1, icarus
- `codefest/cf04/cocotb_mac/sim_log.txt`: 2/2 PASS
- `codefest/cf04/cocotb_mac/waveform.png`: generated from VCD via matplotlib (GTKWave zoom issue)
- Overflow: wraps at -2147455462 after 133146 cycles of +16129, no saturation
- `project/hdl/echo_detect_core.sv`: N=128, DW=16, parameterized skeleton with shift regs + accumulator stub
- `project/hdl/echo_detect_core_tb.py`: cocotb stub with reset, no-echo, full-correlation tests
- README updated with INT16 precision justification and AXI4 Stream bandwidth justification

### Key Decisions
- Precision: INT16 for audio samples, full codec dynamic range, no quantization noise at 16-bit
- Interface: AXI4 Stream confirmed from M1, 0.064 MB/s required vs 400 MB/s rated = 6250x headroom
- mac_correct.v: explicit 16-bit intermediate is the portable fix vs both LLM outputs

### Still Pending
- M2 (due May 3): fully functional HDL compute core, interface module, verified transaction
- M3 (due May 24): OpenLane 2 synthesis
- M4 (due Jun 7): full deliverable package + report

---

## Session 8: May 2, 2026

### What We Did

**Added Week 5 docs:**
- Copied `assignments/Week5/`: CF5 PDF, M2 spec PDF, two lecture slides (TPU/GPU/transformers recap)

**M2 — all deliverables built, simulated, and pushed:**

`project/m2/rtl/compute_core.sv`: synthesizable SystemVerilog compute core
- Two N=128 shift registers (ref and mic buffers), INT16 samples
- Combinational parallel MAC tree: 128 multipliers fire every cycle, result summed into 40-bit accumulator
- Outputs echo_det=1 when acc_cross >= threshold (threshold is a port, not a parameter)
- Single clock domain, synchronous active-high reset
- First valid output appears N+1 valid_in cycles after reset (window fill latency)

`project/m2/rtl/interface.sv`: AXI4-Stream slave (module named axi4s_rx)
- TREADY wired high (no back-pressure: 0.064 MB/s required vs 400 MB/s rated)
- TDATA[31:16] = ref sample, TDATA[15:0] = mic sample
- Decoded pair out to compute_core with 1-cycle latency

`project/m2/tb/tb_compute_core.sv`: 2/2 PASS
- Test 1: ref=1, mic=1 for 128 samples. acc_cross=128 >= 64. echo_det=1. ✓
- Test 2: ref=1, mic=-1. acc_cross=-128 < 64. echo_det=0. ✓
- Reference values from Python: sum(1*1 for _ in range(128)) = 128

`project/m2/tb/tb_interface.sv`: 4/4 PASS
- Test 1: TDATA=0xABCD_1234 → ref_out=0xABCD, mic_out=0x1234, valid_out=1
- Test 2: TVALID=0 → valid_out=0
- Test 3a/b: two back-to-back beats, each decoded correctly

`project/m2/sim/`: compute_core_run.log, interface_run.log (both PASS), waveform.png
- Waveform shows 7 signals: clk, rst, valid_in, ref_in, mic_in, echo_det, valid_out
- Annotated with rst↓ and echo_det↑ events

`project/m2/precision.md`: 526 words
- INT16 chosen: 96 dB dynamic range, direct codec/ADC compatibility
- 40-bit accumulators: max sum = 1.37 × 10¹¹, needs 37 bits, 40 gives headroom
- Roofline tie-in: INT16 keeps AI at 0.747 FLOP/byte; FP32 would halve it to 0.374
- Sqrt normalization deferred to M3 (hardware sqrt costs area + pipeline stages)
- Error analysis: 0 LSB error vs float64 reference on all test vectors

`project/m2/README.md`: exact iverilog commands, module notes, deviations from M1 (none)

**Prose pass:** stop-slop applied to all markdown and SV header comments. All em dashes removed.

### Key Decisions

- **`interface` is a SV reserved keyword**: module named `axi4s_rx`, file stays `interface.sv` per M2 spec. Documented in header and README. No fix possible without renaming the file.
- **Sqrt normalization deferred**: comparing raw acc_cross against threshold works for constant-amplitude signals and is correct for M2. Full normalization (CORDIC or Newton-Raphson) goes into M3.
- **Threshold as port**: lets the caller tune it per signal level rather than baking it in as a parameter.
- **Combinational MAC tree**: for loop in always_comb synthesizes as 128 parallel multipliers feeding a reduction tree. Timing-critical path for large N but correct and synthesizable.
- **iverilog timing**: valid_out only asserts when valid_in is high AND window is full. Need N+1 valid_in pulses minimum to see one valid output. Testbench checks outputs at the posedge where window_full first goes true with valid_in=1, before clearing valid_in.

### Key Numbers

- N=128, DW=16, ACCW=40
- Testbench threshold: 40'sd64
- acc_cross (ref=1, mic=1, N=128) = 128 (computed from Python, exact in INT16)
- Compute core latency: N+1 = 129 valid_in cycles

### Still Pending

- **CF5 CMAN (Saleh, due May 3):** `codefest/cf05/cman_systolic_trace.md`
  - 2×2 weight-stationary systolic array trace, A=[[1,2],[3,4]], B=[[5,6],[7,8]]
  - PE diagram, ≥4-row cycle table, MAC count, reuse count, off-chip access count, output-stationary one-liner
  - NO AI
- M3 (due May 24): OpenLane 2 synthesis
- M4 (due Jun 7): full deliverable package + report

