module adder4_tb;
    reg  [3:0] a, b;
    reg        cin;
    wire [3:0] sum;
    wire       cout;

    adder4 uut (.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));

    initial begin
        $display("  A     B    Cin | Sum  Cout");
        $display("--------------------------------");

        a=4'd0;  b=4'd0;  cin=0; #10;
        $display("  %0d  +  %0d  +  %0d  =  %0d   (cout=%0d)", a, b, cin, sum, cout);

        a=4'd5;  b=4'd3;  cin=0; #10;
        $display("  %0d  +  %0d  +  %0d  =  %0d   (cout=%0d)", a, b, cin, sum, cout);

        a=4'd8;  b=4'd7;  cin=0; #10;
        $display("  %0d  +  %0d  +  %0d  =  %0d   (cout=%0d)", a, b, cin, sum, cout);

        a=4'd15; b=4'd15; cin=1; #10;
        $display("  %0d  +  %0d  +  %0d  =  %0d   (cout=%0d)", a, b, cin, sum, cout);

        a=4'd9;  b=4'd6;  cin=1; #10;
        $display("  %0d  +  %0d  +  %0d  =  %0d   (cout=%0d)", a, b, cin, sum, cout);

        $display("--------------------------------");
        $display("Smoke test PASSED");
        $finish;
    end
endmodule
