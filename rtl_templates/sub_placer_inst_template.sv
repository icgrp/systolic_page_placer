//*************************************************************************
// sub_placer_{ty}
wire [BUS_WIDTH-1:0] {partial_sum_out};

wire complete_{ty};
wire load_enable_out_{ty};
wire [BUS_WIDTH-1:0] {load_pipe_out};
wire [BUS_WIDTH-1:0] {unload_pipe_in};
sub_placer_{ty} sub_placer_{ty}_inst(.clk(clk),
                                   .rst(rst),
                                   .complete(complete_{ty}),
                                   .completed_sum(completed_sum),
                                   .partial_sum_out({partial_sum_out}),
                                   .load_enable_in({load_enable_in}),
                                   .load_enable_out(load_enable_out_{ty}),
                                   .load_pipe_in({load_pipe_in}),
                                   .load_pipe_out({load_pipe_out}),
                                   .unload_pipe_in({unload_pipe_in}),
                                   .unload_pipe_out({unload_pipe_out}));

defparam sub_placer_{ty}_inst.N = N;
defparam sub_placer_{ty}_inst.T = T;
defparam sub_placer_{ty}_inst.D = D;
defparam sub_placer_{ty}_inst.B = B;
defparam sub_placer_{ty}_inst.V = V;
defparam sub_placer_{ty}_inst.MAX_K = MAX_K;
defparam sub_placer_{ty}_inst.P = P;

defparam sub_placer_{ty}_inst.MSAD = MSAD;
defparam sub_placer_{ty}_inst.WSRD = WSRD;
defparam sub_placer_{ty}_inst.RAM_CYCLES = RAM_CYCLES;
defparam sub_placer_{ty}_inst.MULT_CYCLES = MULT_CYCLES;
defparam sub_placer_{ty}_inst.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
defparam sub_placer_{ty}_inst.SCD = SCD;

defparam sub_placer_{ty}_inst.BUS_WIDTH = BUS_WIDTH;
defparam sub_placer_{ty}_inst.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;
defparam sub_placer_{ty}_inst.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;