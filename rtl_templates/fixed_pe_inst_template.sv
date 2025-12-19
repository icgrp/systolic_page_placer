wire fixed_pe_enable_sums;
wire [$clog2((V/2)*F_io*N_io*D + 1)-1:0] fixed_sum_x;
wire [$clog2((V/2)*F_io*N_io*D + 1)-1:0] fixed_sum_y;


wire enable_load_x_sums;
wire enable_load_y_sums;
wire [$clog2((V/2)*F_io*N_io*D + 1)-1:0] load_sum_x;
wire [$clog2((V/2)*F_io*N_io*D + 1)-1:0] load_sum_y;

fixed_pe fixed_pe_inst(
    .clk(clk),
    .rst(rst),
    .load_enable_in({load_enable_in}),

    .in(tree_of_trees_out),
    .out(completed_sum),

    .enable_sums(fixed_pe_enable_sums),
    .enable_load_x_sums(enable_load_x_sums),
    .enable_load_y_sums(enable_load_y_sums),

    .load_in({load_in}),
    .load_sum_x(load_sum_x),
    .load_sum_y(load_sum_y),

    .in_fixed_sum_x(fixed_sum_x),
    .in_fixed_sum_y(fixed_sum_y)
);
defparam fixed_pe_inst.N = N;
defparam fixed_pe_inst.T = T;
defparam fixed_pe_inst.D = D;
defparam fixed_pe_inst.B = B;
defparam fixed_pe_inst.DATA_WIDTH = $clog2((V/2)*F_io*N_io*D + 1);

defparam fixed_pe_inst.MSAD = MSAD;
defparam fixed_pe_inst.WSRD = WSRD;
defparam fixed_pe_inst.RAM_CYCLES = RAM_CYCLES;
defparam fixed_pe_inst.MULT_CYCLES = MULT_CYCLES;
defparam fixed_pe_inst.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
defparam fixed_pe_inst.SCD = SCD;
defparam fixed_pe_inst.BUS_WIDTH = BUS_WIDTH;
defparam fixed_pe_inst.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;
defparam fixed_pe_inst.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;

weight_ram sum_ram_fixed_x(
    .clk(clk),
    .enable_weights(fixed_pe_enable_sums),
    .out_weight(fixed_sum_x),

    .load(enable_load_x_sums),
    .in_weight(load_sum_x)
);
defparam sum_ram_fixed_x.DATA_WIDTH = $clog2((V/2)*F_io*N_io*D + 1);
defparam sum_ram_fixed_x.N = N;
defparam sum_ram_fixed_x.DELAY_CYCLES = {sum_ram_fixed_x_delay_cycles};

weight_ram sum_ram_fixed_y(
    .clk(clk),
    .enable_weights(fixed_pe_enable_sums),
    .out_weight(fixed_sum_y),

    .load(enable_load_y_sums),
    .in_weight(load_sum_y)
);
defparam sum_ram_fixed_y.DATA_WIDTH = $clog2((V/2)*F_io*N_io*D + 1);
defparam sum_ram_fixed_y.N = N;
defparam sum_ram_fixed_y.DELAY_CYCLES = {sum_ram_fixed_x_delay_cycles};