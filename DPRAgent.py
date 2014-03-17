from DPRPacket import DPRPacket
import networkx as nx
import copy 

class DPRAgent:
    def __init__(self, my_id, G, timing_dat, in_buf_size = None, out_buf_size = None):
        """
        DPRAgent Constructor
        INPUTS:
        my_id        = This agent's unique id
        G            = The NetworkX graph object that holds network connectivity information
        timing_dat   = The DPRTimingData object that holds timing information specific to this agent
        in_buf_size  = The number of packets this agent can receive within a single operation loop
        out_buf_size = The number of packets this agent can send out after a single operation loop
        """
        self.tdat = copy.deepcopy(timing_dat) # DPRTimingData object
        
        self.in_buf_size = in_buf_size
        self.out_buf_size = out_buf_size

        self.in_buf = []
        self.out_buf = []
        
        self.fw_id_lists = [] # Forwarding id lists
        
        self.my_id = my_id

        self.G = G # The networkx graph object that stores connectivity information
        self.neighbor_list = G.neighbors(my_id)

        # Termination packet status flags
        self.pkt_rcvd = False
        self.pkt_term = False

    def get_fw_id_list(self, recv_pkt):
        """
        Computes the list of agent ids to forward this packet to
        """
        try: 
            # Check if the target is our neighbor
            self.neighbor_list.index(recv_pkt.target_agent_id)
            return set([recv_pkt.target_agent_id])
        except ValueError: 
            # If not, forward to all neighbors except the ones who have already
            # seen this message
            return set(self.neighbor_list) - set(recv_pkt.prop_chain_ids)

    def should_I_fw_pkt(self, recv_pkt):
        """
        Checks to see whether you should continue forwarding this packet
        """
        retval = True
        if(recv_pkt.target_agent_id == self.my_id):
            retval = False
        return retval

    def process_pkt(self, recv_pkt, meant_for_me):
        """
        Processes all packets meant for this agent
        """
        if meant_for_me:
            self.pkt_rcvd = True # A packet targetted towards this agent has been received
            print "************************************************************"
            print "Packet Received by Agent [%s]"%str(self.my_id)
            print "It was meant for Agent [%s]"%str(recv_pkt.target_agent_id)
            print "Propogation chain for packet, "
            print recv_pkt.prop_chain_ids
            print "Transmission arrival times for packet, "
            print recv_pkt.recv_global_timestamps
            print "************************************************************\n"
        else:
            self.pkt_term = True # A packet tergetted towards another agent terminated here

    def handle_pkts(self):
        """
        Decides what to do with the packets in in_buf (forward or not) and
        moves them appropriately.
        """
        for recv_pkt in self.in_buf:
            # TODO: Remove duplicate messages in the input buffer
            if(self.should_I_fw_pkt(recv_pkt)):
                fw_id_list = self.get_fw_id_list(recv_pkt)
                if(fw_id_list): # Check if the forwarding list is empty
                    self.out_buf.append(recv_pkt)
                    self.fw_id_lists.append(fw_id_list)
                else:
                    self.process_pkt(recv_pkt, False)
            else:
                self.process_pkt(recv_pkt, True)

        self.in_buf = [] # Clear the in buffer after processing received packets

    def create_and_send_pkt(self, target_agent_id):
            new_pkt = DPRPacket(self.my_id, target_agent_id)
            self.out_buf.append(new_pkt)
            self.fw_id_lists.append(set(self.neighbor_list))

    def tick(self):
        """
        Ticks off a second of time in the operation loop. If the loop time has
        run out then handle the packets received during this loop.
        """
        if(self.tdat.curr_op_loop_time >= self.tdat.op_loop_len):
            self.tdat.curr_op_loop_time = 0
            self.tdat.curr_op_cycle += 1
            self.handle_pkts()

        self.pkt_rcvd = False
        self.pkt_term = False
        self.tdat.curr_op_loop_time += 1