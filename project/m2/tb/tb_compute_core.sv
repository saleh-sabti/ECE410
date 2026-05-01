`timescale 1ns/1ps

// tb_compute_core.sv : Testbench for compute_core
//
// Test 1 (echo): ref=1, mic=1 for N=128 samples. acc_cross=128, threshold=64. Expect echo_det=1.
// Test 2 (no echo): ref=1, mic=-1. acc_cross=-128. Expect echo_det=0.
// Reference: Python sum(1*1 for _ in range(128)) = 128, sum(1*-1 for _ in range(128)) = -128.

module tb_compute_core;

    parameter int N    = 128;
    parameter int DW   = 16;
    parameter int ACCW = 40;

    logic                    clk, rst, valid_in;
    logic signed [DW-1:0]   ref_in, mic_in;
    logic signed [ACCW-1:0] threshold;
    logic                    echo_det, valid_out;

    compute_core #(.N(N), .DW(DW), .ACCW(ACCW)) dut (
        .clk(clk), .rst(rst), .valid_in(valid_in),
        .ref_in(ref_in), .mic_in(mic_in),
        .threshold(threshold),
        .echo_det(echo_det), .valid_out(valid_out)
    );

    // 10 ns clock
    initial clk = 0;
    always #5 clk = ~clk;

    // Waveform dump
    initial begin
        $dumpfile("project/m2/sim/compute_core.vcd");
        $dumpvars(0, tb_compute_core);
    end

    integer pass_cnt, fail_cnt;

    task automatic reset_dut;
        rst = 1; valid_in = 0; ref_in = 0; mic_in = 0;
        threshold = 40'sd64;
        repeat(3) @(posedge clk);
        @(negedge clk); rst = 0;
    endtask

    // Send N+1 samples so window fills; task ends at the posedge where outputs are valid
    // Caller must read outputs immediately after return, then clear valid_in
    task automatic send_samples(input logic signed [DW-1:0] rval, mval);
        integer k;
        for (k = 0; k <= N; k++) begin
            @(negedge clk);
            valid_in = 1;
            ref_in   = rval;
            mic_in   = mval;
        end
        @(posedge clk); #1;  // outputs registered here (window_full=1, valid_in=1)
    endtask

    initial begin
        pass_cnt = 0; fail_cnt = 0;

        // ---- Test 1: perfect echo (ref=1, mic=1) ----
        reset_dut();
        send_samples(16'sd1, 16'sd1);
        // Expected: acc_cross = 128 >= threshold=64  =>  echo_det=1, valid_out=1
        if (valid_out === 1'b1 && echo_det === 1'b1) begin
            $display("PASS  test1: echo_det=1 valid_out=1 (acc_cross=128 >= 64)");
            pass_cnt++;
        end else begin
            $display("FAIL  test1: echo_det=%0b valid_out=%0b (expected 1,1)", echo_det, valid_out);
            fail_cnt++;
        end
        @(negedge clk); valid_in = 0;

        // ---- Test 2: anti-correlated (ref=1, mic=-1) ----
        reset_dut();
        send_samples(16'sd1, -16'sd1);
        // Expected: acc_cross = -128 < threshold=64  =>  echo_det=0, valid_out=1
        if (valid_out === 1'b1 && echo_det === 1'b0) begin
            $display("PASS  test2: echo_det=0 valid_out=1 (acc_cross=-128 < 64)");
            pass_cnt++;
        end else begin
            $display("FAIL  test2: echo_det=%0b valid_out=%0b (expected 0,1)", echo_det, valid_out);
            fail_cnt++;
        end
        @(negedge clk); valid_in = 0;

        // ---- Summary ----
        if (fail_cnt == 0)
            $display("PASS  compute_core: %0d/2 tests passed", pass_cnt);
        else
            $display("FAIL  compute_core: %0d test(s) failed", fail_cnt);

        $finish;
    end

endmodule
