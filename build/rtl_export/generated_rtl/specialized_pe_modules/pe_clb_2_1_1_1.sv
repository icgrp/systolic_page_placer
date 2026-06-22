module pe_clb_2_1_1_1(input wire clk,
          input wire rst,
          input wire load_enable_in,
          output reg load_enable_out = 0,
          output wire complete,

          input wire [BUS_WIDTH-1:0] in_right,
          output wire [BUS_WIDTH-1:0] out_right,
          output wire out_hot_move_right,

          input wire [BUS_WIDTH-1:0] in_left,
          input wire in_hot_move_left,
          output wire [BUS_WIDTH-1:0] out_left,

          input wire [BUS_WIDTH-1:0] in_up,
          output wire [BUS_WIDTH-1:0] out_up,
          output wire out_hot_move_up,

          input wire [BUS_WIDTH-1:0] in_down,
          input wire in_hot_move_down,
          output wire [BUS_WIDTH-1:0] out_down,

          output reg enable_weights = 0,
          output reg enable_load_weights = 0,
          input wire [$clog2(V+1)-1:0] in_weight,
          output reg [$clog2(V+1)-1:0] load_weight
);
    //#########################################################################################################################
    // PARAMETERS
    //#########################################################################################################################

    //********************************************************
    // parameters for the entire placer

    // fixed
    parameter integer N = -1;
    parameter integer T = -1;
    parameter integer D = -1;
    parameter integer B = -1;
    parameter integer V = -1;
    parameter integer MAX_K = -1;
    parameter integer P = -1;

    parameter integer MSAD = -1;                // Maximum Sub-Array Depth
    parameter integer WSRD = -1;                // worst sum return depth, the number of cycles for a newly computed sum to arrive at the input of the farthest PE across all sub-arrays.    
    parameter integer RAM_CYCLES = -1;
    parameter integer SUM_COORD_CYCLES = -1;
    parameter integer MULT_CYCLES = -1;
    parameter integer FIXED_SUM_CYCLES = -1;    // should be set to 1
    parameter integer SCD = -1;

    parameter integer BUS_WIDTH = -1;

    parameter integer MAX_NUM_OF_UPDATES = -1;
    parameter integer MAX_SWAPS_PER_UPDATE = -1;
    //********************************************************
    // parameters for this sub-array
    
    // fixed
    parameter integer BLK_ID_OFFSET = -1;       // Converts local blk_id to global blk_id

    parameter integer W_t = -1;
    parameter integer H_t = -1;
    parameter integer B_t = -1;
    parameter integer R_t = -1;

    // calculated
    parameter integer N_t = W_t*H_t;            // this really should be lowercase n, the number of PEs in the array

    //********************************************************
    // parameters for this specific PE

    // fixed
    parameter integer PE_X = -1;
    parameter integer PE_Y = -1;
    parameter integer X = -1;
    parameter integer Y = -1;

    parameter integer PHASE_0_ILLEGAL = -1;
    parameter integer PHASE_1_ILLEGAL = -1;
    parameter integer PHASE_2_ILLEGAL = -1;
    parameter integer PHASE_3_ILLEGAL = -1;
    parameter integer LOAD_PHASE = -1;
    parameter integer UNLOAD_PHASE = -1;

    // calculated
    parameter integer ODD_COL = PE_X%2;
    parameter integer ODD_ROW = PE_Y%2;
    parameter integer SRD = (H_t - 1) - PE_Y;   // sum return depth, the number of cycles for a newly computed sum to arrive at the input of *this* PE.
    //#########################################################################################################################
    // REGISTERS
    //#########################################################################################################################

    //********************************************************
    // Bus muxing register
    reg [BUS_WIDTH-1:0] broadcast;
    //********************************************************
    // General Registers

    reg [$clog2(MAX_SWAPS_PER_UPDATE+1)-1:0] swaps_per_update;
    reg [$clog2(MAX_NUM_OF_UPDATES+1)-1:0]   num_of_updates;

    reg [23:0] state;
    reg [$clog2(MAX_NUM_OF_UPDATES+1)-1:0] update_count;

    reg [$clog2(N_t-1+1)-1:0]       blk_id;
    reg [$clog2(MAX_K+1)-1:0]       k;

    reg [$clog2(MAX_K*R_t+1)-1:0]   k_r;
    reg [$clog2(MAX_K*B_t+1)-1:0]   k_x;
    reg [$clog2(MAX_K*B_t+1)-1:0]   k_y;

    reg [$clog2(P+1)-1:0]           sum_px;
    reg [$clog2(P+1)-1:0]           sum_py;
    //********************************************************
    // Swapping Registers

    // Hot move
    reg                                             out_hot_move;

    // unsigned
    reg [$clog2(MAX_SWAPS_PER_UPDATE+1)-1:0]        swap_count;

    // signed
    reg signed [$clog2(2*P+1)+1-1:0]                partial;
    reg signed [$clog2(2*P+MAX_K*R_t+1)+1-1:0]      half_s;
    reg signed [$clog2(2*P+MAX_K*R_t+1)+1-1:0]      other_half_s;
    reg signed [$clog2(2*(2*P+MAX_K*R_t+1))+1-1:0]  full_s;

    // flag
    reg                                             swap;
    reg                                             done_swapping;
    reg                                             ready_to_unload;
    //********************************************************
    // Sorting Registers

    reg [$clog2(D+1)-1:0]               sort_swap_counter;
    reg [$clog2($clog2(D+1)+1)-1:0]     sort_itter_counter;
    reg [$clog2(N_t-1+1)-1:0]           temp_blk_id;
    reg [$clog2(N_t-1+1)-1:0]           speculated_temp_blk_id;
    reg [2*$clog2(B_t+1)-1:0]           temp_coord;

    reg                                 sort_swap;
    //********************************************************
    // Summing Registers

    reg weight_mode;

    reg [$clog2(SCD+WSRD+(2*N)+1)-1:0]      sum_cycle_counter;
    reg [$clog2(SCD+(H_t-1)+N+1)-1:0]       sample_x_sum_cycle;
    reg [$clog2(SCD+(H_t-1)+(2*N)+1)-1:0]   sample_y_sum_cycle;

    reg [BUS_WIDTH-1:0] partial_update_sum;
    reg [BUS_WIDTH-1:0] completed_update_sum;
    //********************************************************
    // LFSR Registers
    reg [15:0] lfsr;
    reg [15:0] temp;
    reg [15:0] temp_threshold;  // THRESHOLD = INITIAL_TEMP - (TEMP_DEC_STEP*(NUM_OF_STEPS-1));
    reg [15:0] temp_dec_step;   // NUM_OF_STEPS = (NUM_OF_UPDATES*SWAPS_PER_UPDATE) - 1;
    //********************************************************
    // Control Registers

    reg [1:0]   phase;
    reg [1:0]   saved_phase;
    reg         illegal_move;
    //********************************************************
    // Debugging Registers
    
    reg debug_loading = 0;
    reg debug_swapping = 0;
    reg debug_sorting = 0;
    reg debug_summing = 0;
    reg debug_halt = 0;

    reg debug_overflow = 0;
    //#########################################################################################################################
    // LOGIC
    //#########################################################################################################################

    //********************************************************
    // Bus muxing logic
    assign out_right = broadcast;
    assign out_left = broadcast;
    assign out_up = (state != STATE_SUM_0) ? broadcast : partial_update_sum;
    assign out_down = (state != STATE_SUM_0) ? broadcast : completed_update_sum;
    //********************************************************
    // Hot move
    assign out_hot_move_right = out_hot_move;
    assign out_hot_move_up = out_hot_move;
    //********************************************************
    assign complete = (state == STATE_UNLOAD_0);
    //********************************************************
    // General logic

    wire [$clog2(B_t+1)-1:0] x = X;
    wire [$clog2(B_t+1)-1:0] y = Y;

    wire odd_col = ODD_COL;
    wire odd_row = ODD_ROW;

    wire x_phase = (phase == 0 || phase == 2);
    wire y_phase = (phase == 1 || phase == 3);

    wire x_master = (phase == 0) ? ~odd_col : odd_col;          // (only valid if x_phase is valid)     swap x master: if phase is 0, then even, if phase is 2, then odd.
    wire y_master = (phase == 1) ? odd_row : ~odd_row;          // (only valid if y_phase is valid)     swap y master: if phase is 1, then odd, if phase is 3, then even.

    wire master = x_phase ? x_master : y_master;

    wire sort_master_x = (phase == 0) ? ~odd_col : odd_col;     // assumes phase is 0 or 2
    wire sort_master_y = (phase == 3) ? ~odd_row : odd_row;     // assumes phase is 1 or 3

    // fake register
    reg [BUS_WIDTH-1:0] active_in = 0; // idk if this should actually be set to zero or not since it is fake

    always @(*) begin
        case(phase)
        2'd0: begin
            // phase 0
            illegal_move = PHASE_0_ILLEGAL;
            active_in = (~odd_col) ? in_right : in_left;
        end
        2'd1: begin 
            // phase 1
            illegal_move = PHASE_1_ILLEGAL;
            active_in = (odd_row) ? in_up : in_down;
        end
        2'd2: begin 
            // phase 2
            illegal_move = PHASE_2_ILLEGAL;
            active_in = (odd_col) ? in_right : in_left;
        end
        2'd3: begin
            // phase 3
            illegal_move = PHASE_3_ILLEGAL;
            active_in = (~odd_row) ? in_up : in_down;
        end
        endcase
    end
    
    // This mux assumes phase is 0 or 2
    reg [$clog2(N_t-1+1)-1:0] sort_active_in_x = 0;
    reg sort_illegal_move_x = 0;
    always @(*) begin
        if(phase[1] == 0) begin
            sort_active_in_x = (~odd_col) ? in_right : in_left;
            sort_illegal_move_x = PHASE_0_ILLEGAL;
        end
        else begin
            sort_active_in_x = (odd_col) ? in_right : in_left;
            sort_illegal_move_x = PHASE_2_ILLEGAL;
        end
    end
    
    // This mux assums phase is 1 or 3
    reg [$clog2(N_t-1+1)-1:0] sort_active_in_y = 0;
    reg sort_illegal_move_y = 0;
    always @(*) begin
        if(phase[1] == 0) begin
            sort_active_in_y = (odd_row) ? in_up : in_down;
            sort_illegal_move_y = PHASE_1_ILLEGAL;
        end
        else begin
            sort_active_in_y = (~odd_row) ? in_up : in_down;
            sort_illegal_move_y = PHASE_3_ILLEGAL;
        end
    end

    //********************************************************
    // Swapping logic

    // fake register
    reg [$clog2(MAX_K*R_t+1)-1:0] k_r_comp = 0; // idk if this should actually be set to zero or not since it is fake

    always @(*) begin
        case(phase)
        2'd0: k_r_comp = (k << 1);
        2'd1: k_r_comp = (k << 0);
        2'd2: k_r_comp = (k << 0);
        2'd3: k_r_comp = (k << 0);
        endcase
    end

    wire [$clog2(MAX_K*B_t+1)-1:0] k_x_comp = (master == 1) ? k_x + k_r : k_x - k_r;
    wire [$clog2(MAX_K*B_t+1)-1:0] k_y_comp = (master == 1) ? k_y + k_r : k_y - k_r;
    wire [$clog2(MAX_K*B_t+1)-1:0] k_times_coord = (x_phase == 1) ? k_x : k_y;

    wire [$clog2(MAX_K*B_t+1)-1:0] sum_p = (x_phase == 1) ? sum_px : sum_py;

    wire full_s_msb = full_s[$clog2(2*(2*P+MAX_K*R_t+1))+1-1];

    wire active_hot_move = (x_phase) ? ((x_master) ? hot_move : in_hot_move_left) : 
                                       ((y_master) ? hot_move : in_hot_move_down);

    // signed
    wire signed [$clog2(2*P+1)+1-1:0]                   partial_comp = ($signed(k_times_coord) - $signed(sum_p)) << 1;
    wire signed [$clog2(2*P+MAX_K*R_t+1)+1-1:0]         half_s_comp = (master == 1) ? partial + $signed(k_r) : partial - $signed(k_r); 
    wire signed [$clog2(2*(2*P+MAX_K*R_t+1))+1-1:0]     full_s_comp = (master == 1) ? half_s - other_half_s : other_half_s - half_s;
    //********************************************************
    // Sorting logic

    wire sort_condition_x = !(sort_master_x ^ (sort_active_in_x < temp_blk_id));
    wire sort_condition_y = !(sort_master_y ^ (sort_active_in_y < temp_blk_id));

    wire sort_x_should_swap = ((((odd_row == 0) && sort_condition_x) || ((odd_row != 0) && !sort_condition_x)) && !sort_illegal_move_x);
    wire sort_y_should_swap = (sort_condition_y && !sort_illegal_move_y);
    
    wire sort_pass_done = (sort_swap_counter == (D - 1));
    wire sort_iter_done = (sort_itter_counter == ($clog2(D) - 1));
    //********************************************************
    // Summing logic
    wire [$clog2(B_t+1)-1:0] sum_coord;
    wire [$clog2(V*B_t+1)-1:0] weighted_coord;

    wire [$clog2(B_t+1)-1:0] sum_coord_comp = (weight_mode == 0) ? temp_coord[2*$clog2(B_t+1)-1:$clog2(B_t+1)] : temp_coord[$clog2(B_t+1)-1:0];
    wire [$clog2(V*B_t+1)-1:0] weighted_coord_comp = in_weight*sum_coord;
    //********************************************************
    // LFSR logic

    wire feedback = lfsr[16-1]^lfsr[15-1]^lfsr[13-1]^lfsr[4-1];
    wire hot_move = (lfsr < temp);
    //********************************************************
    // Debugging logic

    wire debug_sample = (sum_cycle_counter == sample_x_sum_cycle) | (sum_cycle_counter == sample_y_sum_cycle);

    //#########################################################################################################################
    // Pipelining 
    //#########################################################################################################################

    // DSP pipelining


    reg [$clog2(B_t+1)-1:0] sum_coord_pipeline [0:SUM_COORD_CYCLES-1];
    integer scp_i;

    always @(posedge clk) begin
        sum_coord_pipeline[0] <= sum_coord_comp;

        for(scp_i = 1; scp_i < SUM_COORD_CYCLES; scp_i = scp_i + 1) begin
            sum_coord_pipeline[scp_i] <= sum_coord_pipeline[scp_i - 1];
        end
    end
    assign sum_coord = sum_coord_pipeline[SUM_COORD_CYCLES - 1];



    reg [$clog2(V*B_t+1)-1:0] multiply_pipeline [0:MULT_CYCLES-1];
    integer mp_i;

    always @(posedge clk) begin
        multiply_pipeline[0] <= weighted_coord_comp;

        for(mp_i = 1; mp_i < MULT_CYCLES; mp_i = mp_i + 1) begin
            multiply_pipeline[mp_i] <= multiply_pipeline[mp_i - 1];
        end
    end
    assign weighted_coord = multiply_pipeline[MULT_CYCLES - 1];

    //#########################################################################################################################
    // STATE MACHINE
    //#########################################################################################################################
    
    // init
    localparam STATE_INIT_0 = 24'b100000000000000000000000;

    // load
    localparam STATE_LOAD_0 = 24'b000000000000000000000001;
    localparam STATE_LOAD_1 = 24'b000000000000000000000010;
    localparam STATE_LOAD_2 = 24'b000000000000000000000100;
    localparam STATE_LOAD_3 = 24'b000000000000000000001000;
    localparam STATE_LOAD_4 = 24'b000000000000000000010000;

    // sort
    localparam STATE_SORT_X_COMPARE        = 24'b000000000000000000100000;
    localparam STATE_SORT_X_EXCHANGE       = 24'b000000000000000001000000;
    localparam STATE_SORT_Y_COMPARE        = 24'b000000000000000010000000;
    localparam STATE_SORT_Y_EXCHANGE       = 24'b000000000000000100000000;
    localparam STATE_SORT_FINAL_X_COMPARE  = 24'b000000000000001000000000;
    localparam STATE_SORT_FINAL_X_EXCHANGE = 24'b000000000000010000000000;

    // swap
    localparam STATE_SWAP_0 = 24'b000000000000100000000000;
    localparam STATE_SWAP_1 = 24'b000000000001000000000000;
    localparam STATE_SWAP_2 = 24'b000000000010000000000000;
    localparam STATE_SWAP_3 = 24'b000000000100000000000000;
    localparam STATE_SWAP_4 = 24'b000000001000000000000000;
    localparam STATE_SWAP_5 = 24'b000000010000000000000000;
    localparam STATE_SWAP_6 = 24'b000000100000000000000000;
    localparam STATE_SWAP_7 = 24'b000001000000000000000000;
    localparam STATE_SWAP_8 = 24'b000010000000000000000000;
    localparam STATE_SWAP_9 = 24'b000100000000000000000000;

    // sum
    localparam STATE_SUM_0 = 24'b001000000000000000000000;

    // unload
    localparam STATE_UNLOAD_0 = 24'b010000000000000000000000;

    // config params
    parameter integer START_DELAY = -1;
    parameter integer LOAD_DELAY = -1;
    parameter integer SUM_DELAY = -1; 
    localparam UNLOAD_DELAY = N;
    localparam RAM_DEPTH = N;

    reg [$clog2(N+B+1)-1:0] load_counter = 0;

    // Note: reset moved to the end in order to reduce control sets
    always @(posedge clk) begin
        case(state)
        STATE_INIT_0: begin
            k_x <= 0;
            k_y <= 0;

            swap_count <= 0;
            sum_px <= 0;
            sum_py <= 0;
            enable_weights <= 0;

            sort_swap_counter <= 0;
            sort_itter_counter <= 0;

            weight_mode <= 0;
            sum_cycle_counter <= 0;

            temp_coord <= {x,y};
            saved_phase <= 0;

            // debug signals, to be removed later
            debug_loading <= 0;
            debug_swapping <= 0;
            debug_sorting <= 0;
            debug_summing <= 0;
            debug_halt <= 0;

            update_count <= 0;

            // loading stuff
            load_counter <= 0;

            if(load_enable_in) begin
                debug_loading <= 1;
                state <= STATE_LOAD_0;
                blk_id <= active_in;
            end
        end
        //********************************************************
        STATE_LOAD_0: begin // 17 (load params)
            if(load_counter == 0) begin
                k <= active_in;
            end
            if(load_counter == 1) begin
                lfsr <= active_in;
            end
            if(load_counter == 2) begin
                temp <= active_in;
            end
            if(load_counter == 3) begin
                temp_dec_step <= active_in;
            end
            if(load_counter == 4) begin
                temp_threshold <= active_in;
            end
            if(load_counter == 5) begin
                swaps_per_update <= active_in;
            end
            if(load_counter == 6) begin
                num_of_updates <= active_in;

                load_counter <= 0;
                state <= STATE_LOAD_1;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_LOAD_1: begin // 18 (load weights)
            enable_load_weights <= 1;
            load_weight <= active_in;

            if(load_counter == RAM_DEPTH-1) begin
                load_counter <= 0;
                state <= STATE_LOAD_2;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_LOAD_2: begin // 19 (load last weight and forward)
            enable_load_weights <= 0;
            load_enable_out <= load_enable_in;

            if(load_enable_in) begin
                if(load_counter == LOAD_DELAY - 1) begin
                    load_counter <= 0;
                    state <= STATE_LOAD_3;
                end
                else begin
                    load_counter <= load_counter + 1;
                end
            end

            broadcast <= active_in;

        end
        STATE_LOAD_3: begin // 20 (init k_x and k_y)
            load_enable_out <= 0;
            if(load_counter < X) begin
                k_x <= k_x + k;
            end
            if(load_counter < Y) begin
                k_y <= k_y + k;
            end
            if(~(load_counter < X) && ~(load_counter < Y)) begin
                load_counter <= 0;
                state <= STATE_LOAD_4;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_LOAD_4: begin // 21 (sync delay before start)
            if(load_counter == START_DELAY - 1) begin

                load_counter <= 0;

                debug_loading <= 0;
                debug_sorting <= 1;

                phase <= 0;
                temp_blk_id <= blk_id;
                state <= STATE_SORT_X_COMPARE;
            end
            else begin
                load_counter <= load_counter + 1;
            end
            broadcast <= blk_id;
        end
        //********************************************************
        // Swapping
        STATE_SWAP_0: begin

            // register k_r_comp for later use
            k_r <= k_r_comp;

            // calculate the partial
            partial <= partial_comp;

            // output the hot_move
            out_hot_move <= hot_move;
            
            state <= STATE_SWAP_1;
        end
        STATE_SWAP_1: begin
            // calculate this PE's half of s(x) and output it
            half_s <= half_s_comp;

            // This is overkill but requiers less logic,
            // and shouldn't cause any trouble
            broadcast <= half_s_comp;

            state <= STATE_SWAP_2;
        end
        STATE_SWAP_2: begin
            other_half_s <= active_in;            

            state <= STATE_SWAP_3;
        end
        STATE_SWAP_3: begin
            // calculate the full s(x)
            full_s <= full_s_comp;

            // need to output this stuff if we swap
            broadcast <= blk_id;

            state <= STATE_SWAP_4;
        end
        STATE_SWAP_4: begin
            // if full_s is negitive or we have
            // a hot move, update k_times_coord and start swapping
            if((full_s_msb | active_hot_move) && !illegal_move) begin
                swap <= 1;
                blk_id <= active_in;
                if(x_phase) begin
                    k_x <= k_x_comp;
                end
                else begin
                    k_y <= k_y_comp;
                end
            end
            else begin
                swap <= 0;
            end

            broadcast <= k;

            state <= STATE_SWAP_5;
        end
        STATE_SWAP_5: begin
            // swap k
            if(swap) begin
                k <= active_in;
            end

            broadcast <= k_x;

            state <= STATE_SWAP_6;
        end
        STATE_SWAP_6: begin
            // swap k_x
            if(swap) begin
                k_x <= active_in;
            end

            broadcast <= k_y;

            state <= STATE_SWAP_7;
        end
        STATE_SWAP_7: begin
            // swap k_y
            if(swap) begin
                k_y <= active_in;
            end

            broadcast <= sum_px;

            // precompute for STATE_SWAP_8 and STATE_SWAP_9
            done_swapping <= (swap_count == (swaps_per_update - 1));

            state <= STATE_SWAP_8;
        end
        STATE_SWAP_8: begin
            // swap sum_x
            if(swap) begin
                sum_px <= active_in;
            end

            broadcast <= sum_py;

            // precompute for STATE_SWAP_9
            ready_to_unload <= done_swapping && (update_count == num_of_updates);

            state <= STATE_SWAP_9;
        end
        STATE_SWAP_9: begin
            // swap sum_y
            if(swap) begin
                sum_py <= active_in;
            end

            if(ready_to_unload) begin
                state <= STATE_UNLOAD_0;
                phase <= UNLOAD_PHASE;
                sum_cycle_counter <= 0;
                load_counter <= 0;

                debug_swapping <= 0;
                debug_halt <= 1;
            end
            else if(done_swapping) begin                               // if done swapping mode, move to sorting mode
                swap_count <= 0;
                state <= STATE_SORT_X_COMPARE;
                phase <= 0;
                saved_phase <= phase + 1;                              // this is the phase we will start off with after we are done sorting and summing
                temp_blk_id <= blk_id;
                temp_coord <= {x,y};

                debug_swapping <= 0;
                debug_sorting <= 1;
            end
            else begin                                                 // otherwise continue in swapping mode
                phase <= phase + 1;                                    // Note: this may overflow to zero, and this is intended
                swap_count <= swap_count + 1;
                state <= STATE_SWAP_0;
            end

            // create the next random number and decrement the counter
            lfsr <= {lfsr[14:0],feedback};
            if(temp > temp_threshold) begin
                temp <= temp - temp_dec_step;
            end
            else begin
                temp <= 0;
            end

            // completed the swap (assuming one was taking place)
            swap <= 0;

            // Needed if we go into sorting mode or unload
            broadcast <= blk_id;
        end
        //********************************************************
        // Sorting
        STATE_SORT_X_COMPARE: begin
            // X compare: decide whether to exchange temp_blk_id/temp_coord
            // with the horizontal neighbor selected by phase 0 or 2.

            // when we enter this state, we assume that
            // the PEs are transmitting their temp_blk_ids,
            // (or their blk_ids if its the first time)

            // So active in has the neighbor's block id
            sort_swap <= sort_x_should_swap;
            speculated_temp_blk_id <= active_in;
            broadcast <= temp_coord;

            state <= STATE_SORT_X_EXCHANGE;
        end
        STATE_SORT_X_EXCHANGE: begin
            // X exchange/control: receive temp_coord if the previous compare
            // selected a swap, then either continue X passes or move to Y passes.
            if(sort_swap) begin
                temp_coord <= active_in;
                temp_blk_id <= speculated_temp_blk_id;
            end
            sort_swap <= 0;

            if(sort_pass_done) begin
                sort_swap_counter <= 0;

                phase <= 3;
                state <= STATE_SORT_Y_COMPARE;
            end
            else begin
                sort_swap_counter <= sort_swap_counter + 1;
                phase <= (phase == 0) ? 2 : 0;
                state <= STATE_SORT_X_COMPARE;
            end

            broadcast <= temp_blk_id;
        end
        STATE_SORT_Y_COMPARE: begin
            // Y compare: decide whether to exchange temp_blk_id/temp_coord
            // with the vertical neighbor selected by phase 3 or 1.
            sort_swap <= sort_y_should_swap;
            speculated_temp_blk_id <= active_in;
            broadcast <= temp_coord;

            state <= STATE_SORT_Y_EXCHANGE;
        end
        STATE_SORT_Y_EXCHANGE: begin
            // Y exchange/control: receive temp_coord if needed. A completed
            // Y pass either starts another X/Y iteration or moves to the final
            // X pass before summing.
            if(sort_swap) begin
                temp_coord <= active_in;
                temp_blk_id <= speculated_temp_blk_id;
            end
            sort_swap <= 0;

            if(sort_pass_done) begin
                if(sort_iter_done) begin
                    sort_itter_counter <= 0;
                    state <= STATE_SORT_FINAL_X_COMPARE;
                end
                else begin
                    sort_itter_counter <= sort_itter_counter + 1;
                    state <= STATE_SORT_X_COMPARE;
                end

                sort_swap_counter <= 0;
                phase <= 0;
            end
            else begin
                sort_swap_counter <= sort_swap_counter + 1;
                phase <= (phase == 3) ? 1 : 3;
                state <= STATE_SORT_Y_COMPARE;
            end

            broadcast <= temp_blk_id;
        end
        STATE_SORT_FINAL_X_COMPARE: begin
            // Final X compare: same compare/exchange operation as a normal X
            // pass, but completion transitions directly into summing.
            sort_swap <= sort_x_should_swap;
            speculated_temp_blk_id <= active_in;
            broadcast <= temp_coord;

            state <= STATE_SORT_FINAL_X_EXCHANGE;
        end
        STATE_SORT_FINAL_X_EXCHANGE: begin
            // Final X exchange/control: finish the final row pass and start
            // the sum phase once all D compare/exchange pairs have run.
            if(sort_swap) begin
                temp_coord <= active_in;
                temp_blk_id <= speculated_temp_blk_id;
            end
            sort_swap <= 0;

            if(sort_pass_done) begin
                sort_swap_counter <= 0;
                phase <= 0;
                state <= STATE_SUM_0;

                sample_x_sum_cycle <= BLK_ID_OFFSET + blk_id + (SCD + SRD);
                sample_y_sum_cycle <= BLK_ID_OFFSET + blk_id + (SCD + SRD + N);

                sum_cycle_counter <= 0;
                enable_weights <= 1;

                debug_sorting <= 0;
                debug_summing <= 1;
            end
            else begin
                sort_swap_counter <= sort_swap_counter + 1;
                phase <= (phase == 0) ? 2 : 0;
                state <= STATE_SORT_FINAL_X_COMPARE;
            end

            broadcast <= temp_blk_id;
        end
        //********************************************************
        // Sum computation
        STATE_SUM_0: begin
            //********************************************************
            // Compute partial sums
            partial_update_sum <= in_down + weighted_coord;
            //********************************************************
            // Forward the completed sums
            completed_update_sum <= in_up;
            //********************************************************
            // Capture completed sums
            if(sum_cycle_counter == sample_x_sum_cycle) begin
                sum_px <= in_up;
            end
            else if(sum_cycle_counter == sample_y_sum_cycle)begin
                sum_py <= in_up;
            end
            //********************************************************
            // Control
            if(sum_cycle_counter == SUM_DELAY + RAM_CYCLES + N - SUM_COORD_CYCLES - 1) begin
                weight_mode <= 1;
            end
            else if(sum_cycle_counter == (SCD + WSRD + 2*N - 1)) begin
                state <= STATE_SWAP_0;
                phase <= saved_phase;
                enable_weights <= 0;
                weight_mode <= 0;
                update_count <= update_count + 1;

                debug_summing <= 0;
                debug_swapping <= 1;
            end
            sum_cycle_counter <= sum_cycle_counter + 1;
            //********************************************************
        end
        //********************************************************
        // Unload
        STATE_UNLOAD_0: begin

            broadcast <= active_in;

            if(load_counter == UNLOAD_DELAY - 1) begin
                debug_halt <= 0;
                load_counter <= 0;
                phase <= LOAD_PHASE;
                state <= STATE_INIT_0;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        endcase
        if(rst) begin
            state <= STATE_INIT_0;
            phase <= LOAD_PHASE;
        end
    end
    //********************************************************
endmodule
