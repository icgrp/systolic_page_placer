import log
########################################################################################
class Entry:

    def __init__(self,state_ty,pe_ty,pe_x,pe_y,blk_id,blk_x,blk_y,px,py,temp_blk_id,temp_x,temp_y,temperature):
        self.state_ty = state_ty
        self.pe_ty = pe_ty
        self.pe_x = pe_x
        self.pe_y = pe_y
        self.blk_x = blk_x
        self.blk_y = blk_y
        self.blk_id = blk_id
        self.px = px
        self.py = py
        self.temp_blk_id = temp_blk_id
        self.temp_x = temp_x
        self.temp_y = temp_y
        self.temperature = temperature
########################################################################################
def get_state_list(trace_file_name):
    state_list = []
    with open(trace_file_name,"r") as f:
        
        working_state_ty = None
        state = []

        for i,line in enumerate(f):

            # skip the first header line
            if(i == 0):
                continue

            # check that line is in right format
            val_list = line.strip().split(",")
            if(len(val_list) != 13):
                log.red("Error: Malformed line! Expected 13 values, got: {}".format(len(val_list)))
                return
            if val_list[0] not in {"post_sort", "post_swap", "post_sum", "null"}:
                log.red("Error: Malformed line! Unknown state type: {}".format(val_list[0]))
                return
            if not all([x.isdigit() for x in val_list[2:]]):
                log.red("Error: Malformed line! Non-digit found where digit expected.")
                return
            
            # parse line to create an Entry object
            state_ty = val_list[0]
            pe_ty = val_list[1]

            entry = Entry(state_ty,pe_ty,*list(map(int,val_list[2:])))

            # set the initial working state
            if(i == 1):
                working_state_ty = state_ty

            # keep collecting entries belonging to the same state.
            # when done, push the state to the state list
            # and start collecting entries for the next state.
            if state_ty == working_state_ty:
                state.append(entry)
            else:
                state_list.append(state)
                working_state_ty = state_ty
                state = [entry]

        state_list.append(state)
    return state_list
########################################################################################