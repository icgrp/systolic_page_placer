import argparse
####################################################################################
def main():
    description = 'reads routing time from VTR log output'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("vtr_log",help="VTR log file to load")
    args = p.parse_args()

    with open(args.vtr_log,"r") as f:
        for line in f:
            if line.startswith("# Routing took"):
                line_list = line.split()
                metric = line_list[3]
                units = line_list[4]
                print("{} {}".format(metric,units))
                return
####################################################################################
if __name__ == "__main__":
    main()