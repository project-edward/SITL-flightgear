import xml.etree.ElementTree as ET
import asyncio
import time
import my_pb2
import zmq

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
    self._fg_chunks = []
    context = zmq.Context()
    self._publisher = context.socket(zmq.PUB)
    self._publisher.bind("tcp://*:5556")
    self._previous_time = time.time()

  def AddChunk(self, chunk):
    self._fg_chunks.append(chunk)

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
    for chunk_itm in zip(self._fg_chunks, msg_list):
      chunk_itm[0].SetValue(chunk_itm[0].GetType()(chunk_itm[1]))

    # TODO: Publish over protobuf
    self._publisher.send_string("{}".format(self._fg_chunks[0].GetValue()))
    person = my_pb2.Person()
    person.name = "fred"
    person.id = 0
    person.email = "something@something.com"

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

