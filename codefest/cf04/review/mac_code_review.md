# CF4 CLLM — MAC Code Review

## LLM Assignments

| File | LLM | Model Version |
|------|-----|---------------|
| mac_llm_A.v | Claude | Claude Sonnet 4.6 |
| mac_llm_B.v | Gemini | Gemini 3.1 Pro |

---

## Compilation Results

**mac_llm_A.v:**
```
iverilog -g2012 -o mac_llm_A_sim mac_llm_A.v mac_tb.v
→ No errors, no warnings.
```

**mac_llm_B.v:**
```
iverilog -g2012 -o mac_llm_B_sim mac_llm_B.v mac_tb.v
→ No errors, no warnings.
```

---

## Simulation Results

Testbench: `mac_tb.v`. Sequence: a=3,b=4 for 3 cycles (12→24→36), rst (→0), a=−5,b=2 for 2 cycles (−10→−20).

### mac_llm_A.v (Claude Sonnet 4.6)

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

### mac_llm_B.v (Gemini 3.1 Pro)

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

### mac_correct.v

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

### Issue 1: Over-sized multiplier (mac_llm_B.v, Gemini)

**Offending lines:**
```systemverilog
out <= out + (signed'(32'(a)) * signed'(32'(b)));
```

**Why it is wrong:**
The cast `32'(a)` widens `a` from 8 bits to 32 bits before multiplication. So `signed'(32'(a)) * signed'(32'(b))` is a full 32×32-bit multiply. The spec inputs are 8-bit signed values. The correct hardware intent is an 8×8 multiply producing a 16-bit signed product, which is then sign-extended and accumulated into 32 bits. A 32×32 multiplier requires roughly 4–16× more logic (DSPs or LUTs) than a 16-bit product path. In a custom chiplet where area is the design constraint, this is a direct area cost with no benefit: the upper 24 bits of each operand are just sign-extended zeros.

**Corrected version:**
```systemverilog
logic signed [15:0] product;
assign product = a * b;                          // 8×8 → 16-bit
out <= out + {{16{product[15]}}, product};        // sign-extend to 32
```

---

### Issue 2: Redundant `signed'()` outer cast (mac_llm_B.v, Gemini)

**Offending lines:**
```systemverilog
out <= out + (signed'(32'(a)) * signed'(32'(b)));
```

**Why it is ambiguous:**
`a` is declared `logic signed [7:0]`. Per IEEE 1800-2017 §6.24.1, a size cast `32'(expr)` sign-extends or zero-extends based on the signedness of the operand. Since `a` is signed, `32'(a)` already produces a signed 32-bit value. The outer `signed'()` is a no-op — it re-declares something that is already signed. This double-cast pattern suggests the model was uncertain about whether `32'()` preserves signedness, and guarded against it redundantly. The comment ("forces the synthesizer to perform the sign extension first") is correct in intent but incorrect in explaining which cast actually does the work.

**Corrected version:**
```systemverilog
// 32'(a) already sign-extends since a is signed; signed'() is redundant
out <= out + (32'(a) * 32'(b));
// Better yet: use explicit 16-bit intermediate (Issue 1 fix)
```

---

### Issue 3: Sign extension ambiguity via implicit size cast (mac_llm_A.v, Claude)

**Offending lines:**
```systemverilog
out <= out + 32'(a * b);
```

**Why it is ambiguous:**
`a * b` is a sub-expression with self-determined width of 8 bits (both operands are 8-bit). The `32'()` cast then applies to the 8-bit product. In iverilog, the outer context extends operands to 32 bits before the multiply, so the result is correct. In Verilator and some synthesis linters, `a * b` is computed as 8-bit first, then `32'()` zero-extends, giving wrong results for negative products where the 8-bit result has its MSB set. The behavior is tool-dependent and produces no compile-time warning.

Example failure: `a = −5 (0xFB), b = 2 → a*b = −10 (0xF6 as 8-bit). 32'(0xF6)` = `32'h000000F6` = 246 (wrong) in tools that evaluate self-determined first.

**Corrected version:**
```systemverilog
logic signed [15:0] product;
assign product = a * b;
out <= out + {{16{product[15]}}, product};
```

---

## mac_correct.v — Design Summary

`mac_correct.v` avoids all three issues:
1. 16-bit explicit intermediate (`assign product = a * b`) → 8×8 multiply only.
2. No ambiguous casts — the product width is unambiguous.
3. Explicit sign extension via `{{16{product[15]}}, product}` — portable across iverilog, Verilator, and synthesis tools.

Compiled cleanly, all 7 testbench steps pass.

---

## Yosys Synthesis

Not available in this environment. To run:
```
yosys -p 'synth; stat' mac_correct.v
```
