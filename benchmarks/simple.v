module simple(input wire clk, input wire i, output reg o);

always @(posedge clk) begin
	o <= ~ i;
end

endmodule
