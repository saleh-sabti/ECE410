// Echo detection compute core — normalized cross-correlation
// N: window size (samples), DW: data width per sample
// Inputs are INT16 audio samples (ref = far-end, mic = near-end)
// Output: 1-bit echo_det (1 = rho >= threshold)
module echo_detect_core #(
    parameter int N  = 128,
    parameter int DW = 16
) (
    input  logic             clk,
    input  logic             rst,
    input  logic             valid_in,
    input  logic signed [DW-1:0] ref_sample,
    input  logic signed [DW-1:0] mic_sample,
    input  logic [DW-1:0]    threshold,
    output logic             echo_det,
    output logic             valid_out
);

    // Shift registers hold N samples of ref and mic
    logic signed [DW-1:0] ref_buf [0:N-1];
    logic signed [DW-1:0] mic_buf [0:N-1];

    // Accumulator widths: DW*2 + log2(N) to avoid overflow
    // For N=128, DW=16: 32 + 7 = 39 bits; use 48 for margin
    localparam int ACCW = DW * 2 + $clog2(N) + 1;

    logic signed [ACCW-1:0] acc_cross;  // sum(ref[i] * mic[i])
    logic signed [ACCW-1:0] acc_ref;    // sum(ref[i]^2)
    logic signed [ACCW-1:0] acc_mic;    // sum(mic[i]^2)

    // Shift registers and accumulation
    always_ff @(posedge clk) begin
        if (rst) begin
            for (int i = 0; i < N; i++) begin
                ref_buf[i] <= '0;
                mic_buf[i] <= '0;
            end
            acc_cross <= '0;
            acc_ref   <= '0;
            acc_mic   <= '0;
            echo_det  <= 1'b0;
            valid_out <= 1'b0;
        end else if (valid_in) begin
            // Shift in new samples
            ref_buf[0] <= ref_sample;
            mic_buf[0] <= mic_sample;
            for (int i = 1; i < N; i++) begin
                ref_buf[i] <= ref_buf[i-1];
                mic_buf[i] <= mic_buf[i-1];
            end

            // Recompute accumulators over the full window each cycle
            // (placeholder: full parallel MAC array goes here for M2)
            acc_cross <= '0;
            acc_ref   <= '0;
            acc_mic   <= '0;
            for (int i = 0; i < N; i++) begin
                acc_cross <= acc_cross + {{(ACCW-DW*2){ref_buf[i][DW-1] ^ mic_buf[i][DW-1]}},
                                          ref_buf[i] * mic_buf[i]};
                acc_ref   <= acc_ref   + {{(ACCW-DW*2){ref_buf[i][DW-1]}},
                                          ref_buf[i] * ref_buf[i]};
                acc_mic   <= acc_mic   + {{(ACCW-DW*2){mic_buf[i][DW-1]}},
                                          mic_buf[i] * mic_buf[i]};
            end

            // Threshold compare (full normalizer replaced by scaled compare for stub)
            // rho >= tau  <=>  acc_cross >= tau * sqrt(acc_ref * acc_mic)
            // Stub: compare acc_cross against scaled threshold (M2 will add sqrt unit)
            echo_det  <= (acc_cross >= $signed({{(ACCW-DW){1'b0}}, threshold}));
            valid_out <= 1'b1;
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
