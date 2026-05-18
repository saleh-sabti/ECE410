# M3 Plan — compute_core

The synthesis numbers point to one fix: pipeline the MAC tree. 243,521 cells and a 113.5 ns critical path both come from 128 multipliers feeding an unregistered 7-level adder tree in a single clock cycle. The default floorplan cannot route that many cells.

For M3 I will add pipeline registers after level 3-4 of the adder reduction. That splits the 113.5 ns path into two stages of roughly 55 ns each, targeting a 20 ns clock (50 MHz) on sky130. Latency increases by one cycle; throughput is unchanged: one result per valid_in cycle once the pipeline fills.

I will also increase the floorplan area (DIE_AREA in config.json). If routing still fails after pipelining, I will drop N from 128 to 64, cutting cell count by roughly 4x.

Target: routing completes at 20 ns clock, no DRT failures.
