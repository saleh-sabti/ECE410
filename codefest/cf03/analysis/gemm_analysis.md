# GEMM Roofline Analysis
ECE 410/510 Spring 2026 | Saleh Sabti

---

## Why the naive kernel is memory-bound

- Each thread loads a full row of A and full column of B from global memory. No element is reused across threads.
- DRAM traffic for N=1024: 8N^3 bytes = 8.59 GB. Arithmetic intensity = 0.25 FLOP/byte.
- RTX 4050 Laptop ridge = 18.7 FLOP/byte. At 0.25, the kernel is theoretically **memory-bound**.
- DRAM-bound ceiling = 192 GB/s x 0.25 = 48 GFLOP/s. Measured: **508 GFLOP/s**.

## How tiling reduces DRAM traffic

- 8x8 tiles of A and B load into shared memory once per tile step. Each element is reused 8 times before the tile advances.
- DRAM traffic drops 8x from 8N^3 to N^3 bytes. Arithmetic intensity rises to 2.0 FLOP/byte.
- Shared memory is on-chip. Those 8 reuses cost no DRAM bandwidth.

## Whether the improvement matched expectations

- Tiled measured: **493 GFLOP/s**, about the same as naive (508 GFLOP/s). The expected 8x speedup did not appear.
- The reason: at N=1024, all three matrices total 12 MB and fit inside the RTX 4050 Laptop's L2 cache. The naive kernel gets hardware-managed reuse for free, so shared memory tiling adds no benefit at this size.
- T=8 also has small tiles, so the __syncthreads() overhead partially offsets any gain.
- Both kernels sit well below peak compute (3588 GFLOP/s). The remaining bottleneck is L2 cache bandwidth, not DRAM and not compute.
