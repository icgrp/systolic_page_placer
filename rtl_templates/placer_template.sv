module placer(input wire clk,
              input wire rst,
              input wire load_enable_in,
              output wire complete,
              input wire [BUS_WIDTH-1:0] load_in,
              output wire [BUS_WIDTH-1:0] unload_out);

    //*************************************************************************
    // Placer params

    parameter integer N = {N};
    parameter integer T = {T};
    parameter integer D = {D};
    parameter integer B = {B};
    parameter integer V = {V};
    parameter integer MAX_K = {MAX_K};
    parameter integer P = {P};
    parameter integer N_io = {N_io};
    parameter integer F_io = {F_io};

    parameter integer MSAD = {MSAD};
    parameter integer WSRD = {WSRD};
    parameter integer RAM_CYCLES = {RAM_CYCLES};
    parameter integer MULT_CYCLES = {MULT_CYCLES};
    parameter integer FIXED_SUM_CYCLES = {FIXED_SUM_CYCLES};
    parameter integer SCD = {SCD};

    parameter integer BUS_WIDTH = {BUS_WIDTH};
    parameter integer MAX_NUM_OF_UPDATES = {MAX_NUM_OF_UPDATES};
    parameter integer MAX_SWAPS_PER_UPDATE = {MAX_SWAPS_PER_UPDATE};

    //*************************************************************************
    // Sub Placers
    assign complete = {complete};
    wire [BUS_WIDTH-1:0] completed_sum;
{sub_placers}
    //*************************************************************************
    // Tree of Trees
    wire [BUS_WIDTH-1:0] tree_of_trees_out;
{tree_of_trees}
    //*************************************************************************
    // Fixed PE
{fixed_pe}

endmodule