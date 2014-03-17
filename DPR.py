from DPRSim import DPRSim
import DPRTimingData as TD
import networkx as nx

def start(G):
    
    sim = DPRSim(G, randomize_timings = False)
