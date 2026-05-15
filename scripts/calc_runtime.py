import argparse
import placer_params as pp
import numpy as np

################################################################################################
def compute_runtime(placer_params,num_of_updates,swaps_per_update,frequency):

    FIXED_SUM_CYCLES = 1

    placer_params, sub_placer_params_dict = pp.read_params_from_file(placer_params)

    cycles_per_swap = 10
    cycles_per_sort = 4*placer_params.D*np.ceil(np.log2(placer_params.D)) + 2*placer_params.D
    cycles_per_sum = placer_params.SCD - FIXED_SUM_CYCLES + placer_params.WSRD + 2*placer_params.N



    runtime_cycles = (swaps_per_update*num_of_updates)*cycles_per_swap + num_of_updates*(cycles_per_sort + cycles_per_sum)
    runtime = runtime_cycles*(1/frequency)

    return runtime

# Main
################################################################################################
def main():

    description = 'Computes systolic runtime'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("placer_params",help="placer_params file")
    p.add_argument("num_of_updates",help="num_of_updates")
    p.add_argument("swaps_per_update",help="swaps_per_update")
    p.add_argument("frequency",help="frequency_of_placer")
    args = p.parse_args()

    print(compute_runtime(args.placer_params,
                          int(args.num_of_updates),
                          int(args.swaps_per_update),
                          int(args.frequency)))

################################################################################################
if __name__ == "__main__":
    main()

