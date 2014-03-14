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

    DEFAULT_max_op_loop_length = 100
    DEFAULT_max_start_offset = 100
    DEFAULt_max_msg_process_time = 100

    def __init__(self, G, randomize_timings = True, op_loop_len = None, start_offset = None, msg_process_time = None):
        """
        Simulator constructor
        """
        self.G = copy.deepcopy(G)
        self.num_agents = self.G.number_of_nodes()
        
        # Set up the initial timing data
        self.randomize_timings = randomize_timings
        if randomize_timings:
            # Randomize timing data if requested
            randomize_timing_data()
        else:
            set_timing_data(op_loop_len, start_offset, msg_process_time)

        # Create agent with these parameters
        self.agents = {G.nodes()[i]: create_agent(G.nodes()[i], self.agent_timing_data[i]) for i in range(self.num_agents)}

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
        op_loop_length = [int(random.random() * self.DEFAULT_max_op_loop_length) for i in range(self.num_agents)]
        start_offset = [int(random.random() * self.DEFAULT_max_start_offset) for i in range(self.num_agents)]
        msg_process_time = [int(random.random() * self.DEFAULT_msg_process_time) for i in range(self.num_agents)]

        self.agent_timing_data = [DPRTimingData(op_loop_len[i], start_offset[i], msg_process_time[i]) for i in range(self.num_agents)]

    def set_timing_data(self, op_loop_length, start_offset, msg_process_time):
        """
        Sets initial timing information for agents.
        If user does not provide this information then defaults are used
        """
         # Operation loop length for agents
        if op_loop_len is None:
            op_loop_len = [self.DEFAULT_op_loop_len] * self.num_agents

        if type(op_loop_len) is not list:
            op_loop_len = [op_loop_len] * self.num_agents

        # Start offset for agents
        if start_offset is None:
            start_offset = [self.DEFAULT_start_offset] * self.num_agents

        if type(start_offset) is not list:
            start_offset = [start_offset] * self.num_agents

        # Message processing time
        if msg_process_time is None:
            msg_process_time = [self.DEFAULT_msg_process_time] * self.num_agents

        if type(msg_process_time) is not list:
            msg_process_time = [msg_process_time] * self.num_agents
        self.agent_timing_data = [DPRTimingData(op_loop_len[i], start_offset[i], msg_process_time[i]) for i in range(self.num_agents)]

