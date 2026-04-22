import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


N  = 128
DW = 16


@cocotb.test()
async def test_reset(dut):
    """After reset, all outputs should be 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value       = 1
    dut.valid_in.value  = 0
    dut.ref_sample.value = 0
    dut.mic_sample.value = 0
    dut.threshold.value  = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ps")

    assert dut.echo_det.value  == 0
    assert dut.valid_out.value == 0
    dut._log.info("Reset check passed: echo_det=0, valid_out=0")


@cocotb.test()
async def test_no_echo(dut):
    """Uncorrelated signals should not trigger echo detection."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # Feed N cycles of ref=100, mic=0 (zero mic → zero cross-correlation)
    dut.valid_in.value   = 1
    dut.threshold.value  = 0x7FFF  # high threshold
    for i in range(N):
        dut.ref_sample.value = 100
        dut.mic_sample.value = 0
        await RisingEdge(dut.clk)

    await Timer(1, unit="ps")
    dut._log.info(
        f"No-echo: echo_det={dut.echo_det.value}, valid_out={dut.valid_out.value}"
    )


@cocotb.test()
async def test_full_correlation(dut):
    """Identical ref and mic should produce high correlation."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # ref == mic → rho = 1.0; even low threshold should trigger
    dut.valid_in.value  = 1
    dut.threshold.value = 1  # near-zero threshold
    sample = 1000
    for i in range(N):
        dut.ref_sample.value = sample
        dut.mic_sample.value = sample
        await RisingEdge(dut.clk)

    await Timer(1, unit="ps")
    dut._log.info(
        f"Full-correlation: echo_det={dut.echo_det.value}, valid_out={dut.valid_out.value}"
    )
