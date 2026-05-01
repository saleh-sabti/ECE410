/*
 * interface.sv : AXI4-Stream slave for echo detection chiplet
 *
 * 'interface' is a reserved keyword in SystemVerilog. Module is named axi4s_rx.
 * File is named interface.sv per M2 spec.
 *
 * Ports:
 *   clk        in    1         clock (single domain)
 *   rst        in    1         synchronous active-high reset
 *   s_tvalid   in    1         AXI4-S: master data valid
 *   s_tready   out   1         AXI4-S: slave ready (wired high, no back-pressure)
 *   s_tdata    in   32         AXI4-S: [31:16]=ref_sample, [15:0]=mic_sample
 *   ref_out    out  16         decoded far-end reference sample (signed INT16)
 *   mic_out    out  16         decoded near-end mic sample (signed INT16)
 *   valid_out  out   1         decoded pair valid (1 cycle after TVALID)
 *
 * AXI4-Stream slave (AMBA AXI4-S spec section 2). TREADY wired high.
 * Transaction on every TVALID cycle. No TLAST, TKEEP, or TSTRB.
 * Required data rate: 0.064 MB/s. AXI4-S rated: 400 MB/s. No flow control needed.
 * Single clock domain, synchronous active-high reset.
 */
module axi4s_rx (
    input  logic        clk,
    input  logic        rst,
    // AXI4-Stream slave
    input  logic        s_tvalid,
    output logic        s_tready,
    input  logic [31:0] s_tdata,
    // decoded outputs to compute_core
    output logic signed [15:0] ref_out,
    output logic signed [15:0] mic_out,
    output logic               valid_out
);

    // Always ready: accept every beat; no FIFO or flow control needed at 0.064 MB/s
    assign s_tready = 1'b1;

    always_ff @(posedge clk) begin
        if (rst) begin
            ref_out   <= '0;
            mic_out   <= '0;
            valid_out <= 1'b0;
        end else begin
            valid_out <= s_tvalid;
            if (s_tvalid) begin
                ref_out <= s_tdata[31:16];
                mic_out <= s_tdata[15:0];
            end
        end
    end

endmodule
