#Flightgear SITL
##Helpful Information
###FlightGear
To startup the property tree server: `fgfs --httpd=<port>`

To startup the generic output: `fgfs --generic=socket,out,50,localhost,6789,udp,fg_out`

To listen to FlightGear output, `nc -ul <port>`