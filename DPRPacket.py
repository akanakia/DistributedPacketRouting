class DPRPacket:
    def __init__(self, source_agent_id, target_agent_id):
        self.sent_timestamps        = []
        self.recv_global_timestamps = []
        self.recv_local_timestamps  = [0]
        self.prop_chain_ids         = [source_agent_id]
        self.target_agent_id        = target_agent_id
