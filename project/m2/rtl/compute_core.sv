/*
 * compute_core.sv  —  Echo detection compute core
 *
 * Ports:
 *   clk        in    1         clock (single domain)
 *   rst        in    1         synchronous active-high reset
 *   valid_in   in    1         input sample pair is valid this cycle
 *   ref_in     in   DW         far-end reference sample (signed INT16)
 *   mic_in     in   DW         near-end mic sample (signed INT16)
 *   threshold  in   ACCW       echo threshold in accumulated cross-correlation units
 *   echo_det   out   1         1 = echo detected (acc_cross >= threshold)
 *   valid_out  out   1         output valid; asserted one cycle after window fills
 *
 * Algorithm: unnormalized cross-correlation Σref[i]*mic[i] vs threshold.
 *   Full normalization (÷ sqrt(ref_energy * mic_energy)) deferred; documented in precision.md.
 * Precision: INT16 samples, 40-bit signed accumulators (32-bit product + 8 overhead bits).
 * Clock domain: single. Reset: synchronous, active-high.
 * Latency: outputs valid N+1 valid_in cycles after reset (window fill).
 */
module compute_core #(
    parameter int N    = 128,
    parameter int DW   = 16,
    parameter int ACCW = 40    // DW*2 + ceil(log2(N)) + 1 = 32+7+1
) (
    input  logic                    clk,
    input  logic                    rst,
    input  logic                    valid_in,
    input  logic signed [DW-1:0]   ref_in,
    input  logic signed [DW-1:0]   mic_in,
    input  logic signed [ACCW-1:0] threshold,
    output logic                    echo_det,
    output logic                    valid_out
);

    localparam int CNTW = $clog2(N) + 1;  // 8 bits for N=128

    logic signed [DW-1:0]   ref_buf [0:N-1];
    logic signed [DW-1:0]   mic_buf [0:N-1];
    logic [CNTW-1:0]        win_cnt;

    // window_full goes high combinationally once win_cnt reaches N
    logic window_full;
    assign window_full = (win_cnt == CNTW'(N));

    // Sign-extend buffers to ACCW bits (combinational, synthesizes as wires)
    logic signed [ACCW-1:0] ref_e [0:N-1];
    logic signed [ACCW-1:0] mic_e [0:N-1];
    genvar g;
    generate
        for (g = 0; g < N; g++) begin : sign_ext
            assign ref_e[g] = ACCW'(ref_buf[g]);  // signed assignment sign-extends
            assign mic_e[g] = ACCW'(mic_buf[g]);
        end
    endgenerate

    // Parallel MAC tree: N multipliers evaluated combinationally each cycle
    logic signed [ACCW-1:0] acc_cross;

    always_comb begin : mac_tree
        acc_cross = '0;
        for (int i = 0; i < N; i++)
            acc_cross = acc_cross + ref_e[i] * mic_e[i];  // 40x40 -> 40-bit (lower bits)
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            for (int i = 0; i < N; i++) begin
                ref_buf[i] <= '0;
                mic_buf[i] <= '0;
            end
            win_cnt   <= '0;
            echo_det  <= 1'b0;
            valid_out <= 1'b0;
        end else if (valid_in) begin
            // Shift new sample into buffer front
            ref_buf[0] <= ref_in;
            mic_buf[0] <= mic_in;
            for (int i = 1; i < N; i++) begin
                ref_buf[i] <= ref_buf[i-1];
                mic_buf[i] <= mic_buf[i-1];
            end
            if (!window_full)
                win_cnt <= win_cnt + 1'b1;
            // Register outputs; acc_cross is computed from pre-shift buffer
            echo_det  <= window_full & (acc_cross >= threshold);
            valid_out <= window_full;
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
