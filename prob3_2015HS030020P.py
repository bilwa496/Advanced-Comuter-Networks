from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from collections import defaultdict
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr,EthAddr
from pox.lib.packet.ipv4 import ipv4
from time import sleep
import struct
from collections import namedtuple
from pox.lib.revent import *
from pox.lib.recoco import Timer
from time import time
from pox.openflow.of_json import *

log = core.getLogger()
starttime = 0
switches=0
SwitchMap={}
w, h = 4, 4;
Matrix = [[0 for x in range(w)] for y in range(h)] 
def _handle_ConnectionUp(event):
    global switches
    global starttime
    switches+=1
    switchNo=int(dpid_to_str(event.dpid)[-1])
    print ('Conection Up:',switchNo)
    SwitchMap[switchNo]=event
    if switchNo == 1:
        msg = of.ofp_flow_mod()
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port = 3))
        SwitchMap[1].connection.send(msg)

        msg=of.ofp_flow_mod()
        msg.match.in_port = 3
        msg.match.dl_type = 0x0800
        msg.match.nw_dst = IPAddr("10.0.0.2")
        msg.match.priority = 60000
        msg.actions.append(of.ofp_action_output(port = 2))
        SwitchMap[1].connection.send(msg)

    if switchNo == 2:
        msg = of.ofp_flow_mod()
        msg.match.in_port = 1
        msg.match.dl_type = 0x0800
        msg.match.priority = 60000
        msg.match.nw_dst = IPAddr("10.0.0.4")
        msg.actions.append(of.ofp_action_output(port = 2))
        SwitchMap[2].connection.send(msg)

        msg=of.ofp_flow_mod()
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port = 1))
        SwitchMap[2].connection.send(msg)

    if switchNo == 3:
        msg = of.ofp_flow_mod()
        msg.match.in_port = 1
        msg.match.dl_type = 0x0800
        msg.match.priority = 60000
        msg.match.nw_dst = IPAddr("10.0.0.4")
        msg.actions.append(of.ofp_action_output(port = 2))
        SwitchMap[2].connection.send(msg)

        msg=of.ofp_flow_mod()
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port = 1))
        SwitchMap[2].connection.send(msg)

    if switchNo == 4:
        msg = of.ofp_flow_mod()
        msg.match.in_port = 1
        msg.match.dl_type = 0x0800
        msg.match.priority = 60000
        msg.match.nw_dst = IPAddr("10.0.0.3")
        msg.actions.append(of.ofp_action_output(port = 2))
        SwitchMap[2].connection.send(msg)

        msg=of.ofp_flow_mod()
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port = 1))
        SwitchMap[2].connection.send(msg)

    if switches ==4:
        starttime = time()
        for i in range(1,3):
            msg=of.ofp_flow_mod()
            msg.match.in_port = 1;
            if i == 2:
                msg.actions.append(of.ofp_action_output(port = 2))
            msg.actions.append(of.ofp_action_output(port = 3))
            SwitchMap[i].connection.send(msg)

            msg=of.ofp_flow_mod()
            msg.match.in_port = 3
            msg.actions.append(of.ofp_action_output(port = 1))
            if i == 1:
                msg.actions.append(of.ofp_action_output(port = 2))
            SwitchMap[i].connection.send(msg)
    
def _handle_flowstats_received(event):
    #Uncomment the following line to view the flowstats received
    print 'Printing Stats of switch',event.connection.dpid,' is \n',flow_stats_to_list(event.stats)
    global switches
    global starttime
    #Iterating through All the flows received
    for f in event.stats:
        #Fetching the output port from the sublist in the flow entry
        for act in f.actions:                    
            outport = act.port
        #Use the 2D Matrix predefined above named Matrix to store the number of bytes
        #One dimension will correspond to switch number and Second dimension will correspond to the port of that switch
        #Write Algorithm to map the flow byte count to the byte count of each port of switch
    for i in range(1,4):           #i.e. For all the ports on a switch
        print("Switch ",event.connection.dpid," Link on Port ",i,": ",  Use Matrix to print the values," Bytes/s")
        #Do the needful with the 2D Matrix after processing the flows      

def Prober():
    if switches ==4 :
        for connection in core.openflow._connections.values(): 
            print '----->>>  ',connection
            connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))


def launch():
    
    core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUp)
    core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received) 
    Timer(1.0, Prober, recurring = True)

