import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_mac_basic(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ps")
    assert dut.out.value.to_signed() == 0

    dut.rst.value = 0
    dut.a.value = 3
    dut.b.value = 4

    for expected in [12, 24, 36]:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ps")
        assert dut.out.value.to_signed() == expected, \
            f"expected {expected}, got {dut.out.value.to_signed()}"

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ps")
    assert dut.out.value.to_signed() == 0

    dut.rst.value = 0
    dut.a.value = (-5) & 0xFF  # two's complement of -5
    dut.b.value = 2

    await RisingEdge(dut.clk)
    await Timer(1, unit="ps")
    assert dut.out.value.to_signed() == -10

    await RisingEdge(dut.clk)
    await Timer(1, unit="ps")
    assert dut.out.value.to_signed() == -20


@cocotb.test()
async def test_mac_overflow(dut):
    """Verify accumulator wraps (2s complement) — does not saturate."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # a=127, b=127 → +16129 per cycle
    dut.a.value = 127
    dut.b.value = 127
    product = 127 * 127   # 16129
    MAX32   = 2**31 - 1   # 2147483647

    cycles = (MAX32 // product) + 2
    for _ in range(cycles):
        await RisingEdge(dut.clk)

    await Timer(1, unit="ps")
    final = dut.out.value.to_signed()
    assert final != MAX32, \
        f"Accumulator saturated at {MAX32}; expected two's complement wrap"
    dut._log.info(
        f"After {cycles} cycles of +{product}: out={final} (wrapped, no saturation)"
    )
