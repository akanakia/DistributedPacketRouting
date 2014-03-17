class DPRTimingData:
    # Define some variables
    def __init__(self, op_loop_len, start_offset, msg_process_time):
        self.op_loop_len      = op_loop_len
        self.start_offset     = start_offset
        self.msg_process_time = msg_process_time
        
        self.curr_op_loop_time    = start_offset % op_loop_len
        self.curr_op_cycle        = int(start_offset / op_loop_len)
        self.processing_time_left = 0