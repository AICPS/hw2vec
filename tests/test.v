module top
  (
   input CLK, 
   input RST,
   input enable,
   input [31:0] value,
   output [7:0] led
  );
  reg [31:0] count;
  reg [7:0] state;
  reg temp;
  wire alpha;
  wire beta;
  assign led = ~(beta >> 7) | count[23:16] ^ (alpha << 7) & (beta << 7) && (alpha >> 7);
  assign temp = ~alpha;
  always @(posedge CLK, negedge CLK) begin
    if(RST) begin
      count <= 0;
      state <= 0;
    end else begin
      if(state == 0) begin
        if(enable) state <= 1;
      end else if(state == 1) begin
        state <= 2;
      end else if(state == 2) begin
        count <= count + value;
        state <= 0;
      end
    end
  end
endmodule