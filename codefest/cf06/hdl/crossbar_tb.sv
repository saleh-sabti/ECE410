// Testbench for crossbar_mac
// Weights: [[1,-1,1,-1],[1,1,-1,-1],[-1,1,1,-1],[-1,-1,-1,1]]
// Inputs: in = [10, 20, 30, 40]
// Expected: out = [-40, 0, -20, -20]
module crossbar_tb;

    logic             clk, rst, load;
    logic [15:0]      wdata;
    logic signed [7:0] in0, in1, in2, in3;
    logic signed [9:0] out0, out1, out2, out3;

    crossbar_mac dut (.*);

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("crossbar_tb.vcd");
        $dumpvars(0, crossbar_tb);

        rst = 1; load = 0; wdata = 0;
        in0 = 0; in1 = 0; in2 = 0; in3 = 0;
        @(posedge clk); #1;
        rst = 0;

        // load weights
        // w[i][j] = wdata[4*i+j], 1=+1, 0=-1
        // row0=[1,-1,1,-1]: bits[3:0]  = 4'b0101
        // row1=[1,1,-1,-1]:  bits[7:4]  = 4'b0011
        // row2=[-1,1,1,-1]: bits[11:8] = 4'b0110
        // row3=[-1,-1,-1,1]: bits[15:12]= 4'b1000
        wdata = 16'b1000_0110_0011_0101;
        load = 1;
        @(posedge clk); #1;
        load = 0;

        // apply inputs
        in0 = 8'sd10; in1 = 8'sd20; in2 = 8'sd30; in3 = 8'sd40;
        @(posedge clk); #1;

        $display("out0 = %0d  (expected -40)", $signed(out0));
        $display("out1 = %0d  (expected  0)",  $signed(out1));
        $display("out2 = %0d  (expected -20)", $signed(out2));
        $display("out3 = %0d  (expected -20)", $signed(out3));

        if ($signed(out0)==-40 && $signed(out1)==0 &&
            $signed(out2)==-20 && $signed(out3)==-20)
            $display("PASS: all outputs match");
        else
            $display("FAIL");

        $finish;
    end

endmodule
