import xml.etree.ElementTree as ET
import asyncio
import time
import protos.core_pb2 as core_pb2
import zmq
from collections import OrderedDict

class FgChunk:
  def __init__(self, node_name, name, unit, unit_format):
    self._node_name = node_name
    self._name = name
    self._unit = unit
    self._format = unit_format
    self._value = None

  def SetValue(self, value):
    self._value = value

  def GetType(self):
    return eval(self._unit)

  def GetValue(self):
    return self._value

class FgParseSend:
  def __init__(self):
    self._fg_chunks = OrderedDict([])
    context = zmq.Context()
    self._publisher = context.socket(zmq.PUB)
    self._publisher.bind("tcp://*:5556")
    self._previous_time = time.time()

  def AddChunk(self, chunk):
    self._fg_chunks[chunk._name] = chunk

  def SetupFromXML(self, filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    chunks = root.find('generic').find('output').findall('chunk')
    for chunk in chunks:
      fg_chunk = FgChunk(chunk.find('node').text, 
                         chunk.find('name').text, 
                         chunk.find('type').text, 
                         chunk.find('format').text)
      self.AddChunk(fg_chunk)

  def connection_made(self, transport):
    self._transport = transport

  def datagram_received(self, data, addr):
    message = data.decode()
    msg_list = message.split()
    if (len(self._fg_chunks) != len(msg_list)):
      print("Packet Error: Not the correct size")
    for chunk_itm in zip(self._fg_chunks.values(), msg_list):
      chunk_itm[0].SetValue(chunk_itm[0].GetType()(chunk_itm[1]))

    imu = core_pb2.IMU()
    imu.roll = self._fg_chunks["roll-deg"].GetValue()
    imu.pitch = self._fg_chunks["pitch-deg"].GetValue()
    imu.yaw = self._fg_chunks["heading-magnetic-deg"].GetValue()
    imu_string = str(imu.SerializeToString())

    gps = core_pb2.GPS()
    gps.lat = self._fg_chunks["latitude-deg"].GetValue()
    gps.lon = self._fg_chunks["longitude-deg"].GetValue()
    gps.altitude = self._fg_chunks["altitude-ft"].GetValue()
    gps_string = str(gps.SerializeToString())

    self._publisher.send_string("IMU_MESSAGE:{}".format(imu_string))
    self._publisher.send_string("GPS_MESSAGE:{}".format(imu_string))

if __name__ == '__main__':
  fg_parser = FgParseSend()
  fg_parser.SetupFromXML('fg_out.xml')
  loop = asyncio.get_event_loop()
  listen = loop.create_datagram_endpoint(
    lambda : fg_parser, local_addr=('0.0.0.0', 6789))
  transport, protocol = loop.run_until_complete(listen)

  try:
      loop.run_forever()
  except KeyboardInterrupt:
      pass

  transport.close()
  loop.close()

