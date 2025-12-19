`timescale 1ns / 1ps

module placer_interface(input wire clk,
                        input wire rst,
                        input wire done,
                        output reg ack,
                        
                        output reg [12:0] address,
                        output reg [31:0] data_out,
                        input wire [31:0] data_in,
                        output reg [3:0] we,
                        output wire ram_en,
                        output wire ram_rst
);

    assign ram_en = 1;
    assign ram_rst = 0;
    //*************************************************************************
    localparam N = {N};
    localparam NUM_OF_PACKETS = N + 2;
    localparam SIZE_OF_PACKET = N + 8;
    localparam SIZE_OF_UNLOAD = N;
    
    wire not_rst = ~rst;
    reg load_enable_in;
    wire [{BUS_WIDTH}-1:0] unload_out;
    wire complete;
    
    (* dont_touch = "yes" *) placer placer_inst(.clk(clk),
                       .rst(not_rst),
                       .load_enable_in(load_enable_in),
                       .complete(complete),
                       .load_in(data_in),
                       .unload_out(unload_out)
    );

    //*************************************************************************
    reg [$clog2(NUM_OF_PACKETS + 1)-1:0] packet_counter;
    reg [$clog2(SIZE_OF_PACKET + 1)-1:0] packet_step_counter;
    reg [3:0] state;
    localparam STATE_0 = 0;
    localparam STATE_1 = 1;
    localparam STATE_2 = 2;
    localparam STATE_3 = 3;
    localparam STATE_4 = 4;
    localparam STATE_5 = 5;
    localparam STATE_6 = 6;
    always @(posedge clk) begin
        if(~rst) begin
            we <= 0;
            ack <= 0;
            address <= 0;
            data_out <= 0;
            packet_counter <= 0;
            packet_step_counter <= 0;
            load_enable_in <= 0;
            state <= STATE_0;
        end
        else begin
        case(state)
        STATE_0: begin
            if(done) begin
                state <= STATE_1;
                address <= 32'h00_00_00_00;
            end
        end
        STATE_1: begin
            // BRAM read of address 0x00000000 takes in this cycle
            load_enable_in <= 1;
            address <= address + 4;
            packet_step_counter <= 0;
            state <= STATE_2;
        end
        STATE_2: begin
            // BRAM data read from address 0x00000000 is availible
            // in the first cycle in this state
            load_enable_in <= 0;

            if(packet_step_counter == SIZE_OF_PACKET - 1) begin
                ack <= 1;
                packet_counter <= packet_counter + 1;
                state <= STATE_3;
            end

            address <= address + 4;
            packet_step_counter <= packet_step_counter + 1;
        end
        STATE_3: begin
            if(~done) begin
                ack <= 0;
                if(packet_counter != NUM_OF_PACKETS) begin
                    state <= STATE_0;
                end
                else begin
                    state <= STATE_4;
                end
            end
        end
        STATE_4: begin
            if(done) begin
                address <= 32'h00_00_00_00;
                packet_step_counter <= 0;
                load_enable_in <= 1;
                state <= STATE_5;
            end
        end
        STATE_5: begin
            load_enable_in <= 0;
            if(complete) begin
                data_out <= unload_out;
                we <= 4'b1111;
                state <= STATE_6;
            end
        end
        STATE_6: begin
            if(complete) begin
                data_out <= unload_out;
                address <= address + 4;
            end
            else begin
                ack <= 1;
                we <= 0;
                packet_counter <= 0;
                state <= STATE_3;
            end
        end
        endcase
        end
    end
    //*************************************************************************

endmodule
