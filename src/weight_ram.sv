module weight_ram (input wire clk,
                   input wire enable_weights,
                   output reg [DATA_WIDTH-1:0] out_weight,

                   input wire load,
                   input wire [DATA_WIDTH-1:0] in_weight
);

    parameter integer DATA_WIDTH = -1;
    parameter integer N = -1;
    parameter integer DELAY_CYCLES = -1;
    
    reg [$clog2(DELAY_CYCLES + 1)-1:0] counter = 0;
    reg [$clog2(N)-1:0] address = 0;

    reg [DATA_WIDTH-1:0] weights[0:N-1];

    always @(posedge clk) begin
        if(load) begin
            weights[address] <= in_weight;
            address <= address + 1;
        end
        else if(~load && ~enable_weights) begin
            address <= 0;
            counter <= 0;
        end
        else begin
            if(counter < DELAY_CYCLES) begin
                counter <= counter + 1;
            end
            else begin
                if(address == N - 1) begin
                    address <= 0;
                end
                else begin
                    address <= address + 1;
                end
            end
            out_weight <= weights[address];
        end
    end

endmodule