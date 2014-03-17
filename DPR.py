from DPRSim import DPRSim
from DPRTimingData import DPRTimingData

import networkx as nx
import matplotlib.pyplot

def start(G):
    
    sim = DPRSim(G, randomize_timings = False)
