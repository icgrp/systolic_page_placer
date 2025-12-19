module fixed_pe(input wire clk,
                input wire rst,
                input wire load_enable_in,

                input wire [BUS_WIDTH-1:0] in,
                output reg [BUS_WIDTH-1:0] out,

                output reg enable_sums,
                output reg enable_load_x_sums,
                output reg enable_load_y_sums,

                input wire [BUS_WIDTH-1:0] load_in,
                output reg [DATA_WIDTH-1:0] load_sum_x,
                output reg [DATA_WIDTH-1:0] load_sum_y,

                input wire [DATA_WIDTH-1:0] in_fixed_sum_x,
                input wire [DATA_WIDTH-1:0] in_fixed_sum_y
);
    //#########################################################################################################################
    // PARAMETERS
    //#########################################################################################################################

    //********************************************************
    // fixed parameters for the entire array

    parameter integer N = -1;                   // this really should be lowercase n, the number of PEs in the array
    parameter integer T = -1;
    parameter integer D = -1;
    parameter integer B = -1;
    parameter integer DATA_WIDTH = -1;
    
    parameter integer MSAD = -1;                // Maximum Sub-Array Depth
    parameter integer WSRD = -1;                // worst sum return depth, the number of cycles for a newly computed sum to arrive at the input of the farthest PE across all sub-arrays.    
    parameter integer RAM_CYCLES = -1;          // should be set to 1
    parameter integer MULT_CYCLES = -1;         // should be set to 0 for now
    parameter integer FIXED_SUM_CYCLES = -1;    // should be set to 1

    parameter integer BUS_WIDTH = -1;
    parameter integer MAX_SWAPS_PER_UPDATE = -1;
    parameter integer MAX_NUM_OF_UPDATES = -1;
    //********************************************************
    // fixed_pe stuff

    // fixed
    parameter integer CYCLES_PER_SWAP = 10;
    
    // calculated
    parameter integer SORT_CYCLES = 4*D*$clog2(D) + 2*D;
    parameter integer SCD = -1;
    //#########################################################################################################################
    // REGISTERS
    //#########################################################################################################################
    reg sum_mode;

    reg [$clog2(N+1)-1:0] load_counter;
    reg [$clog2(B+1)-1:0] start_delay_counter;
    reg [$clog2(SORT_CYCLES+1)-1:0] sort_counter;
    reg [$clog2(SCD+WSRD+2*N+1)-1:0] sum_cycle_counter;
    reg [$clog2(MAX_SWAPS_PER_UPDATE*CYCLES_PER_SWAP+1)-1:0] swap_cycle_counter;
    reg [$clog2(MAX_SWAPS_PER_UPDATE*CYCLES_PER_SWAP+1)-1:0] swap_cycle_counter_target;
    reg [$clog2(MAX_NUM_OF_UPDATES+1)-1:0] swap_set_counter;
    reg [$clog2(MAX_NUM_OF_UPDATES+1)-1:0] swap_set_counter_target;
    //#########################################################################################################################
    // LOGIC
    //#########################################################################################################################

    wire [DATA_WIDTH-1:0] in_fixed_sum_of_coord = (sum_mode == 0) ? in_fixed_sum_x : in_fixed_sum_y;
    //#########################################################################################################################
    // STATE MACHINE
    //#########################################################################################################################

    //********************************************************
    // State machine

    parameter integer START_DELAY = -1;

    localparam STATE_INIT = 0;
    localparam STATE_DUMMY_X = 1;
    localparam STATE_LOAD_X_SUMS = 2;
    localparam STATE_WAIT_DUMMY_Y = 3;
    localparam STATE_DUMMY_Y = 4;
    localparam STATE_LOAD_Y_SUMS = 5;
    localparam STATE_WAIT_PLACE = 6;
    localparam STATE_WAIT_START = 7;
    localparam STATE_WAIT_SORT = 8;
    localparam STATE_SUM = 9;
    localparam STATE_WAIT_SWAP = 10;

    reg [3:0] state;
    always @(posedge clk) begin
        if(rst) begin
            load_counter <= 0;
            enable_load_x_sums <= 0;
            enable_load_y_sums <= 0;
            start_delay_counter <= 0;
            sort_counter <= 0;
            sum_cycle_counter <= 0;
            swap_cycle_counter <= 0;
            enable_sums <= 0;
            sum_mode <= 0;
            out <= 0;
            swap_set_counter <= 0;
            state <= STATE_INIT;
        end
        else begin
        case(state)
        STATE_INIT: begin // 0
            load_counter <= 0;
            if(load_enable_in) begin
                swap_cycle_counter_target <= load_in;
                state <= STATE_DUMMY_X;
            end
        end
        STATE_DUMMY_X: begin // 1
            if(load_counter == 0) begin
               swap_set_counter_target <= load_in; 
            end
            if(load_counter == 6) begin
                load_counter <= 0;
                state <= STATE_LOAD_X_SUMS;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_LOAD_X_SUMS: begin // 2
            enable_load_x_sums <= 1;
            load_sum_x <= load_in;
            if(load_counter == N - 1) begin
                state <= STATE_WAIT_DUMMY_Y;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_WAIT_DUMMY_Y: begin
            enable_load_x_sums <= 0;
            if(load_enable_in) begin
                load_counter <= 0;
                state <= STATE_DUMMY_Y;
            end
        end
        STATE_DUMMY_Y: begin // 3
            if(load_counter == 6) begin
                load_counter <= 0;
                state <= STATE_LOAD_Y_SUMS;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_LOAD_Y_SUMS: begin // 4
            enable_load_y_sums <= 1;
            load_sum_y <= load_in;
            if(load_counter == N - 1) begin
                state <= STATE_WAIT_PLACE;
            end
            else begin
                load_counter <= load_counter + 1;
            end
        end
        STATE_WAIT_PLACE: begin
            enable_load_y_sums <= 0;     
            if(load_enable_in) begin
                state <= STATE_WAIT_START;
            end
        end
        STATE_WAIT_START: begin // 5
            if(start_delay_counter == B) begin
                start_delay_counter <= 0;
                state <= STATE_WAIT_SORT;
            end
            else begin
                start_delay_counter <= start_delay_counter + 1;
            end
        end
        STATE_WAIT_SORT: begin // 6
            if(sort_counter == SORT_CYCLES - 1) begin
                state <= STATE_SUM;
                sum_cycle_counter <= 0;
                enable_sums <= 1;
            end
            sort_counter <= sort_counter + 1;
        end
        //********************************************************
        // Sum computation
        STATE_SUM: begin // 7
            //****************************************************
            // Add the contribution from the fixed blocks
            out <= in + in_fixed_sum_of_coord;
            //****************************************************
            // Control 
            if(sum_cycle_counter == SCD - FIXED_SUM_CYCLES + N - 1) begin
                sum_mode <= 1;
            end
            if(sum_cycle_counter == (SCD - FIXED_SUM_CYCLES + WSRD + 2*N + 1)) begin
                state <= STATE_WAIT_SWAP;
                swap_set_counter <= swap_set_counter + 1;
                swap_cycle_counter <= 0;
                enable_sums <= 0;
                sum_mode <= 0;
            end
            sum_cycle_counter <= sum_cycle_counter + 1;        
        end
        STATE_WAIT_SWAP: begin // 8
            if(swap_cycle_counter == swap_cycle_counter_target-1) begin
                if(swap_set_counter == swap_set_counter_target) begin
                    state <= STATE_INIT;
                    swap_set_counter <= 0;
                    sort_counter <= 0;
                end
                else begin
                    state <= STATE_WAIT_SORT;
                    sort_counter <= 0;
                end
            end
            swap_cycle_counter <= swap_cycle_counter + 1;
        end
        endcase
        end
    end
    //********************************************************
endmodule