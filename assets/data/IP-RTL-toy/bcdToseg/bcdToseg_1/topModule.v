/*
	7 segment code
	MSB => a
	LSB => g
	active low outputs
*/

`define s0 		7'b0000001
`define s1		7'b1001111
`define s2		7'b0010010
`define s3		7'b0000110
`define s4		7'b1001100
`define s5		7'b0100100
`define s6		7'b0100000
`define s7		7'b0001111
`define s8		7'b0000000
`define s9		7'b0000100
`define se		7'b0110000 //error

module top (A, x);
	input [3:0] x;
	output [6:0] A;
	reg[6:0] A;
	always@(*)
	begin
		case (x)
			4'b0000: A = `s0;
			4'b0001: A = `s1;
			4'b0010: A = `s2;
			4'b0011: A = `s3;
			4'b0100: A = `s4;
			4'b0101: A = `s5;
			4'b0110: A = `s6;
			4'b0111: A = `s7;
			4'b1000: A = `s8;
			4'b1001: A = `s9;
			default: A = `se;
		endcase
	end
endmodule
