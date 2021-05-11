`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2020 12:29:50 AM
// Design Name: 
// Module Name: ALU
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module ALU(
    input [31:0] a,  
    input [31:0] b, 
    input [3:0] alu_control,
    output zero, 
    output reg [31:0] alu_result);  
    
 always @(*)
 begin   
      case(alu_control)  
      4'b0000: alu_result = a & b; // and  
      4'b0001: alu_result = a | b; // or  
      4'b0010: alu_result = a + b; // add  
      4'b0100: alu_result = a ^ b; //xor
      4'b0101: alu_result = a * b; //mult
      4'b0110: alu_result = a - b; // sub,beq 
      4'b0111: alu_result = (a<b) ? 1 : 0; //slt
      4'b1000: alu_result = a << b[10:6]; //sll
      4'b1001: alu_result = a >> b[10:6]; //srl
      4'b1010: alu_result = $signed(a) >>> b[10:6]; //sra
      4'b1011: alu_result = a / b; //div
      4'b1100: alu_result = ~(a | b); //nor
 
      default: alu_result = a + b; // add  
      endcase  
 end  
 assign zero = (alu_result==32'd0) ? 1'b1: 1'b0;

endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2020 04:24:03 AM
// Design Name: 
// Module Name: ALUControl
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module ALUControl(
    input [1:0] ALUOp, 
    input [5:0] Function,
    output reg[3:0] ALU_Control);  

wire [7:0] ALUControlIn;  
 assign ALUControlIn = {ALUOp,Function};  
 always @(ALUControlIn)  
 casex (ALUControlIn)  
  8'b10100100: ALU_Control=4'b0000; //and
  8'b11xxxxxx: ALU_Control=4'b0000; //andi
  8'b10100101: ALU_Control=4'b0001; //or
  8'b00xxxxxx: ALU_Control=4'b0010; //addi,lw,sw
  8'b10100000: ALU_Control=4'b0010; //add
  8'b10011000: ALU_Control=4'b0101; //mult
  8'b10100010: ALU_Control=4'b0110; //sub
  8'b01xxxxxx: ALU_Control=4'b0110; //beq
  8'b10101010: ALU_Control=4'b0111; //slt
  8'b10000000: ALU_Control=4'b1000; //sll
  8'b10000010: ALU_Control=4'b1001; //srl
  8'b10000011: ALU_Control=4'b1010; //sra
  8'b10011010: ALU_Control=4'b1011; //div
  8'b10100110: ALU_Control=4'b0100; //xor
  8'b10100111: ALU_Control=4'b1100; //nor
  default: ALU_Control=4'b0000;  
  endcase  
 endmodule  



`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2020 04:18:43 AM
// Design Name: 
// Module Name: control
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module control(
    input reset,
    input[5:0] opcode,  
    output reg reg_dst, mem_to_reg, 
    output reg [1:0] alu_op,  
    output reg mem_read, mem_write, alu_src, reg_write, branch, jump 
    );


always @(*)  
 begin  
      if(reset == 1'b1) begin  
                reg_dst = 1'b0;  
                mem_to_reg = 1'b0;  
                alu_op = 2'b10;  
                mem_read = 1'b0;  
                mem_write = 1'b0;  
                alu_src = 1'b0;  
                reg_write = 1'b0;      
      end  
      else begin  
      case(opcode)   
      6'b000000: begin // [add, and, or, sub] <- original functions [nor, slt, xor, mult, div] <- added fucntions
                reg_dst = 1'b1;  
                mem_to_reg = 1'b0;  
                alu_op = 2'b10;  
                mem_read = 1'b0;  
                mem_write = 1'b0;  
                alu_src = 1'b0;  
                reg_write = 1'b1;
                branch = 1'b0;
                jump = 1'b0;   
                end                
      6'b001000: begin // addi <- original function 
                reg_dst = 1'b0;  
                mem_to_reg = 1'b0;  
                alu_op = 2'b00;  
                mem_read = 1'b0;  
                mem_write = 1'b0;  
                alu_src = 1'b1;  
                reg_write = 1'b1;
                branch = 1'b0; 
                jump = 1'b0;                  
                end 
      6'b100011: begin // lw <- original function  
                reg_dst = 1'b0;  
                mem_to_reg = 1'b1;  
                alu_op = 2'b00;    
                mem_read = 1'b1;  
                mem_write = 1'b0;  
                alu_src = 1'b1;  
                reg_write = 1'b1;
                branch = 1'b0; 
                jump = 1'b0;                  
                end  
      6'b101011: begin // sw <- original function  
                reg_dst = 1'b0;  
                mem_to_reg = 1'b0;  
                alu_op = 2'b00;    
                mem_read = 1'b0;  
                mem_write = 1'b1;  
                alu_src = 1'b1;  
                reg_write = 1'b0;  
                branch = 1'b0;
                jump = 1'b0;                
                end  
      6'b001100: begin //andi <- added function
                reg_dst = 1'b0;  
                mem_to_reg = 1'b0;  
                alu_op = 2'b11;    
                mem_read = 1'b0;  
                mem_write = 1'b0;  
                alu_src = 1'b1;  
                reg_write = 1'b1; 
                branch = 1'b0; 
                jump = 1'b0;
                end     
      6'b000100: begin //beq <- added function
                reg_dst = 1'b0;
                mem_to_reg = 1'b0;
                alu_op = 2'b01;
                mem_read = 1'b0;
                mem_write = 1'b0;
                alu_src = 1'b0;
                reg_write = 1'b0;
                branch = 1'b1;
                jump = 1'b0;
                end
      6'b110000: begin //sll, srl, sra <- added functions
                reg_dst = 1'b1;
                mem_to_reg = 1'b0;
                alu_op = 2'b10;
                mem_read = 1'b0;
                mem_write = 1'b0;
                alu_src = 1'b1;
                reg_write = 1'b1;
                branch = 1'b0;
                jump = 1'b0;
                end        
      6'b000010: begin //jump <- added function
                reg_dst = 1'b0;
                mem_to_reg = 1'b0;
                alu_op = 2'bxx; //?
                mem_read = 1'b0;
                mem_write = 1'b0;
                alu_src = 1'b0;
                reg_write = 1'b0;
                branch = 1'b0;
                jump = 1'b1;
                end                          
      endcase
      end  
 end 
 endmodule `timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/16/2020 02:31:52 PM
// Design Name: 
// Module Name: datapath
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module datapath(
    input clk, reset, 
    input reg_dst, reg_write,
    input alu_src, pc_src, 
    input mem_read, mem_write,
    input mem_to_reg, 
    input branch, jump,
    input [3:0] ALU_Control, 
    output [31:0] datapath_result,
    output [5:0] inst_31_26, 
    output [5:0] inst_5_0
    );
    
    reg [9:0] pc; 
    wire [9:0] pc_plus4;// = 6'b000000;
    wire [9:0] pc_next;
    wire [31:0] instr;
    wire [4:0] write_reg_addr;
    wire [31:0] write_back_data;
    wire [31:0] reg1, reg2;
    wire [31:0] imm_value;
    wire [31:0] alu_in2;
    wire zero;
    wire [31:0] alu_result;
    wire [31:0] mem_read_data;
    
    wire [31:0] branch_imm;
    wire branch_sel;
    wire [31:0]mux_branch_result;
    wire [27:0] jump_addr;
    
    always @(posedge clk or posedge reset)  
    begin   
      if(reset)   
           pc <= 10'b0000000000;
      else  
           pc <= pc_next;  
    end  
 
    assign pc_plus4 = pc + 10'b0000000100;
        
    instruction_mem inst_mem (
        .read_addr(pc),
        .data(instr));
        
    assign inst_31_26 = instr[31:26];
    assign inst_5_0 = instr[5:0];
    
    mux2 #(.mux_width(5)) reg_mux 
    (   .a(instr[20:16]),
        .b(instr[15:11]),
        .sel(reg_dst),
        .y(write_reg_addr));
        
    register_file reg_file (
        .clk(clk),  
        .reset(reset),  
        .reg_write_en(reg_write),  
        .reg_write_dest(write_reg_addr),  
        .reg_write_data(write_back_data),  
        .reg_read_addr_1(instr[25:21]), 
        .reg_read_addr_2(instr[20:16]), 
        .reg_read_data_1(reg1),
        .reg_read_data_2(reg2));  
        
    sign_extend sign_ex_inst (
        .sign_ex_in(instr[15:0]),
        .sign_ex_out(imm_value));
        
    mux2 #(.mux_width(32)) alu_mux 
    (   .a(reg2),
        .b(imm_value),
        .sel(alu_src),
        .y(alu_in2));
        
    ALU alu_inst (
        .a(reg1),
        .b(alu_in2),
        .alu_control(ALU_Control),
        .zero(zero),
        .alu_result(alu_result));
        
    data_memory data_mem (
        .clk(clk),
        .mem_access_addr(alu_result),
        .mem_write_data(reg2),
        .mem_write_en(mem_write),
        .mem_read_en(mem_read),
        .mem_read_data(mem_read_data));
        
     mux2 #(.mux_width(32)) writeback_mux 
    (   .a(alu_result),
        .b(mem_read_data),
        .sel(mem_to_reg),
        .y(write_back_data)); 
        
     assign branch_imm = pc_plus4 + (imm_value << 2);
     assign branch_sel = branch & zero;
     mux2 #(.mux_width(32)) branch_mux
     (  .a(pc_plus4),
        .b(branch_imm),
        .sel(branch_sel),
        .y(mux_branch_result));
        
     assign jump_addr = {4'b0000, instr[25:0] << 2};
     mux2 #(.mux_width(10)) jump_mux
     (  .a(mux_branch_result[9:0]),
        .b(jump_addr[9:0]),
        .sel(jump),
        .y(pc_next));
        
    assign datapath_result = write_back_data;
endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2020 12:40:29 AM
// Design Name: 
// Module Name: data_memory
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module data_memory(
    input clk,
    input [31:0] mem_access_addr,
    input [31:0] mem_write_data,
    input mem_write_en,
    input mem_read_en,
    output [31:0] mem_read_data);
    
    integer i;  
    reg [31:0] ram [255:0];  
    wire [7 : 0] ram_addr = mem_access_addr[9 : 2];  
    
    initial 
    begin  
        for(i=0;i<256;i=i+1)  
            ram[i] <= 32'd0;  
        end  
        always @(posedge clk) begin  
            if (mem_write_en)  
                ram[ram_addr] <= mem_write_data;  
            end  
      
      assign mem_read_data = (mem_read_en==1'b1) ? ram[ram_addr]: 32'd0;
      
endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/16/2020 03:11:42 PM
// Design Name: 
// Module Name: instruction_mem
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module instruction_mem(
    input [9:0] read_addr,
    output [31:0] data
    );
    
    reg [31:0] rom [255:0];  
    
    initial  
    begin  
		                                                // instruction           alu result in hex       register content       mem content
														
        /*rom[0]  = 32'b00100000000000010000000000000110; // addi r1,r0,#6                 6                    r1=6                   -
        rom[1]  = 32'b00100000000000100000000000001110; // addi r2,r0,#e                 e                    r2=e                   -
        rom[2]  = 32'b00100000000000110000000001001110; // addi r3,r0,#4e                4e                   r3=4e                  -
        rom[3]  = 32'b00100000000001000000000011010010; // addi r4,r0,#d2                d2                   r4=d2                  -
        rom[4]  = 32'b00100000000001011110000110010101; // addi r5,r0,#e195           ffffe195                r5=ffffe195            -
        rom[5]  = 32'b00100000000001101111111000010010; // addi r6,r0,#fe12           fffffe12                r6=fffffe12            -
        rom[6]  = 32'b00000000001001000011100000100000; // add r7,r1,r4                  d8                   r7=d8                  -
        rom[7]  = 32'b00000000011001010100000000100000; // add r8,r3,r5               ffffe1e3                r8=ffffe1e3            -
        rom[8]  = 32'b10101100001001110000000000000010; // sw mem[r1+2] <= r7            8                    -                   mem[2]=d8
        rom[9]  = 32'b10101100100010001111111111111110; // sw mem[r4-2] <= r8            d0                   -                   mem[52]=ffffe1e3
        rom[10] = 32'b00000000100000100100100000100010; // sub r9,r4,r2                  C4                   r9=c4                  -
        rom[11] = 32'b00000000001001010101000000100010; // sub r10,r1,r5                1e71                  r10=1e71               -
        rom[12] = 32'b10101101001010100000000000000000; // sw mem[r9+0] <= r10           c4                   -                   mem[49]=1e71
        rom[13] = 32'b00000001001001110101100000100101; // or r11,r9,r7                  dc                   r11=dc                 -
        rom[14] = 32'b00000001000010100110000000100100; // and r12,r8,r10                61                   r12=61                 -
        rom[15] = 32'b10001100001011010000000000000010; // r13 =mem[r1+2]                8                    r13=d8                 -
        rom[16] = 32'b10001100100011101111111111111110; // r14 =mem[r4-2]                d0                   r14=ffffe1e3           -
        rom[17] = 32'b10001101001011110000000000000000; // r15 =mem[r9+0]                c4                   r15=1e71               - 
        
       //nor
        rom[0] = 32'b00100000000000010000000000000001; // addi r1,r0,#1                  2                    r1=2                   -
        rom[1] = 32'b00100000000000100000000000001001; // addi r2,r0,#9                  9                    r2=9                   -        
        rom[2] = 32'b00000000001000100001100000100111; // nor r3,r1,r2                fffffff6                r3=fffffff6            -
        
        //slt
        rom[0] = 32'b00100000000000100000000000000001; // addi r2,r0,#1                  1                    r2=1                   -       
        rom[1] = 32'b00100000000000010000000000000100; // addi r1,r0,#4                  4                    r1=4                   -       
        rom[3] = 32'b00000000010000010001100000101010; // slt r3,r2,r1                   0                    r3=0                   -
        rom[4] = 32'b00000000001000100001100000101010; // slt r3,r1,r2                   1                    r3=1                   - 
        
        //xor
        rom[0] = 32'b00100000000000010000000000101101; // addi r1,r0,#2d                2d                    r1=2d                  -
        rom[1] = 32'b00100000000000100000000000010101; // addi r2,r0,#15                15                    r2=15                  -
        rom[2] = 32'b00000000001000100001100000100110; // xor r3,r1,r2                  38                    r3=38                  -
        
        //mult and divide
        rom[0] = 32'b00100000000000010000000000000010; // addi r1,r0,#2                  2                    r1=2                   -
        rom[1] = 32'b00100000000000100000000000000011; // addi r2,r0,#3                  3                    r2=3                   -
        rom[2] = 32'b00000000001000100001100000011000; // mult r3,r1,r2                  6                    r3=6                   -      
        rom[3] = 32'b00000000011000010010000000011010; // div r4,r3,r1                   3                    r4=3                   -
          
        //sll, slr
        rom[0] = 32'b00100000000000010000000000000010; // addi r1,r0,#2                  2                    r1=2                   -
        rom[1] = 32'b11000000001000000001000111000000; // sll r2,r1,#7                  100                   r2=100                 -
        rom[2] = 32'b11000000001000000001100001000010; // srl r3,r1,#1                   1                    r3=1                   - 
        
        //sra
        rom[0] = 32'b00100000000000011111111111111000; // addi r1,r0,#-8                -8                    r1=-8                  -
        rom[1] = 32'b11000000001000000001000010000011; // sra r2,r1,#2                  -2                    r2=-2                  - 
        rom[2] = 32'b00100000000000110110000000000000; // addi r3,r0,#-8               6000                   r3=6000                -
        rom[3] = 32'b11000000011000000010000101000011; // sra r4,r3,#5                 300                    r4=300                 -  */       
        
        //branch
        rom[0] = 32'b00100000000000010000000000000001; // addi r1,r0,#1                  1                    r1=1                   -
        rom[1] = 32'b00100000000000100000000000000001; // addi r2,r0,#1                  1                    r2=1                   -
        rom[2] = 32'b00010000001000100000000000000010; // beq r1,r2 #2  
        rom[3] = 32'b00100000000000110000000000000011; // addi r3,r0,#3                  3                    r3=3                   -
        rom[4] = 32'b00100000000000110000000000000100; // addi r3,r0,#4                  4                    r3=4                   -
        rom[5] = 32'b00100000000000110000000000000101; // addi r3,r0,#5                  5                    r3=5                   - 
        rom[6] = 32'b00010000001000110000000000000001; // beq r1,r3 #1  
        rom[7] = 32'b00100000000000110000000000000110; // addi r3,r0,#6                  6                    r3=6                   -
        rom[8] = 32'b00100000000000110000000000000111; // addi r3,r0,#7                  7                    r3=7                   - 
           
        
        /* //jump
        rom[0] = 32'b00100000000000110000000000000011; // addi r2,r0,#3                  3                    r2=3                   -
        rom[1] = 32'b00100000000000110000000000000100; // addi r2,r0,#4                  4                    r2=4                   -
        rom[2] = 32'b00100000000000110000000000000101; // addi r2,r0,#5                  5                    r2=5                   -            
        rom[3] = 32'b00001000000000000000000000000101; // jump #5                                                                    -
        rom[4] = 32'b00100000000000110000000000000110; // addi r2,r0,#6                  6                    r2=6                   -
        rom[5] = 32'b00100000000000110000000000000111; // addi r2,r0,#7                  7                    r2=7                   -   */          

      end  
      
      assign data = rom[read_addr[9:2]];

endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/16/2020 02:10:56 PM
// Design Name: 
// Module Name: top
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module processor(
    input clk, reset,  
    output[31:0] result
    );
    
    wire reg_dst, reg_write, alu_src, pc_src, mem_read, mem_write, mem_to_reg;
    wire [3:0] ALU_Control;
    wire [5:0] inst_31_26, inst_5_0;
    wire [1:0] alu_op;
    wire branch, jump;
    
    datapath datapath_unit(
        .clk(clk), 
        .reset(reset), 
        .reg_dst(reg_dst), 
        .reg_write(reg_write),
        .alu_src(alu_src), 
        .pc_src(pc_src), 
        .mem_read(mem_read), 
        .mem_write(mem_write),
        .mem_to_reg(mem_to_reg), 
        .ALU_Control(ALU_Control), 
        .datapath_result(result),
        .branch(branch),
        .jump(jump),
        .inst_31_26(inst_31_26), 
        .inst_5_0(inst_5_0));
                           
    control control_unit(
        .reset(reset),
        .opcode(inst_31_26),
        .reg_dst(reg_dst), 
        .mem_to_reg(mem_to_reg),
        .alu_op(alu_op),
        .mem_read(mem_read),  
        .mem_write(mem_write),
        .alu_src(alu_src),
        .reg_write(reg_write),
        .branch(branch),
        .jump(jump)); 

    ALUControl ALU_Contrsol_unit(
        .ALUOp(alu_op),
        .Function(inst_5_0),
        .ALU_Control(ALU_Control));  
endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/16/2020 03:56:06 PM
// Design Name: 
// Module Name: mux
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module mux2 #(parameter mux_width= 32)
(   input [mux_width-1:0] a,b,
    input sel,
    output [mux_width-1:0] y
    );
    
    assign y = sel ? b : a;
endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/16/2020 04:05:23 PM
// Design Name: 
// Module Name: register_file
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module register_file(
    input clk, reset,  
    input reg_write_en,  
    input [4:0] reg_write_dest,  
    input [31:0] reg_write_data,
    input [4:0] reg_read_addr_1, 
    input [4:0] reg_read_addr_2,  
    output [31:0] reg_read_data_1,  
    output [31:0] reg_read_data_2 
    );
    
    reg [31:0] reg_array [31:0];  
  
    always @ (posedge clk ) begin  
           if(reset) begin  
                reg_array[0] <= 32'b0;  
                reg_array[1] <= 32'b0;  
                reg_array[2] <= 32'b0;  
                reg_array[3] <= 32'b0;  
                reg_array[4] <= 32'b0;  
                reg_array[5] <= 32'b0;  
                reg_array[6] <= 32'b0;  
                reg_array[7] <= 32'b0; 
                reg_array[8] <= 32'b0;  
                reg_array[9] <= 32'b0;  
                reg_array[10] <= 32'b0;  
                reg_array[11] <= 32'b0;  
                reg_array[12] <= 32'b0;  
                reg_array[13] <= 32'b0;  
                reg_array[14] <= 32'b0;  
                reg_array[15] <= 32'b0;
                reg_array[16] <= 32'b0;  
                reg_array[17] <= 32'b0; 
                reg_array[18] <= 32'b0;  
                reg_array[19] <= 32'b0;  
                reg_array[20] <= 32'b0; 
                reg_array[21] <= 32'b0;  
                reg_array[22] <= 32'b0;  
                reg_array[23] <= 32'b0;  
                reg_array[24] <= 32'b0;  
                reg_array[25] <= 32'b0;  
                reg_array[26] <= 32'b0;  
                reg_array[27] <= 32'b0; 
                reg_array[28] <= 32'b0;  
                reg_array[29] <= 32'b0;  
                reg_array[30] <= 32'b0;  
                reg_array[31] <= 32'b0;     
           end  
           else begin  
                if(reg_write_en) begin  
                     reg_array[reg_write_dest] <= reg_write_data;  
                end  
           end  
      end  
      assign reg_read_data_1 = ( reg_read_addr_1 == 0)? 32'b0 : reg_array[reg_read_addr_1];  
      assign reg_read_data_2 = ( reg_read_addr_2 == 0)? 32'b0 : reg_array[reg_read_addr_2];  
endmodule
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/17/2020 12:11:26 AM
// Design Name: 
// Module Name: sign_extend
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module sign_extend(
    input [15:0] sign_ex_in,
    output reg [31:0] sign_ex_out
    );
    
    always @(*) begin
        sign_ex_out = { {16{sign_ex_in[15]}}, sign_ex_in };
    end
endmodule
