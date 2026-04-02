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

---

## Session 2: Context & Workflow Setup
**Date:** April 1, 2026

### What We Did
- Explored project structure to understand existing files and organization
- Created persistent memory system (MEMORY.md, project_overview.md, user_profile.md)
- Clarified project status: M1 deadline is April 12 (11 days away)
- Identified what's remaining for M1 completion

### Project Files Inventory
```
codefest/cf01/          → ResNet18 analysis (profiling work)
project/                → Heilmeier draft, algorithm diagram
smoke_test/             → 4-bit adder (LLM smoke test)
SESSION_NOTES.md        → Setup and progress tracking
README.md               → Project overview
```

### Key Design Decisions Made
1. **Algorithm Choice:** Normalized cross-correlation for echo detection (regular, predictable computation — ideal for custom hardware)
2. **Hardware Scope:** Fixed-function chiplet (no branching, no variable inputs, small/fast/cheap)
3. **Problem Motivation:** Remove CPU burden, reduce latency (<1ms), enable downstream cancellation
4. **Target Applications:** Voice calls on earbuds, hearing aids, smart speakers (battery-constrained)

### M1 Remaining Tasks (Apr 12 deadline)
- [ ] Finish Heilmeier Catechism (Q4-Q7: cost, timeline, stakeholders, competition)
- [ ] Write Python software baseline (reference echo detection implementation)
- [ ] Roofline analysis (peak performance vs. algorithm demands)
- [ ] Interface selection (SPI/I2C/AXI4-Lite/AXI4-Stream/PCIe/UCIe)
- [ ] Block diagram (hardware + host integration)

### Important Questions Asked
1. **"What is the best way to work?"** → Answer: Start with one deliverable at a time; Heilmeier → Python baseline → roofline → interface → block diagram
2. **"I feel there are lots of files and such"** → Answer: Organized by milestone; SESSION_NOTES.md is your main context document; use it to track decisions and progress

### Codefest 1 CMAN Analysis
Created `codefest/cf01/cman_calculator.py` — automated roofline analysis tool
- Input: Layer dimensions (fully-connected networks)
- Output: MACs, parameters, memory usage, arithmetic intensity
- Validates handwritten CMAN calculations from Code HW1 assignment
- Classifies networks as memory-bound vs. compute-bound
- Pushed to GitHub (commit: 91315ad)

### Next Steps
1. Complete Heilmeier Catechism (remaining Q4-Q7)
2. Write Python correlation-based echo detector
3. Run roofline analysis on the Python implementation
4. Finalize interface choice and block diagram
5. Push all M1 deliverables to GitHub before April 12
