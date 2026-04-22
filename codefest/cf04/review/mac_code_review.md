# CF4 CLLM — MAC Code Review

## LLM Assignments

| File | LLM | Model Version |
|------|-----|---------------|
| mac_llm_A.v | Claude | Claude Sonnet 4.6 |
| mac_llm_B.v | GPT-4o | GPT-4o (fill in version after prompting) |

---

## Compilation Results

**mac_llm_A.v:**
```
iverilog -g2012 -o mac_llm_A_sim mac_llm_A.v mac_tb.v
→ No errors, no warnings.
```

**mac_llm_B.v:**
```
[fill in after obtaining GPT-4o output]
```

---

## Simulation Results

### mac_llm_A.v

Command: `vvp mac_llm_A_sim`

```
PASS step 0: out=0
PASS step 1: out=12
PASS step 2: out=24
PASS step 3: out=36
PASS step 4: out=0
PASS step 5: out=-10
PASS step 6: out=-20
ALL TESTS PASSED
```

Sequence: a=3,b=4 for 3 cycles (12→24→36), rst asserts (0), then a=-5,b=2 for 2 cycles (-10→-20).

### mac_llm_B.v

```
[fill in after simulation]
```

### mac_correct.v

Command: `vvp mac_correct_sim`

```
PASS step 0: out=0
PASS step 1: out=12
PASS step 2: out=24
PASS step 3: out=36
PASS step 4: out=0
PASS step 5: out=-10
PASS step 6: out=-20
ALL TESTS PASSED
```

---

## Issues Found

### Issue 1 — Accumulator width mismatch via implicit size cast (mac_llm_A.v)

**Offending lines:**
```systemverilog
out <= out + 32'(a * b);
```

**Why it is wrong/ambiguous:**
The `32'()` operator is a size cast. Per IEEE 1800-2017 §6.24.1, a size cast zero-extends or sign-extends based on the signedness of the operand. Here `a * b` is signed, so iverilog sign-extends correctly. However, the expression context dependency is tool-specific: Verilator and some synthesis linters evaluate `a * b` in a self-determined context (8-bit, since both operands are 8-bit), compute the product as 8-bit (overflowing for |a×b| > 127), and then apply the size cast. This makes the design non-portable: it passes iverilog but silently produces wrong results in tools that don't propagate the outer context into the sub-expression.

Example failure case: a=100, b=100, expected product=10000. In 8-bit: 100×100=10000, truncated to 10000 mod 256=16. `32'(8'd16)` = 32'h00000010 = 16 (wrong).

**Corrected version (mac_correct.v approach):**
```systemverilog
logic signed [15:0] product;
assign product = a * b;   // 16-bit context, no overflow for 8×8

always_ff @(posedge clk) begin
    if (rst)
        out <= '0;
    else
        out <= out + {{16{product[15]}}, product};  // explicit sign extension
end
```

Explicitly declaring a 16-bit intermediate removes the ambiguity: the multiplication is unambiguously 16-bit, and the sign extension to 32 bits is done manually.

---

### Issue 2 — Reset value style: `32'sd0` vs `'0` (mac_llm_A.v, minor)

**Offending lines:**
```systemverilog
out <= 32'sd0;
```

**Why it is ambiguous:**
`32'sd0` is a 32-bit signed zero literal — functionally equivalent to `'0` but unnecessarily verbose. The idiomatic SystemVerilog reset idiom is `'0`, which fills all bits with 0 regardless of the signal width. If `out` is later widened (e.g., to 64-bit accumulator), `32'sd0` would require updating while `'0` adapts automatically.

**Corrected version:**
```systemverilog
out <= '0;
```

---

### Issue 3 — [mac_llm_B.v: fill in after obtaining GPT-4o output]

Common failure modes to check in GPT-4o output:
- `always @(posedge clk)` instead of `always_ff`
- Missing `signed` keyword on port declarations
- `initial` block or `$display` in the module (non-synthesizable)
- Wrong accumulator width (adding 8-bit product into 32-bit without extension)

---

## mac_correct.v — Design Notes

`mac_correct.v` fixes both issues:
1. Explicit 16-bit intermediate `product` with `assign product = a * b` — unambiguous 16-bit multiplication.
2. Explicit sign extension: `{{16{product[15]}}, product}` — portable across all tools.
3. Uses `'0` for reset and `always_ff` for the sequential block.

Compiled cleanly and all 7 testbench steps pass.

---

## Yosys Synthesis

Not available in this environment. To run:
```
yosys -p 'synth; stat' mac_correct.v
```
