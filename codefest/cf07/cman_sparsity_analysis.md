# CMAN Sparsity Breakeven Analysis
**ECE 410/510 | Codefest 7 | Spring 2026**

N=512, s = fraction of zeros, FP32 weights (4 bytes/element), BW = 320 GB/s

---

## (a) Expressions for Dense and Sparse Compute/Memory

### Dense

```
Dense FLOPs  = 2 × N²  = 2 × 512²  = 524,288 FLOPs
Dense bytes  = 4 × N²  = 4 × 512²  = 1,048,576 bytes
```

### Sparse (CSR)

nnz = N²(1-s)

```
Sparse FLOPs  = 2 × N²(1-s)

Sparse bytes  = values array   : 4 × N²(1-s)     (one FP32 per nonzero)
              + col_idx array  : 4 × N²(1-s)     (one INT32 per nonzero)
              + row_ptr array  : 4 × (N+1)        (one INT32 per row pointer)
              = 8N²(1-s) + 4(N+1)
```

---

## (b) FLOPs Speedup and s for 2x

```
Speedup = Dense FLOPs / Sparse FLOPs
        = 2N² / 2N²(1-s)
        = 1 / (1-s)
```

Set speedup = 2:

```
1 / (1-s) = 2
1-s = 0.5
s = 0.5
```

> **FLOPs speedup = 1/(1-s). At s = 0.5 (50% sparsity) the speedup is exactly 2x.**

---

## (c) Memory Breakeven Sparsity

Set sparse bytes = dense bytes:

```
8N²(1-s) + 4(N+1) = 4N²

8N²(1-s) = 4N² - 4(N+1)

1-s = [4N² - 4(N+1)] / 8N²
    = 0.5 - (N+1) / 2N²

s = 0.5 + (N+1) / 2N²
```

Plug in N=512:

```
s = 0.5 + 513 / (2 × 262144)
  = 0.5 + 513 / 524288
  = 0.5 + 0.000978
  ≈ 0.501
```

> **Above s ≈ 0.501 (just over 50% sparsity), CSR uses less memory than dense storage.**

---

## (d) End-to-End Speedup at s=0.9, BW = 320 GB/s

```
Dense bytes  = 4 × N²
             = 4 × 262,144
             = 1,048,576 bytes

Sparse bytes = 8 × N²(1-s) + 4(N+1)
             = 8 × 262,144 × 0.1 + 4 × 513
             = 209,715 + 2,052
             = 211,767 bytes

Dense time   = 1,048,576 / (320 × 10⁹) = 3.277 µs
Sparse time  = 211,767   / (320 × 10⁹) = 0.662 µs

Speedup = 3.277 / 0.662 ≈ 4.95x
```

> **At s=0.9, a memory-bandwidth-limited system runs the sparse MVM about 5x faster than dense.**
