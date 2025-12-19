module sum_tree_node (input wire clk,
                      input wire [BUS_WIDTH-1:0] in_a,
                      input wire [BUS_WIDTH-1:0] in_b,
                      output reg [BUS_WIDTH-1:0] out
);

    parameter integer BUS_WIDTH = 16;

    always @(posedge clk) begin
        out <= in_a + in_b;
    end

endmodule