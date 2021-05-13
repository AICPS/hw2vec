module top	(	sysclk,
				sysrstl,

				uartXMITdataH,
				xmitH,
				xmitdataH,
				xmitdoneH,

				uartRECdataH,
				recdataH,
				recreadyH
			);



input			sysclk;
input			sysrstl;


output			uartXMITdataH;
input			xmitH;
input	[7:0]	xmitdataH;
output			xmitdoneH;

input			uartRECdataH;
output	[7:0]	recdataH;
output			recreadyH;

reg	[7:0]	recdataH;
reg     [7:0]   recdataHtemp;
wire    [7:0]   recdataHrec;
wire			recreadyH;



uxmit  iXMIT(  .sysclk(sysclk),
				.sysrstl(sysrstl),

				.uartxmitH(uartXMITdataH),
				.xmitH(xmitH),
				.xmitdataH(xmitdataH),
				.xmitdoneH(xmitdoneH)
			);

urec iRECEIVER (   .sysrstl(sysrstl),
				.sysclk(sysclk),


				.uartdataH(uartRECdataH),

				.recdataH(recdataHrec),
				.recreadyH(recreadyH)

				);

always @(posedge sysclk or negedge sysrstl) begin
   if (~sysrstl) begin
      recdataH=0;
  end
   else begin
     recdataH=recdataHtemp;
   end
  end

assign recdataHtemp = ~sysrstl ? 1'b0 : recdataHrec;



endmodule

module urec (
				sysrstl,
				sysclk,


				uartdataH,


				recdataH,
				recreadyH

				);


input			sysrstl;
input			sysclk;

input			uartdataH;

output	[7:0]	recdataH;
output			recreadyH;



reg		[2:0]	nextstate, state;
reg				recdatH, recdatSyncH;
reg		[3:0]	bitCellcntrH;
reg				cntrresetH;
reg		[7:0]	pardataH;
reg				shiftH;
reg		[3:0]	recdbitCntrH;
reg				countH;
reg				rstCountH;
reg				recreadyH;
reg				recreadyInH;


wire	[7:0]	recdataH;


assign recdataH = pardataH;

always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) begin
     recdatSyncH <= 1;
     recdatH     <= 1;
  end else begin
     recdatSyncH <= uartdataH;
     recdatH     <= recdatSyncH;
  end


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) bitCellcntrH <= 0;
  else if (cntrresetH) bitCellcntrH <= 0;
  else bitCellcntrH <= bitCellcntrH + 1;


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) pardataH <= 0;
  else if(shiftH) begin
     pardataH[6:0] <= pardataH[7:1];
     pardataH[7]   <= recdatH;
  end


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) recdbitCntrH <= 0;
  else if (countH) recdbitCntrH <= recdbitCntrH + 1;
  else if (rstCountH) recdbitCntrH <= 0;




always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) state <= 3'b001;
  else state <= nextstate;


always @(state or recdatH or bitCellcntrH or recdbitCntrH)
begin

  nextstate  = state;
  cntrresetH = 1'b1;
  shiftH      = 1'b0;
  countH      = 1'b0;
  rstCountH   = 1'b0;
  recreadyInH= 1'b0;

  case (state)

    3'b001: begin
       if (~recdatH ) nextstate = 3'b010;
       else begin
         nextstate = 3'b001;
         rstCountH  = 1'b1;
         recreadyInH = 1'b1;
       end
    end

    3'b010: begin
       if (bitCellcntrH == 4'h4) begin
         if (~recdatH) nextstate = 3'b011;
         else nextstate = 3'b001;
       end else begin
         nextstate  = 3'b010;
		 cntrresetH = 1'b0;
       end
    end


	3'b011: begin
		if (bitCellcntrH == 4'hE) begin
           if (recdbitCntrH == 8)
             nextstate = 3'b101;
           else begin
             nextstate = 3'b100;
           end
        end else begin
             nextstate  = 3'b011;
             cntrresetH = 1'b0;
        end
    end

	3'b100: begin
		shiftH = 1'b1;
		countH = 1'b1;
		nextstate = 3'b011;
	end


    3'b101: begin
		nextstate = 3'b001;
        recreadyInH = 1'b1;
    end

    default: begin
       nextstate  = 3'bxxx;
       cntrresetH = 1'bx;
	   shiftH      = 1'bx;
	   countH      = 1'bx;
       rstCountH   = 1'bx;
       recreadyInH  = 1'bx;

    end

  endcase


end


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) recreadyH <= 0;
  else recreadyH <= recreadyInH;




endmodule

module uxmit(	sysclk,
				sysrstl,

				uartxmitH,
				xmitH,
				xmitdataH,
				xmitdoneH
			);

input			sysclk;
input			sysrstl;
output			uartxmitH;
input			xmitH;
input	[7:0]	xmitdataH;
output			xmitdoneH;



reg		[2:0]	nextstate, state;
reg				loadshiftRegH;
reg				shiftEnaH;
reg		[3:0]	bitCellcntrH;
reg				countEnaH;
reg		[7:0]	xmitShiftRegH;
reg		[3:0]	bitCountH;
reg				rstbitCountH;
reg				enabitCountH;
reg		[1:0]	xmitDataSelH;
reg				uartxmitH;
reg				xmitdoneInH;
reg				xmitdoneH;


always @(posedge sysclk)
	if(xmitShiftRegH || xmitDataSelH)
  case (xmitDataSelH)
		2'b00: uartxmitH = 1'b0;
		2'b01:  uartxmitH = 1'b1;
	        2'b10: uartxmitH = 1'b0;
		2'b10: uartxmitH = xmitShiftRegH[0];
		default:    uartxmitH = 1'bx;
  endcase


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) bitCellcntrH <= 0;
  else if (countEnaH) bitCellcntrH <= bitCellcntrH + 1;
  else bitCellcntrH <= 0;



always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) xmitShiftRegH <= 0;
  else
	if (loadshiftRegH) xmitShiftRegH <= xmitdataH;
	else if (shiftEnaH) begin
		xmitShiftRegH[6:0] <= xmitShiftRegH[7:1];
		xmitShiftRegH[7]   <= 1'b1;
	end else xmitShiftRegH <= xmitShiftRegH;



always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) bitCountH <= 0;
  else if (rstbitCountH) bitCountH <= 0;
  else if (enabitCountH) bitCountH <= bitCountH + 1;



always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) state <= 3'b000;
  else state <= nextstate;

always @(posedge sysclk)
	if(state || xmitH || bitCellcntrH || bitCountH)
begin

	nextstate 		= state;
		loadshiftRegH	= 1'b0;
		countEnaH       = 1'b0;
		shiftEnaH       = 1'b0;
		rstbitCountH   = 1'b0;
		enabitCountH   = 1'b0;
	    xmitDataSelH    = 2'b01;
		xmitdoneInH	= 1'b0;

	case (state)

			3'b000: begin
			if (xmitH) begin
	                nextstate = 3'b010;
					loadshiftRegH = 1'b1;
                                bitCellcntrH <= 0;
                                bitCountH <= 0;
                                xmitShiftRegH <= 0;
			end else begin
					nextstate    = 3'b000;
					rstbitCountH = 1'b1;
	                xmitdoneInH  = 1'b1;
			end
		end



			3'b010: begin
	            xmitDataSelH    = 2'b00;
			if (bitCellcntrH == 4'hF)
					nextstate = 3'b011;
			else begin
					nextstate = 3'b010;
					countEnaH  = 1'b1;
			end
		end


			3'b011: begin
	            xmitDataSelH    = 2'b10;
			if (bitCellcntrH == 4'hE) begin
					if (bitCountH == 8)
						nextstate = 3'b101;
				else begin
						nextstate = 3'b100;
						enabitCountH = 1'b1;
				end
			end else begin
					nextstate = 3'b011;
					countEnaH  = 1'b1;
			end
		end



			3'b100: begin
	            xmitDataSelH    = 2'b10;
				nextstate = 3'b011;
				shiftEnaH  = 1'b1;
		end


			3'b101: begin
	            xmitDataSelH    = 2'b01;
			if (bitCellcntrH == 4'hF) begin
					nextstate   = 3'b000;
	                xmitdoneInH = 1'b1;
			end else begin
					nextstate = 3'b101;
					countEnaH = 1'b1;
			end
		end



		default: begin
			nextstate     = 3'bxxx;
				loadshiftRegH = 1'bx;
				countEnaH      = 1'bx;
	            shiftEnaH      = 1'bx;
	            rstbitCountH  = 1'bx;
	            enabitCountH  = 1'bx;
            xmitDataSelH   = 2'bxx;
	            xmitdoneInH   = 1'bx;
		end

    endcase

end


always @(posedge sysclk or negedge sysrstl)
  if (~sysrstl) xmitdoneH <= 0;
  else xmitdoneH <= xmitdoneInH;


endmodule


