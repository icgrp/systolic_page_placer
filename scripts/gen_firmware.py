from collections import Counter
from shell import *
import argparse
import string
import textwrap
import grid_info as gi
import arch_info as ai
import placer_params as pp
import loc
import math
import log

# Main
################################################################################################
def main():

    description = 'Generates firmware header file'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("placer_params",help="Placer parameters file to load")
    p.add_argument("header_file",help="Header file to write")
    args = p.parse_args()

    ################################################################################
    # Load the placer and sub_placer parameters
    log.blue("[Reading parameters]")
    placer_params, sub_placer_params_dict = pp.read_params_from_file(args.placer_params)

    ################################################################################
    log.blue("[Writing firmware header file]")
    with open(args.header_file,"w") as f:
        f.write("#define N {}".format(placer_params.N))

################################################################################################
if __name__ == "__main__":
    main()