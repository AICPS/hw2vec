module top (O,I);
output [2:0] O;
input [7:0] I;
or (O[0],I[1],I[3],I[5],I[7]);
or (O[1],I[2],I[3],I[6],I[7]);
or (O[2],I[4],I[5],I[6],I[7]);
endmodule 
