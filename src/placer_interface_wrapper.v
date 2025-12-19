module placer_interface_wraper(input wire clk,
                        input wire rst,
                        input wire done,
                        output wire ack,
                        
                        output wire [12:0] address,
                        output wire [31:0] data_out,
                        input wire [31:0] data_in,
                        output wire [3:0] we,
                        output wire ram_en,
                        output wire ram_rst
);

    placer_interface placer_interface_inst(.clk(clk),
                                           .rst(rst),
                                           .done(done),
                                           .ack(ack),
                                           
                                           .address(address),
                                           .data_out(data_out),
                                           .data_in(data_in),
                                           .we(we),
                                           .ram_en(ram_en),
                                           .ram_rst(ram_rst));

endmodule