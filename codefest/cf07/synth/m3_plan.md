# M3 Plan — compute_core

The synthesis result makes the problem clear: 243,521 cells and a 113.5 ns critical path are both caused by the same thing — 128 multipliers feeding an unregistered 7-level adder tree in a single combinational stage. Routing fails because the cell count exceeds what the default floorplan can route.

For M3 I will pipeline the MAC tree. The plan is to register the adder tree at the halfway point (after level 3-4 of the reduction), splitting the 113.5 ns path into two ~55 ns stages. That brings the clock target to roughly 20 ns (50 MHz), which is achievable on sky130. This adds one cycle of latency but does not change the throughput for streaming audio — one result still comes out every valid_in cycle once the pipeline is full.

I will also increase the floorplan die area in the config (DIE_AREA parameter) to give the router enough space for the cell count. If routing still fails after pipelining I will reduce N from 128 to 64, which cuts cells by roughly 4x.

Target for M3: synthesis completes routing at 20 ns clock, no DRT failures.
