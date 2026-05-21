/*
 * tb_top.sv : End-to-end co-simulation testbench for integrated top module
 *
 * Drives the host-side AXI4-Stream interface (no direct compute_core access).
 * Two tests:
 *   Test 1: 128 beats with ref=1, mic=1 → acc_cross=128 >= threshold=64 → echo_det=1 (PASS)
 *   Test 2: 128 beats with ref=1, mic=-1 → acc_cross=-128 < threshold=64 → echo_det=0 (PASS)
 *
 * Independent reference: Python — sum(1*1 for _ in range(128))=128, sum(1*(-1) for _ in range(128))=-128
 *
 * Timing: axi4s_rx adds 1 cycle latency. compute_core needs N+1 valid_in pulses before valid_out.
 * Total: drive N beats → wait 2 more clock edges → sample outputs.
 */

`timescale 1ns/1ps

module tb_top;

    localparam int N    = 128;
    localparam int ACCW = 40;

    logic        clk, rst;
    logic        s_tvalid, s_tready;
    logic [31:0] s_tdata;
    logic signed [ACCW-1:0] threshold;
    logic        echo_det, valid_out;

    top #(.N(N)) dut (
        .clk      (clk),
        .rst      (rst),
        .s_tvalid (s_tvalid),
        .s_tready (s_tready),
        .s_tdata  (s_tdata),
        .threshold(threshold),
        .echo_det (echo_det),
        .valid_out(valid_out)
    );

    // 10 ns clock
    initial clk = 0;
    always #5 clk = ~clk;

    // VCD dump
    initial begin
        $dumpfile("project/m3/sim/cosim.vcd");
        $dumpvars(0, tb_top);
    end

    // Send n AXI-S beats then wait a few cycles for output to register.
    // compute_core needs N+1 valid_in pulses; interface adds 1 cycle latency,
    // so caller must pass n = N+1 to see the first valid echo_det output.
    task automatic send_beats(input logic [15:0] ref_val, mic_val, input int n);
        integer i;
        for (i = 0; i < n; i++) begin
            @(negedge clk);
            s_tvalid = 1'b1;
            s_tdata  = {ref_val, mic_val};
        end
        @(negedge clk);
        s_tvalid = 1'b0;
        s_tdata  = '0;
        repeat (4) @(posedge clk);
    endtask

    integer pass_count;
    initial begin
        pass_count = 0;
        rst       = 1'b1;
        s_tvalid  = 1'b0;
        s_tdata   = '0;
        threshold = 40'sd64;

        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        // --- Test 1: ref=1, mic=1, expect echo_det=1 ---
        // Python ref: sum(1*1 for _ in range(128)) = 128 >= 64 → echo_det=1
        // N+1 beats: interface latency (1 cycle) + N valid_in needed to fill window + 1 to register output
        send_beats(16'sd1, 16'sd1, N + 1);
        if (echo_det === 1'b1) begin
            $display("Test 1 PASS: ref=1, mic=1, echo_det=%0b (expected 1)", echo_det);
            pass_count++;
        end else begin
            $display("Test 1 FAIL: ref=1, mic=1, echo_det=%0b (expected 1)", echo_det);
        end

        // Reset between tests
        @(negedge clk);
        rst = 1'b1;
        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        // --- Test 2: ref=1, mic=-1, expect echo_det=0 ---
        // Python ref: sum(1*(-1) for _ in range(128)) = -128 < 64 → echo_det=0
        send_beats(16'sd1, 16'sd1 * (-1), N + 1);
        if (echo_det === 1'b0) begin
            $display("Test 2 PASS: ref=1, mic=-1, echo_det=%0b (expected 0)", echo_det);
            pass_count++;
        end else begin
            $display("Test 2 FAIL: ref=1, mic=-1, echo_det=%0b (expected 0)", echo_det);
        end

        if (pass_count == 2)
            $display("PASS: 2/2 tests passed");
        else
            $display("FAIL: %0d/2 tests passed", pass_count);

        #20;
        $finish;
    end

endmodule
