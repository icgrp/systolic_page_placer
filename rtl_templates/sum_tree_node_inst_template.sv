// Node {node}
wire [BUS_WIDTH-1:0] out_level{level}_node{node};
sum_tree_node sum_tree_level{level}_node{node}(
    .clk(clk),
    .in_a({in_a}),
    .in_b({in_b}),
    .out(out_level{level}_node{node})
);
defparam sum_tree_level{level}_node{node}.BUS_WIDTH = BUS_WIDTH;
