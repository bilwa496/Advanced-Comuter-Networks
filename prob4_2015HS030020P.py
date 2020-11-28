from pox.core import core
from pox.lib.packet importpkt #import proper class as per the type of packet
from pox.lib.packet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr,EthAddr
from pox.lib.packet.ipv4 import ipv4
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Solution (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)
    self.mac_to_port = {}

  def pkt_TX (self, packet_in, out_port):= of.ofp_packet_out()
    msg.data = packet_in
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    self.connection.send(msg)
  
  def pkt_Processing (self, event):
    packet = event.parsed 
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
    packet_in = event.ofp 
    if packet.type == ethernet.IP_TYPE:
      ip_packet = event.parsed.find("ipv4")
      src_ip = ip_packet.srcip
      dst_ip = ip_packet.dstip
      log.debug(str(src_ip) + " " + str(dst_ip))
    if packet.type == packet.ARP_TYPE:
      if packet.payload.opcode == arp.REQUEST:
        print("ARP Request: "+str(packet.payload))
      if packet.payload.opcode == arp.REPLY:
        print("ARP Reply: "+str(EthAddr(packet.src)))
    self.switchForm(packet, packet_in)

  def switchForm (self, packet, packet_in):
    if packet.src not in self.mac_to_port:
        self.mac_to_port[packet.src] = packet_in.in_port
    if packet.dst in self.mac_to_port:
      self.pkt_TX(packet_in, self.mac_to_port[packet.dst])
      log.debug("Installing flow...")
      msg = of.ofp_flow_mod()
      msg.match.dl_dst = packet.dst
      msg.actions.append(of.ofp_action_output(port = self.mac_to_port[packet.dst]))
      self.connection.send(msg)
    else:
      self.pkt_TX(packet_in, of.OFPP_ALL)

  def hubForm (self, packet, packet_in):
    self.pkt_TX(packet_in, of.OFPP_ALL)

def launch ():
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Solution(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
