/*
 * top.sv : Integrated top module — echo detection chiplet
 *
 * Ports:
 *   clk        in    1         clock (single domain)
 *   rst        in    1         synchronous active-high reset
 *   s_tvalid   in    1         AXI4-S: master data valid
 *   s_tready   out   1         AXI4-S: slave ready
 *   s_tdata    in   32         AXI4-S: [31:16]=ref_sample, [15:0]=mic_sample
 *   threshold  in   40         echo detection threshold (host-configured)
 *   echo_det   out   1         1 = echo detected
 *   valid_out  out   1         echo_det is valid
 *
 * Instantiates axi4s_rx (interface.sv) and compute_core.
 * No glue logic required: axi4s_rx.valid_out drives compute_core.valid_in directly.
 * Single clock domain, synchronous active-high reset.
 */
module top #(
    parameter int N    = 128,
    parameter int DW   = 16,
    parameter int ACCW = 40
) (
    input  logic                    clk,
    input  logic                    rst,
    input  logic                    s_tvalid,
    output logic                    s_tready,
    input  logic [31:0]             s_tdata,
    input  logic signed [ACCW-1:0] threshold,
    output logic                    echo_det,
    output logic                    valid_out
);

    logic signed [DW-1:0] ref_sample;
    logic signed [DW-1:0] mic_sample;
    logic                 sample_valid;

    axi4s_rx u_rx (
        .clk      (clk),
        .rst      (rst),
        .s_tvalid (s_tvalid),
        .s_tready (s_tready),
        .s_tdata  (s_tdata),
        .ref_out  (ref_sample),
        .mic_out  (mic_sample),
        .valid_out(sample_valid)
    );

    compute_core #(.N(N), .DW(DW), .ACCW(ACCW)) u_core (
        .clk      (clk),
        .rst      (rst),
        .valid_in (sample_valid),
        .ref_in   (ref_sample),
        .mic_in   (mic_sample),
        .threshold(threshold),
        .echo_det (echo_det),
        .valid_out(valid_out)
    );

endmodule
