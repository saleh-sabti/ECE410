# M3 Plan — compute_core

The synthesis numbers point to one fix: pipeline the MAC tree. 243,521 cells and a 113.5 ns critical path both come from 128 multipliers feeding an unregistered 7-level adder tree in one clock cycle. The default floorplan cannot route that many cells.

For M3 I will add pipeline registers after level 3-4 of the adder reduction, splitting the 113.5 ns path into two ~55 ns stages and targeting a 20 ns clock (50 MHz). Latency increases by one cycle; throughput is unchanged: one result per valid_in cycle once the pipeline fills.

I will also increase DIE_AREA in config.json. If routing still fails, N drops from 128 to 64, cutting cell count by roughly 4x.

Target: routing completes at 20 ns, no DRT failures.
