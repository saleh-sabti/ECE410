# M3 Critical Path Analysis

## Critical Path (pre-PNR STA, nom_ss_100C_1v60 worst corner)

**Start:** `_439687_`: a `sky130_fd_sc_hd__dfxtp_2` flip-flop holding `u_core.ref_buf[127][3]` (deepest element of the reference shift register in compute_core)

**Logic stages:**
1. FF Q output (`ref_buf[127]`): sign extension to 40 bits (combinational wires, zero delay)
2. Fanout buffering through `fanout10621` → `fanout10620` → `fanout10619` (`buf_8` cells) to distribute one shift-register bit to all 128 multiplier inputs
3. AND/NAND tree implementing the 16×16 signed multiplier for one of the 128 MAC pairs
4. 7-level binary adder reduction tree: 128 products → 64 → 32 → 16 → 8 → 4 → 2 → 1 (40-bit accumulator)
5. 40-bit signed comparator: `acc_cross >= threshold`

**End:** `_441740_`: the `echo_det` flip-flop in compute_core

**Measured critical path delay:**
- Pre-PNR nom_ss corner: 154.0 ns (20 ns target → WNS = -134.0 ns)
- Pre-PNR nom_tt corner: 86.7 ns (20 ns target → WNS = -66.7 ns)
- **Post-CTS/optimization nom_tt corner: WNS = 0 ns, worst slack = +3.477 ns (timing closed)**

The OpenROAD resizer closed nom_tt by inserting buffer trees on the high-fanout shift-register nets and resizing cells on the path. nom_ss remains unclosed, but nom_tt at 50 MHz is valid.

## Why this is the critical path

All 128 multiplications happen combinationally in parallel each cycle. Results have to propagate through the full 7-level adder tree and comparator before the clock captures echo_det. No pipeline registers anywhere in the path. ref_buf[127] is the worst-case start because it drives the longest fanout chain before hitting a multiplier.

## What would shorten it

Insert pipeline registers after adder tree level 4 (reducing 128 products to 8 partial sums, then registering). This splits the 154 ns path into two stages of approximately 50-60 ns each, targeting a 10 ns clock (100 MHz). Latency increases by one cycle; throughput is unchanged. Alternatively, reducing N from 128 to 64 removes one adder tree level and cuts the multiplier fanout by half, which alone may close the slow-corner timing at 20 ns.
