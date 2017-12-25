from switchyard.lib.userlib import *
import time

def main(net):
    my_interfaces = net.interfaces() 
    mymacs = [intf.ethaddr for intf in my_interfaces]
    htable = {}
    ttable = {}
    while True:
        # Check the table to remove outdated entries
        copy_ttable = deepcopy(ttable)
        for key,val in copy_ttable.items():
            diff = int(time.time() - float(val))
            if diff % 60 >= 10:
                del(htable[key])
                del(ttable[key])
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            return

        cur = time.time()
        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))
        e = packet[0]
        tup = {e.src : input_port}
        htable.update(tup)
        tup = {e.src : repr(cur)}
        ttable.update(tup)

        if e.dst in mymacs:
            log_debug ("Packet intended for me")
        else:
            if htable.get(e.dst) != None:
                port = htable.get(e.dst)
                net.send_packet(port, packet)
            else:
                # If entry is not present, broadcast the packet
                for intf in my_interfaces:
                    if input_port != intf.name:
                         log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                         net.send_packet(intf.name, packet)
	

    net.shutdown()
