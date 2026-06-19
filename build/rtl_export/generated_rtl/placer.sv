module placer(input wire clk,
              input wire rst,
              input wire load_enable_in,
              output wire complete,
              input wire [BUS_WIDTH-1:0] load_in,
              output wire [BUS_WIDTH-1:0] unload_out);

    //*************************************************************************
    // Placer params

    parameter integer N = 967;
    parameter integer T = 3;
    parameter integer D = 35;
    parameter integer B = 35;
    parameter integer V = 194;
    parameter integer MAX_K = 42839;
    parameter integer P = 1487020;
    parameter integer N_io = 800;
    parameter integer F_io = 1;

    parameter integer MSAD = 40;
    parameter integer WSRD = 34;
    parameter integer RAM_CYCLES = 2;
    parameter integer MULT_CYCLES = 1;
    parameter integer FIXED_SUM_CYCLES = 1;
    parameter integer SCD = 46;

    parameter integer BUS_WIDTH = 23;
    parameter integer MAX_NUM_OF_UPDATES = 500;
    parameter integer MAX_SWAPS_PER_UPDATE = 500;

    //*************************************************************************
    // Sub Placers
    assign complete = complete_clb;
    wire [BUS_WIDTH-1:0] completed_sum;
    //*************************************************************************
    // sub_placer_clb
    wire [BUS_WIDTH-1:0] clb_partial_sum_out;

    wire complete_clb;
    wire load_enable_out_clb;
    wire [BUS_WIDTH-1:0] clb_load_pipe_out;
    wire [BUS_WIDTH-1:0] clb_unload_pipe_in;
    sub_placer_clb sub_placer_clb_inst(.clk(clk),
                                       .rst(rst),
                                       .complete(complete_clb),
                                       .completed_sum(completed_sum),
                                       .partial_sum_out(clb_partial_sum_out),
                                       .load_enable_in(load_enable_in),
                                       .load_enable_out(load_enable_out_clb),
                                       .load_pipe_in(load_in),
                                       .load_pipe_out(clb_load_pipe_out),
                                       .unload_pipe_in(clb_unload_pipe_in),
                                       .unload_pipe_out(unload_out));

    defparam sub_placer_clb_inst.N = N;
    defparam sub_placer_clb_inst.T = T;
    defparam sub_placer_clb_inst.D = D;
    defparam sub_placer_clb_inst.B = B;
    defparam sub_placer_clb_inst.V = V;
    defparam sub_placer_clb_inst.MAX_K = MAX_K;
    defparam sub_placer_clb_inst.P = P;

    defparam sub_placer_clb_inst.MSAD = MSAD;
    defparam sub_placer_clb_inst.WSRD = WSRD;
    defparam sub_placer_clb_inst.RAM_CYCLES = RAM_CYCLES;
    defparam sub_placer_clb_inst.MULT_CYCLES = MULT_CYCLES;
    defparam sub_placer_clb_inst.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
    defparam sub_placer_clb_inst.SCD = SCD;

    defparam sub_placer_clb_inst.BUS_WIDTH = BUS_WIDTH;
    defparam sub_placer_clb_inst.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;
    defparam sub_placer_clb_inst.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;

    //*************************************************************************
    // sub_placer_mult_36
    wire [BUS_WIDTH-1:0] mult_36_partial_sum_out;

    wire complete_mult_36;
    wire load_enable_out_mult_36;
    wire [BUS_WIDTH-1:0] mult_36_load_pipe_out;
    wire [BUS_WIDTH-1:0] mult_36_unload_pipe_in;
    sub_placer_mult_36 sub_placer_mult_36_inst(.clk(clk),
                                       .rst(rst),
                                       .complete(complete_mult_36),
                                       .completed_sum(completed_sum),
                                       .partial_sum_out(mult_36_partial_sum_out),
                                       .load_enable_in(load_enable_out_clb),
                                       .load_enable_out(load_enable_out_mult_36),
                                       .load_pipe_in(clb_load_pipe_out),
                                       .load_pipe_out(mult_36_load_pipe_out),
                                       .unload_pipe_in(mult_36_unload_pipe_in),
                                       .unload_pipe_out(clb_unload_pipe_in));

    defparam sub_placer_mult_36_inst.N = N;
    defparam sub_placer_mult_36_inst.T = T;
    defparam sub_placer_mult_36_inst.D = D;
    defparam sub_placer_mult_36_inst.B = B;
    defparam sub_placer_mult_36_inst.V = V;
    defparam sub_placer_mult_36_inst.MAX_K = MAX_K;
    defparam sub_placer_mult_36_inst.P = P;

    defparam sub_placer_mult_36_inst.MSAD = MSAD;
    defparam sub_placer_mult_36_inst.WSRD = WSRD;
    defparam sub_placer_mult_36_inst.RAM_CYCLES = RAM_CYCLES;
    defparam sub_placer_mult_36_inst.MULT_CYCLES = MULT_CYCLES;
    defparam sub_placer_mult_36_inst.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
    defparam sub_placer_mult_36_inst.SCD = SCD;

    defparam sub_placer_mult_36_inst.BUS_WIDTH = BUS_WIDTH;
    defparam sub_placer_mult_36_inst.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;
    defparam sub_placer_mult_36_inst.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;

    //*************************************************************************
    // sub_placer_memory
    wire [BUS_WIDTH-1:0] memory_partial_sum_out;

    wire complete_memory;
    wire load_enable_out_memory;
    wire [BUS_WIDTH-1:0] memory_load_pipe_out;
    wire [BUS_WIDTH-1:0] memory_unload_pipe_in;
    sub_placer_memory sub_placer_memory_inst(.clk(clk),
                                       .rst(rst),
                                       .complete(complete_memory),
                                       .completed_sum(completed_sum),
                                       .partial_sum_out(memory_partial_sum_out),
                                       .load_enable_in(load_enable_out_mult_36),
                                       .load_enable_out(load_enable_out_memory),
                                       .load_pipe_in(mult_36_load_pipe_out),
                                       .load_pipe_out(memory_load_pipe_out),
                                       .unload_pipe_in(memory_unload_pipe_in),
                                       .unload_pipe_out(mult_36_unload_pipe_in));

    defparam sub_placer_memory_inst.N = N;
    defparam sub_placer_memory_inst.T = T;
    defparam sub_placer_memory_inst.D = D;
    defparam sub_placer_memory_inst.B = B;
    defparam sub_placer_memory_inst.V = V;
    defparam sub_placer_memory_inst.MAX_K = MAX_K;
    defparam sub_placer_memory_inst.P = P;

    defparam sub_placer_memory_inst.MSAD = MSAD;
    defparam sub_placer_memory_inst.WSRD = WSRD;
    defparam sub_placer_memory_inst.RAM_CYCLES = RAM_CYCLES;
    defparam sub_placer_memory_inst.MULT_CYCLES = MULT_CYCLES;
    defparam sub_placer_memory_inst.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
    defparam sub_placer_memory_inst.SCD = SCD;

    defparam sub_placer_memory_inst.BUS_WIDTH = BUS_WIDTH;
    defparam sub_placer_memory_inst.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;
    defparam sub_placer_memory_inst.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;


    //*************************************************************************
    // Tree of Trees
    wire [BUS_WIDTH-1:0] tree_of_trees_out;
 
    //************************************************************************
    // Level 0
    // Node 0
    wire [BUS_WIDTH-1:0] out_level0_node0;
    sum_tree_node sum_tree_level0_node0(
        .clk(clk),
        .in_a(memory_partial_sum_out),
        .in_b(clb_partial_sum_out),
        .out(out_level0_node0)
    );
    defparam sum_tree_level0_node0.BUS_WIDTH = BUS_WIDTH;
    // Node 1
    wire [BUS_WIDTH-1:0] out_level0_node1;
    sum_tree_node sum_tree_level0_node1(
        .clk(clk),
        .in_a(mult_36_partial_sum_out),
        .in_b(23'd0),
        .out(out_level0_node1)
    );
    defparam sum_tree_level0_node1.BUS_WIDTH = BUS_WIDTH;

    //************************************************************************
    // Level 1
    // Node 0
    wire [BUS_WIDTH-1:0] out_level1_node0;
    sum_tree_node sum_tree_level1_node0(
        .clk(clk),
        .in_a(out_level0_node0),
        .in_b(out_level0_node1),
        .out(out_level1_node0)
    );
    defparam sum_tree_level1_node0.BUS_WIDTH = BUS_WIDTH;


    assign tree_of_trees_out = out_level1_node0;
    //*************************************************************************
    // Fixed PE
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
        .load_enable_in(load_enable_out_memory),

        .in(tree_of_trees_out),
        .out(completed_sum),

        .enable_sums(fixed_pe_enable_sums),
        .enable_load_x_sums(enable_load_x_sums),
        .enable_load_y_sums(enable_load_y_sums),

        .load_in(memory_load_pipe_out),
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
    defparam sum_ram_fixed_x.DELAY_CYCLES = 44;

    weight_ram sum_ram_fixed_y(
        .clk(clk),
        .enable_weights(fixed_pe_enable_sums),
        .out_weight(fixed_sum_y),

        .load(enable_load_y_sums),
        .in_weight(load_sum_y)
    );
    defparam sum_ram_fixed_y.DATA_WIDTH = $clog2((V/2)*F_io*N_io*D + 1);
    defparam sum_ram_fixed_y.N = N;
    defparam sum_ram_fixed_y.DELAY_CYCLES = 44;

endmodule