// 4x4 binary-weight crossbar MAC unit
// out[j] = sum_i weight[i][j] * in[i], weights are +1 (w=1) or -1 (w=0)
// weights loaded via wdata[4*i+j] on posedge clk when load=1
module crossbar_mac (
    input  logic             clk,
    input  logic             rst,
    input  logic             load,
    input  logic [15:0]      wdata,
    input  logic signed [7:0] in0, in1, in2, in3,
    output logic signed [9:0] out0, out1, out2, out3
);

    logic w [0:3][0:3];

    always_ff @(posedge clk) begin
        if (load)
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++)
                    w[i][j] <= wdata[4*i + j];
    end

    logic signed [7:0] ins [0:3];
    assign ins[0] = in0; assign ins[1] = in1;
    assign ins[2] = in2; assign ins[3] = in3;

    logic signed [9:0] acc [0:3];

    always_comb begin
        for (int j = 0; j < 4; j++) begin
            acc[j] = 0;
            for (int i = 0; i < 4; i++) begin
                if (w[i][j])
                    acc[j] = acc[j] + {{2{ins[i][7]}}, ins[i]};
                else
                    acc[j] = acc[j] - {{2{ins[i][7]}}, ins[i]};
            end
        end
    end

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            out0 <= 0; out1 <= 0; out2 <= 0; out3 <= 0;
        end else begin
            out0 <= acc[0]; out1 <= acc[1];
            out2 <= acc[2]; out3 <= acc[3];
        end
    end

endmodule
