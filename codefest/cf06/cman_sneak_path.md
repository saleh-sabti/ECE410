# CF6 CMAN: Sneak Paths in a Resistive Crossbar

2x2 crossbar, rows are inputs, columns sense current.

R[0][0] = 1 kΩ (on), R[0][1] = 2 kΩ (off), R[1][0] = 2 kΩ (off), R[1][1] = 1 kΩ (on).

---

## (a) Ideal Read

Conditions: V_row0 = 1V, col0 = 0V, row1 = 0V, col1 = 0V.

Row1 is grounded so no current comes from it. Only R[0][0] matters here.

```
I_col0 = V_row0 / R[0][0] + V_row1 / R[1][0]
       = 1V / 1kΩ + 0V / 2kΩ
       = 1 mA
```

**I_col0 (ideal) = 1 mA**

---

## (b) Sneak Path Read: KCL for Floating Nodes

Conditions: V_row0 = 1V, col0 = 0V. Row1 and col1 are floating.

Since row1 is floating it's not grounded anymore, so it can pick up a voltage through the crossbar. I need to find V_row1 and V_col1 using KCL.

**KCL at V_row1:**

Row1 is floating so no external current. The currents through R[1][0] (to col0) and R[1][1] (to col1) have to sum to zero.

```
(V_row1 - 0) / 2k + (V_row1 - V_col1) / 1k = 0

multiply by 2k:
V_row1 + 2(V_row1 - V_col1) = 0
3*V_row1 - 2*V_col1 = 0    ...(1)
```

**KCL at V_col1:**

Col1 is also floating. Currents from row0 through R[0][1] and from row1 through R[1][1] must also sum to zero.

```
(1 - V_col1) / 2k + (V_row1 - V_col1) / 1k = 0

multiply by 2k:
(1 - V_col1) + 2(V_row1 - V_col1) = 0
2*V_row1 - 3*V_col1 = -1    ...(2)
```

**Solving (1) and (2):**

From (1): V_col1 = 1.5 * V_row1

Sub into (2):
```
2*V_row1 - 3*(1.5*V_row1) = -1
2*V_row1 - 4.5*V_row1 = -1
-2.5*V_row1 = -1
V_row1 = 0.4 V
V_col1 = 0.6 V
```

Quick check:
- At V_row1: 0.4/2k + (0.4-0.6)/1k = 0.2 - 0.2 = 0 mA ✓
- At V_col1: (1-0.6)/2k + (0.4-0.6)/1k = 0.2 - 0.2 = 0 mA ✓

**V_row1 = 0.4 V, V_col1 = 0.6 V**

Note: you can also see this as a voltage divider. The sneak path is a series chain R[0][1] + R[1][1] + R[1][0] = 2k + 1k + 2k = 5k, so sneak current = 1V/5k = 0.2 mA and the node voltages fall out the same way.

---

## (c) Actual I_col0 with Sneak Path

The sneak current travels: row0 (1V) -> R[0][1] -> col1 (0.6V) -> R[1][1] -> row1 (0.4V) -> R[1][0] -> col0 (0V), and it gets counted in the col0 sense current.

```
I_col0 = 1V / 1kΩ + 0.4V / 2kΩ
       = 1 mA + 0.2 mA
       = 1.2 mA
```

Intended path (row0 -> R[0][0] -> col0): 1.0 mA
Sneak path (row0 -> R[0][1] -> col1 -> R[1][1] -> row1 -> R[1][0] -> col0): 0.2 mA
Actual I_col0 = 1.2 mA

That's 20% more than the ideal read.

---

## (d) How Sneak Paths Corrupt MVM

Col0 is only supposed to see current from the selected row. But row1 floated to 0.4V because it's connected to row0 through the off-state resistors, and that pushed 0.2 mA into col0 from a row that was never driven. In a real crossbar with many rows, every undriven row adds its own sneak current to every sensed column. The errors add up fast and the output current stops representing the actual weights.
