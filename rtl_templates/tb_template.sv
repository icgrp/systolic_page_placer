`timescale 1ns/1ps

module test_tb();
    //################################################################################################
    // Control Signals
    reg clk = 0;
    reg reset = 0;
    //################################################################################################
    // Instantiate the placer
    parameter integer BUS_WIDTH = {BUS_WIDTH};
    parameter integer N = {N};

    wire complete;
    reg load_enable_in;
    reg [BUS_WIDTH-1:0] load_in;
    wire [BUS_WIDTH-1:0] unload_out;
    placer dut(.clk(clk),
               .rst(reset),
               .complete(complete),
               .load_enable_in(load_enable_in),
               .load_in(load_in),
               .unload_out(unload_out));
    //################################################################################################
    // Create a trace file, print out the placer's params
    integer trace_file;
    integer unload_file;

    initial begin
        $dumpfile("trace.fst");
        $dumpvars(0);

        trace_file = $fopen("{trace_file}","w");
        unload_file = $fopen("{unload_file}","w");
        $fwrite(trace_file,"state,pe_ty,pe_x,pe_y,blk_id,x,y,px,py,temp_blk_id,temp_x,temp_y,temperature\n");

        $display();
        $display("N",dut.N);
        $display("T",dut.T);
        $display("D",dut.D);
        $display("B",dut.B);
        $display("V",dut.V);
        $display("MAX_K",dut.MAX_K);
        $display("P",dut.P);
        $display("N_io",dut.N_io);
        $display("F_io",dut.F_io);
        $display();
        $display("MSAD",dut.MSAD);
        $display("WSRD",dut.WSRD);
        $display("RAM_CYCLES",dut.RAM_CYCLES);
        $display("MULT_CYCLES",dut.MULT_CYCLES);
        $display("FIXED_SUM_CYCLES",dut.FIXED_SUM_CYCLES);
        $display();
        $display("BUS_WIDTH",dut.BUS_WIDTH);
        $display();
    end
    //################################################################################################
    // Tap critical signals from the placer, and write the trace file as necessary
    integer phase = 0;

    always @(negedge dut.{sense_sub_array}.pe_x0_y0.debug_swapping) begin
        $display("%-15s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-15s%-10s%-10s%-10s","state","type","pe_x","pe_y","blk_id","blk_x","blk_y","px","py","temp_blk_id","temp_x","temp_y","temperature");
        $display("----------------------------------------------------------------------------------------------------------------------------------------------");
{swap_display_str}
        $display("");
{swap_write_str}
    end

    always @(negedge dut.{sense_sub_array}.pe_x0_y0.debug_sorting) begin
        $display("%-15s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-15s%-10s%-10s%-10s","state","type","pe_x","pe_y","blk_id","blk_x","blk_y","px","py","temp_blk_id","temp_x","temp_y","temperature");
        $display("----------------------------------------------------------------------------------------------------------------------------------------------");
{sort_display_str}
        $display("");
{sort_write_str}
    end

    always @(negedge dut.{sense_sub_array}.pe_x0_y0.debug_summing) begin
        $display("%-15s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-15s%-10s%-10s%-10s","state","type","pe_x","pe_y","blk_id","blk_x","blk_y","px","py","temp_blk_id","temp_x","temp_y","temperature");
        $display("----------------------------------------------------------------------------------------------------------------------------------------------");
{sum_display_str}
        $display("");
{sum_write_str}
    end
    //################################################################################################
    // Drive the placer

    initial begin
        reset = 1;
        #2
        reset = 0;
    end

    always begin
        #1 clk <= ~clk;
    end

    parameter integer HEADER_LENGTH = 1;
    parameter integer PACKET_LENGTH = 8 + N;
    parameter integer NUM_OF_PACKETS = N + 2;
    parameter integer MEM_DEPTH = HEADER_LENGTH+(PACKET_LENGTH*NUM_OF_PACKETS);

    reg [BUS_WIDTH:0] data[0:MEM_DEPTH-1];

    initial begin
        $readmemh("build/bitstream/bitstream.txt",data);
    end

    reg [3:0] state;
    reg [$clog2(MEM_DEPTH+1)-1:0] address;
    reg [15:0] step_counter;
    reg [15:0] packet_counter;
    reg [15:0] run_counter;
    

    // Modify as needed to test robustness of individual PE loading logic
    reg [15:0] packet_delay_counter;
    localparam PACKET_DELAY = 20;
    localparam FIXED_DELAY = 10;
    localparam NUM_OF_RUNS = 1;

    localparam STATE_0 = 0;
    localparam STATE_1 = 1;
    localparam STATE_2 = 2;
    localparam STATE_3 = 3;
    localparam STATE_4 = 4;
    localparam STATE_5 = 5;

    always @(posedge clk) begin
        if(reset) begin
            load_enable_in <= 0;
            load_in <= 0;
            address <= 1;           // skip the bitstream header
            step_counter <= 0;
            packet_counter <= 0;
            state <= STATE_0;

            packet_delay_counter <= 0;
            run_counter <= 0;
        end
        else begin
            case(state)
            STATE_0: begin
                if(packet_delay_counter == PACKET_DELAY) begin
                    load_enable_in <= 1;
                    load_in <= data[address];
                    address <= address + 1;
                    step_counter <= step_counter + 1;
                    packet_counter <= packet_counter + 1;
                    state <= STATE_1;

                    packet_delay_counter <= 0;
                end
                else begin
                    packet_delay_counter <= packet_delay_counter + 1;
                end
            end
            STATE_1: begin
                load_enable_in <= 0;
                load_in <= data[address];
                address <= address + 1;

                if(step_counter == PACKET_LENGTH - 1) begin
                    
                    $display("finished loading packet %d",packet_counter);
                    step_counter <= 0;
                    if(packet_counter != NUM_OF_PACKETS) begin
                        state <= STATE_0;
                    end
                    else begin
                        state <= STATE_2;
                    end
                end
                else begin
                    step_counter <= step_counter + 1;
                end
            end
            STATE_2: begin
                if(step_counter == FIXED_DELAY) begin
                    load_enable_in <= 1;
                    step_counter <= 0;
                    state <= STATE_3;
                end
                else begin
                    step_counter <= step_counter + 1;
                end
            end
            STATE_3: begin
                load_enable_in <= 0;

                if(complete) begin
                    run_counter <= run_counter + 1;
                    $display("unloaded %d",unload_out);
                    $fwrite(unload_file,"%0d\n",unload_out);
                    state <= STATE_4;
                end
            end
            STATE_4: begin
                if(complete) begin
                    $display("unloaded %d",unload_out);
                    $fwrite(unload_file,"%0d\n",unload_out);
                end
                else begin
                    if(run_counter == NUM_OF_RUNS) begin
                        $finish;
                        $fclose(trace_file);
                        $fclose(unload_file);
                    end
                    else begin
                        load_enable_in <= 0;
                        load_in <= 0;
                        address <= 0;
                        step_counter <= 0;
                        packet_counter <= 0;
                        state <= STATE_0;

                        packet_delay_counter <= 0;
                        run_counter <= run_counter + 1;
                    end
                end
            end
            endcase
        end
    end
    
    //################################################################################################
endmodule