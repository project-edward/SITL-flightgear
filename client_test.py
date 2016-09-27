import zmq

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Waiting for messages from flightgear...")
socket.connect("tcp://localhost:5556")

socket.setsockopt_string(zmq.SUBSCRIBE, "GPS_MESSAGE")

while(True):
  string = socket.recv_string()
  print(string)
