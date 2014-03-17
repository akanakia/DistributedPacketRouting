from DPRAgent import DPRAgent
from DPRPacket import DPRPacket
from DPRTimingData import DPRTimingData
import networkx as nx
import copy
import random

class DPRSim:

    DEFAULT_op_loop_len = 50
    DEFAULT_start_offset = 0
    DEFAULT_msg_process_time = 1
    DEFAULT_msg_transfer_time = 1

    DEFAULT_max_op_loop_length = 100
    DEFAULT_max_start_offset = 100
    DEFAULT_max_msg_process_time = 100
    DEFAULT_max_msg_transfer_time = 10

    def __init__(self, G, randomize_timings = True, op_loop_len = None, start_offset = None, msg_process_time = None , msg_transfer_time = None):
        """
        Simulator constructor
        """
        self.G = copy.deepcopy(G)
        self.num_agents = self.G.number_of_nodes()
        
        # Set up the initial timing data
        self.randomize_timings = randomize_timings
        if randomize_timings:
            # Randomize timing data if requested
            self.randomize_timing_data()
        else:
            self.set_timing_data(op_loop_len, start_offset, msg_process_time, msg_transfer_time)

        # Create agent with these parameters
        self.agents = {G.nodes()[i]: self.create_agent(G.nodes()[i], self.agent_timing_data[i]) for i in range(self.num_agents)}

        # Print init info
        self.print_init_info()

    def print_init_info(self):
        """
        Prints the initialization state of the simulator
        """
        print "================================================================"
        print "Simulation Initilization Information\n"
        print "NUMBER OF AGENTS = %d"%self.num_agents
        print "TIME SINCE START = %d"%self.start_time
        for agent in self.agents.itervalues():
            print "\nAGENT [%s] (Started at %d):"%(str(agent.my_id), self.start_time - agent.tdat.start_offset)
            print "\tOperation Loop Length       = %d"%agent.tdat.op_loop_len
            print "\tMessage Processing Time     = %d"%agent.tdat.msg_process_time
            print "\tCurrent Operation Loop Time = %d"%agent.tdat.curr_op_loop_time
            print "\tCurrent Operation Cycle     = %d"%agent.tdat.curr_op_cycle
        print "================================================================"

    def create_agent(self, new_agent_id, new_agent_timing_data):
        """
        Creates a new agents with the given timing data and id
        """
        new_agent = DPRAgent(new_agent_id, self.G, new_agent_timing_data)
        return new_agent

    def randomize_timing_data(self):
        """
        Randomizes all the timing information for agents
        """
        self.op_loop_len = [int(random.random() * self.DEFAULT_max_op_loop_length) for i in range(self.num_agents)]
        self.start_offset = [int(random.random() * self.DEFAULT_max_start_offset) for i in range(self.num_agents)]
        self.msg_process_time = [int(random.random() * self.DEFAULT_max_msg_process_time) for i in range(self.num_agents)]
        self.msg_transfer_time = [int(random.random() * self.DEFAULT_max_msg_transfer_time) for i in range(self.num_agents)]

        self.agent_timing_data = [DPRTimingData(self.op_loop_len[i], self.start_offset[i], self.msg_process_time[i]) for i in range(self.num_agents)]
        self.start_time = max(self.start_offset)

    def set_timing_data(self, op_loop_len, start_offset, msg_process_time, msg_transfer_time):
        """
        Sets initial timing information for agents.
        If user does not provide this information then defaults are used
        """
         # Operation loop length for agents
        if op_loop_len is None:
            self.op_loop_len = [self.DEFAULT_op_loop_len] * self.num_agents
        elif type(op_loop_len) is not list:
            self.op_loop_len = [op_loop_len] * self.num_agents

        # Start offset for agents
        if start_offset is None:
            self.start_offset = [self.DEFAULT_start_offset] * self.num_agents
        elif type(start_offset) is not list:
            self.start_offset = [start_offset] * self.num_agents

        # Message processing time
        if msg_process_time is None:
            self.msg_process_time = [self.DEFAULT_msg_process_time] * self.num_agents
        elif type(msg_process_time) is not list:
            self.msg_process_time = [msg_process_time] * self.num_agents
           
        # Message transfer time between agents
        if msg_transfer_time is None:
            self.msg_transfer_time = [self.DEFAULT_msg_transfer_time] * self.num_agents
        elif type(msg_transfer_time) is not list:
            self.msg_transfer_time = [msg_transfer_time] * self.num_agents

        # DEBUG
        #print self.op_loop_len
        #print self.start_offset
        #print self.msg_process_time
        #print self.msg_transfer_time

        self.agent_timing_data = [DPRTimingData(self.op_loop_len[i], self.start_offset[i], self.msg_process_time[i]) for i in range(self.num_agents)]
        self.start_time = max(self.start_offset)

    def move_packets(self):
        """
        Transfers packets from all agent output buffers to forward agent input buffers
        Also adds appropriate meta-data for every transferred packet such as,
        the id of the receiving agent in the propogation chain and the time of 
        arrival at the receiving agent. 
        """
        for agent in self.agents.itervalues():
            for i in range(len(agent.out_buf)):
                for fw_id in agent.fw_id_lists[i]:
                    transfer_pkt = copy.deepcopy(agent.out_buf[i])
                    transfer_pkt.recv_local_timestamps.append(self.agents[fw_id].tdat.curr_op_loop_time)
                    transfer_pkt.recv_global_timestamps.append(self.curr_time)
                    transfer_pkt.prop_chain_ids.append(fw_id)
                    self.agents[fw_id].in_buf.append(transfer_pkt)

            # Clear the output and forwarding buffers 
            # after all messages have been sent
            agent.out_buf = []
            agent.fw_id_lists = []

    def run(self, stop_conds, log_lvl = 1):
        """
        Runs the simulation till a stopping condition is met
        PARAMETERS: 
        stop_conds - A dictionary of stopping conditions. Possible key-value pairs, 
            iter:n    - The number of iterations to run the simulation for
            rcvd:True - Run till any target agent receives a packet. 
                        Note that rcvd:False does nothing.
        log_lvl    - A logging level to decide what data to output to file
            Level    Agents    In Buffer    Out buffer    Imp Times    Pkt Info
              1        Y          Y             Y            Y           Y
              2        Y          Y             Y            Y           N
              3        Y          N             N            Y           N
        """
        self.curr_time = self.start_time
        while(True):
            self.curr_time += 1
            for agent in self.agents.itervalues():
                agent.tick()

            self.move_packets()

            # Check stopping conditions here
            stop = False
            for cond in stop_conds:
                # Number of iterations
                if cond == 'iter':
                    if self.curr_time > (stop_conds['iter'] + self.start_time):
                        stop = True
                        break

                # Packet reveived by any target agent
                if cond == 'rcvd':
                    rcvd = False
                    if stop_conds['rcvd']:
                        for agent in self.agents.itervalues():
                            if agent.pkt_rcvd:
                                rcvd = True
                                break
                        if rcvd:
                            stop = True
                            break
            if stop:
                break