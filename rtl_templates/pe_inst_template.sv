//************************************************************************
// PE (x{pe_x},y{pe_y})
{def_wire_load_enable_in}
{def_wire_load_enable_out}

wire [BUS_WIDTH-1:0] pe_x{pe_x}_y{pe_y}_in_right;
wire [BUS_WIDTH-1:0] pe_x{pe_x}_y{pe_y}_out_right;
wire pe_x{pe_x}_y{pe_y}_out_hot_move_right;

wire [BUS_WIDTH-1:0] pe_x{pe_x}_y{pe_y}_in_up;
wire [BUS_WIDTH-1:0] pe_x{pe_x}_y{pe_y}_out_up;
wire pe_x{pe_x}_y{pe_y}_out_hot_move_up;

wire pe_x{pe_x}_y{pe_y}_enable_weights;
wire [$clog2(V+1)-1:0] pe_x{pe_x}_y{pe_y}_out_weight;

wire pe_x{pe_x}_y{pe_y}_enable_load_weights;
wire [$clog2(V+1)-1:0] pe_x{pe_x}_y{pe_y}_load_weight;

{module_name} pe_x{pe_x}_y{pe_y}(
    .clk(clk),
    .rst(rst),
    .load_enable_in({load_enable_in}),
    .load_enable_out({load_enable_out}),
    .complete({complete}),

    .in_right({in_right}),
    .out_right({out_right}),
    .out_hot_move_right(pe_x{pe_x}_y{pe_y}_out_hot_move_right),

    .in_left({in_left}),
    .in_hot_move_left({in_hot_move_left}),
    .out_left({out_left}),

    .in_up({in_up}),
    .out_up(pe_x{pe_x}_y{pe_y}_out_up),
    .out_hot_move_up(pe_x{pe_x}_y{pe_y}_out_hot_move_up),

    .in_down({in_down}),
    .in_hot_move_down({in_hot_move_down}),
    .out_down({out_down}),

    .enable_weights(pe_x{pe_x}_y{pe_y}_enable_weights),
    .enable_load_weights(pe_x{pe_x}_y{pe_y}_enable_load_weights),
    .in_weight(pe_x{pe_x}_y{pe_y}_out_weight),
    .load_weight(pe_x{pe_x}_y{pe_y}_load_weight)
);

// fixed params for entire placer
defparam pe_x{pe_x}_y{pe_y}.N = N;
defparam pe_x{pe_x}_y{pe_y}.T = T;
defparam pe_x{pe_x}_y{pe_y}.D = D;
defparam pe_x{pe_x}_y{pe_y}.B = B;
defparam pe_x{pe_x}_y{pe_y}.V = V;
defparam pe_x{pe_x}_y{pe_y}.MAX_K = MAX_K;
defparam pe_x{pe_x}_y{pe_y}.P = P;

defparam pe_x{pe_x}_y{pe_y}.MSAD = MSAD;
defparam pe_x{pe_x}_y{pe_y}.WSRD = WSRD;
defparam pe_x{pe_x}_y{pe_y}.RAM_CYCLES = RAM_CYCLES;
defparam pe_x{pe_x}_y{pe_y}.MULT_CYCLES = MULT_CYCLES;
defparam pe_x{pe_x}_y{pe_y}.FIXED_SUM_CYCLES = FIXED_SUM_CYCLES;
defparam pe_x{pe_x}_y{pe_y}.SCD = SCD;

defparam pe_x{pe_x}_y{pe_y}.BUS_WIDTH = BUS_WIDTH;
defparam pe_x{pe_x}_y{pe_y}.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES;
defparam pe_x{pe_x}_y{pe_y}.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE;

// fixed parameters for the sub-array
defparam pe_x{pe_x}_y{pe_y}.BLK_ID_OFFSET = BLK_ID_OFFSET;

defparam pe_x{pe_x}_y{pe_y}.W_t = W_t;
defparam pe_x{pe_x}_y{pe_y}.H_t = H_t;
defparam pe_x{pe_x}_y{pe_y}.B_t = B_t;
defparam pe_x{pe_x}_y{pe_y}.R_t = R_t;

// fixed params for this pe
defparam pe_x{pe_x}_y{pe_y}.PE_X = {pe_x};
defparam pe_x{pe_x}_y{pe_y}.PE_Y = {pe_y};
defparam pe_x{pe_x}_y{pe_y}.X = {blk_x};
defparam pe_x{pe_x}_y{pe_y}.Y = {blk_y};

defparam pe_x{pe_x}_y{pe_y}.PHASE_0_ILLEGAL = {phase_0_illegal};
defparam pe_x{pe_x}_y{pe_y}.PHASE_1_ILLEGAL = {phase_1_illegal};
defparam pe_x{pe_x}_y{pe_y}.PHASE_2_ILLEGAL = {phase_2_illegal};
defparam pe_x{pe_x}_y{pe_y}.PHASE_3_ILLEGAL = {phase_3_illegal};
defparam pe_x{pe_x}_y{pe_y}.LOAD_PHASE = {load_phase};
defparam pe_x{pe_x}_y{pe_y}.UNLOAD_PHASE = {unload_phase};
defparam pe_x{pe_x}_y{pe_y}.LOAD_DELAY = {load_delay};
defparam pe_x{pe_x}_y{pe_y}.START_DELAY = {start_delay};

// weight ram
weight_ram weight_ram_x{pe_x}_y{pe_y}(
    .clk(clk),
    .enable_weights(pe_x{pe_x}_y{pe_y}_enable_weights),
    .out_weight(pe_x{pe_x}_y{pe_y}_out_weight),

    .load(pe_x{pe_x}_y{pe_y}_enable_load_weights),
    .in_weight(pe_x{pe_x}_y{pe_y}_load_weight)
);
defparam weight_ram_x{pe_x}_y{pe_y}.DATA_WIDTH = $clog2(V + 1);
defparam weight_ram_x{pe_x}_y{pe_y}.N = N;
defparam weight_ram_x{pe_x}_y{pe_y}.DELAY_CYCLES = MSAD - ($clog2(W_t) + H_t) + {pe_y};