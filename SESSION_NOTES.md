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

## Useful Commands

```bash
# Run a Verilog simulation
iverilog -o output_name file.v testbench.v
vvp output_name

# Push changes to GitHub
git add .
git commit -m "your message"
git push

# Check Python packages
python3 -c "import torch; print(torch.__version__)"
python3 -c "import torchinfo; print(torchinfo.__version__)"
```
