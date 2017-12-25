from switchyard.lib.userlib import *

def main(net):
    my_interfaces = net.interfaces() 
    mymacs = [intf.ethaddr for intf in my_interfaces]
    mytable = []
    count = 0
    timer = 0
    while True:
        timer = timer + 1
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            return

        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))
        e = packet[0]
        entry = [e.src, input_port, 0]
        need_entry = 1

        # Dont insert if the entry is already present 
        for ent in mytable:
            if e.src == ent[0] and input_port == ent[1]:
                 need_entry = 0

        if need_entry == 1:
            count = count + 1
            # Evict entry which is least recently used
            if count > 5:
                 i = -1
                 min_index = 0
                 mini = mytable[0][2]
                 for ent in mytable:
                        i = i + 1
                        if (ent[2] < mini):
                             mini = ent[2]
                             min_index = i
                 mytable.pop(min_index)

            mytable.append(entry)

        if e.dst in mymacs:
            log_debug ("Packet intended for me")
        else:
            i = -1
            entry_found = 0
            for ent in mytable:
                i = i + 1
                if ent[0] == e.dst:
                    entry_found = 1
                    net.send_packet(ent[1], packet)
                    # Update the reference time
                    entry = [ent[0], ent[1], timer]
                    mytable.pop(i);
                    mytable.append(entry)
                    break 

            # If there is no entry, broadcast the packet
            if entry_found == 0:
                for intf in my_interfaces:
                    if input_port != intf.name:
                        log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                        net.send_packet(intf.name, packet)
	

    net.shutdown()
