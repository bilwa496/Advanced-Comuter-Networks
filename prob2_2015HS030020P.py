from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr,EthAddr
from pox.lib.packet.ipv4 import ipv4
from pox.lib.revent import *
from pox.openflow.of_json import *

log = core.getLogger()
switches = 0
SwitchMap = {}

def _handle_ConnectionUp(event):
    global switches
    switches+=1
    switchNo=int(dpid_to_str(event.dpid)[-1])
    SwitchMap[switchNo]=event
    def makeNew(inport, outport):
        msg = of.ofp_flow_mod()
        msg.match.in_port = inport
        for p in outport:
            msg.actions.append(of.ofp_action_output(port = p))
        return msg
    def newMSG(ip_src, ip_dest, port, out_port): #Creating newer flow rules
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x0800
        msg.match.nw_src = IPAddr(ip_src)
        msg.match.nw_proto = 6
        msg.match.tp_dst = port
        msg.match.nw_dst = IPAddr(ip_dest)
        msg.match.priority = 1000
        msg.actions.append(of.ofp_action_output(port = out_port))
        return msg
    def pktLoss(ip_src, ip_dest): #Restrictive Ping conditions
        msg = of.ofp_flow_mod()
        msg.match.nw_src = IPAddr(ip_src)
        msg.match.nw_dst = IPAddr(ip_dest)
        msg.match.priority = 1000
        return msg
    if switchNo == 1: #H1's Ping to others are possible along with a special case for H1 to H4
	SwitchMap[1].connection.send(makeNew(1, [2,3]))
	SwitchMap[1].connection.send(makeNew(2, [1]))
	SwitchMap[1].connection.send(makeNew(3, [1]))
	SwitchMap[1].connection.send(makeNew(4, [1]))
	SwitchMap[1].connection.send(newMSG("10.0.0.1", "10.0.0.4", 80, 3))
	SwitchMap[1].connection.send(newMSG("10.0.0.4", "10.0.0.1", 80, 3))
        SwitchMap[1].connection.send(pktLoss("10.0.0.2", "10.0.0.3")) #Imposing the restriction on ping of H2 to H3
        SwitchMap[1].connection.send(pktLoss("10.0.0.2", "10.0.0.4")) #Imposing the restriction on ping of H2 to H4
    if switchNo == 2: #H2 to H1 Ping is possible
	SwitchMap[2].connection.send(makeNew(1, [2]))
        SwitchMap[2].connection.send(makeNew(2, [1]))
    if switchNo == 3: #H2 to H1 Ping is possible
	SwitchMap[3].connection.send(makeNew(1, [2]))
        SwitchMap[3].connection.send(makeNew(2, [1]))
    if switchNo == 4: #H1's Ping to others are possible along with a special case for H1 to H4
	SwitchMap[4].connection.send(makeNew(1, [2,3]))
	SwitchMap[4].connection.send(makeNew(2, [1,3]))
	SwitchMap[4].connection.send(makeNew(3, [1,2]))
	SwitchMap[4].connection.send(makeNew(4, [1,2]))
	SwitchMap[4].connection.send(newMSG("10.0.0.4", "10.0.0.1", 80, 3))
	SwitchMap[4].connection.send(newMSG("10.0.0.1", "10.0.0.4", 80, 3))	  	

def launch():
    core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUp)
