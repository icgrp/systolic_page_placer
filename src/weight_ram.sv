module weight_ram (input wire clk,
                   input wire enable_weights,
                   output wire [DATA_WIDTH-1:0] out_weight,

                   input wire load,
                   input wire [DATA_WIDTH-1:0] in_weight
);

    parameter integer DATA_WIDTH = -1;
    parameter integer N = -1;
    parameter integer DELAY_CYCLES = -1;
    parameter integer RAM_CYCLES = -1;
    
    reg [$clog2(DELAY_CYCLES + 2)-1:0] counter = 0;
    reg [$clog2(N)-1:0] address = 0;

    (* ram_style = "block" *)
    reg [DATA_WIDTH-1:0] weights[0:N-1];

    // Stage 0 is the registered RAM read
    reg [DATA_WIDTH-1:0] output_pipeline [0:RAM_CYCLES-1];
    integer op_i;

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
                // Synchronous RAM read: counts as one RAM cycle.
                output_pipeline[0] <= weights[address];

                // Add RAM_CYCLES - 1 output pipeline stages.
                for(op_i = 1; op_i < RAM_CYCLES; op_i = op_i + 1) begin
                    output_pipeline[op_i] <= output_pipeline[op_i - 1];
                end

                address <= (address == N - 1) ? 0 : address + 1;
            end
        end
    end

    assign out_weight = output_pipeline[RAM_CYCLES - 1];

endmodule