`timescale 1ns/1ps
module mac_tb;
    reg              clk, rst;
    reg  signed [7:0]  a, b;
    wire signed [31:0] out;

    integer errors = 0;

    mac dut (.clk(clk), .rst(rst), .a(a), .b(b), .out(out));

    initial clk = 0;
    always #5 clk = ~clk;

    task check;
        input signed [31:0] expected;
        input integer        label;
        begin
            if ($signed(out) !== expected) begin
                $display("FAIL step %0d: out=%0d expected=%0d", label, $signed(out), expected);
                errors = errors + 1;
            end else begin
                $display("PASS step %0d: out=%0d", label, $signed(out));
            end
        end
    endtask

    initial begin
        $dumpfile("mac_tb.vcd");
        $dumpvars(0, mac_tb);

        rst = 1; a = 0; b = 0;
        @(posedge clk); #1;
        check(0, 0);

        // a=3, b=4 for 3 cycles
        rst = 0; a = 3; b = 4;
        @(posedge clk); #1; check(12,  1);
        @(posedge clk); #1; check(24,  2);
        @(posedge clk); #1; check(36,  3);

        // assert rst
        rst = 1;
        @(posedge clk); #1; check(0, 4);

        // a=-5, b=2 for 2 cycles
        rst = 0; a = -5; b = 2;
        @(posedge clk); #1; check(-10, 5);
        @(posedge clk); #1; check(-20, 6);

        if (errors == 0)
            $display("ALL TESTS PASSED");
        else
            $display("%0d TEST(S) FAILED", errors);

        $finish;
    end
endmodule
