import argparse
import trace
import log
########################################################################################
def main():

    description = "Diffs a rtl trace with a pysim trace"
    p = argparse.ArgumentParser(description = description)
    p.add_argument("rtl_trace",help="rtl trace file")
    p.add_argument("pysim_trace",help="pysim trace file")

    args = p.parse_args()

    rtl_sim_state_list = trace.get_state_list(args.rtl_trace)
    rtl_sim_state_list = [x for x in rtl_sim_state_list if x[0].state_ty == "post_swap"]

    py_sim_state_list = trace.get_state_list(args.pysim_trace)
    py_sim_state_list = [x for x in py_sim_state_list if x[0].state_ty == "post_swap"]


    if len(py_sim_state_list) != len(py_sim_state_list):
        log.red("[Error: trace lengths not equal!]")


    for i in range(len(rtl_sim_state_list)):

        rtl_pos_dict = {}
        for entry in rtl_sim_state_list[i]:
            rtl_pos_dict[(entry.pe_ty,entry.blk_id)] = (entry.pe_x,entry.pe_y,entry.temperature)

        py_pos_dict = {}
        for entry in py_sim_state_list[i]:
            py_pos_dict[(entry.pe_ty,entry.blk_id)] = (entry.pe_x,entry.pe_y,entry.temperature)

        if(rtl_pos_dict == py_pos_dict):
            log.green("[Passed: post_swap {} states equal]".format(i))
        else:
            log.red("[Error: Not Equal!]")
            set1 = set(rtl_pos_dict.items())
            set2 = set(py_pos_dict.items())
            diff = set1 ^ set2

            diff_keys = set([key[0] for key in diff])

            log.red("    (type, id) -> (pe_x, pe_y, temp)\n")
            for x in diff_keys:
                log.blue("    rtl_sim = {} -> {}".format(x,rtl_pos_dict[x]))
                log.magenta("    py_sim  = {} -> {}\n".format(x,py_pos_dict[x]))

            #return
########################################################################################
if __name__ == "__main__":
    main()