`timescale 1ns/1ps

// tb_interface.sv  —  Testbench for axi4s_rx (interface.sv)
//
// Test 1 (write): TVALID=1, TDATA=32'hABCD_1234 -> ref_out=0xABCD, mic_out=0x1234, valid_out=1
// Test 2 (idle):  TVALID=0                       -> valid_out=0
// Test 3 (back-to-back): two consecutive beats, verify each decoded independently

module tb_interface;

    logic        clk, rst;
    logic        s_tvalid, s_tready;
    logic [31:0] s_tdata;
    logic signed [15:0] ref_out, mic_out;
    logic        valid_out;

    axi4s_rx dut (
        .clk(clk), .rst(rst),
        .s_tvalid(s_tvalid), .s_tready(s_tready), .s_tdata(s_tdata),
        .ref_out(ref_out), .mic_out(mic_out), .valid_out(valid_out)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("project/m2/sim/interface.vcd");
        $dumpvars(0, tb_interface);
    end

    integer pass_cnt, fail_cnt;

    initial begin
        pass_cnt = 0; fail_cnt = 0;
        rst = 1; s_tvalid = 0; s_tdata = 0;
        repeat(3) @(posedge clk);
        @(negedge clk); rst = 0;

        // ---- Test 1: single write transaction ----
        // Set TVALID and TDATA before the posedge; outputs are registered at posedge
        @(negedge clk);
        s_tvalid = 1; s_tdata = 32'hABCD_1234;
        @(posedge clk); #1;  // outputs registered here
        if (valid_out === 1'b1 && ref_out === 16'hABCD && mic_out === 16'h1234) begin
            $display("PASS  test1: ref_out=0xABCD mic_out=0x1234 valid_out=1");
            pass_cnt++;
        end else begin
            $display("FAIL  test1: ref_out=%h mic_out=%h valid_out=%0b", ref_out, mic_out, valid_out);
            fail_cnt++;
        end

        // ---- Test 2: idle (TVALID=0) ----
        @(negedge clk); s_tvalid = 0;
        @(posedge clk); #1;
        if (valid_out === 1'b0) begin
            $display("PASS  test2: valid_out=0 when TVALID=0");
            pass_cnt++;
        end else begin
            $display("FAIL  test2: valid_out=%0b expected 0", valid_out);
            fail_cnt++;
        end

        // ---- Test 3: back-to-back beats ----
        @(negedge clk); s_tvalid = 1; s_tdata = 32'h0001_0002;
        @(posedge clk); #1;  // beat 1 registered
        if (valid_out === 1'b1 && ref_out === 16'h0001 && mic_out === 16'h0002) begin
            $display("PASS  test3a: beat1 ref=1 mic=2 valid_out=1");
            pass_cnt++;
        end else begin
            $display("FAIL  test3a: ref_out=%h mic_out=%h valid_out=%0b", ref_out, mic_out, valid_out);
            fail_cnt++;
        end
        @(negedge clk); s_tdata = 32'h0003_0004;  // TVALID still 1
        @(posedge clk); #1;  // beat 2 registered
        if (valid_out === 1'b1 && ref_out === 16'h0003 && mic_out === 16'h0004) begin
            $display("PASS  test3b: beat2 ref=3 mic=4 valid_out=1");
            pass_cnt++;
        end else begin
            $display("FAIL  test3b: ref_out=%h mic_out=%h valid_out=%0b", ref_out, mic_out, valid_out);
            fail_cnt++;
        end
        @(negedge clk); s_tvalid = 0;

        // ---- Summary ----
        if (fail_cnt == 0)
            $display("PASS  axi4s_rx: %0d/4 tests passed", pass_cnt);
        else
            $display("FAIL  axi4s_rx: %0d test(s) failed", fail_cnt);

        $finish;
    end

endmodule
