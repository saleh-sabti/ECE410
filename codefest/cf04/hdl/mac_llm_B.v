// LLM B: Gemini 3.1 Pro
module mac (
    input  logic               clk,
    input  logic               rst,
    input  logic signed [7:0]  a,
    input  logic signed [7:0]  b,
    output logic signed [31:0] out
);

    always_ff @(posedge clk) begin
        if (rst) begin
            out <= 32'sd0;
        end else begin
            // We explicitly cast the 8-bit signed inputs to 32-bit signed values
            // before multiplication to guarantee proper sign extension and prevent
            // the accumulation from overflowing or treating the product as unsigned.
            out <= out + (signed'(32'(a)) * signed'(32'(b)));
        end
    end

endmodule
