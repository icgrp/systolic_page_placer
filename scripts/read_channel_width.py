import argparse
####################################################################################
def main():
    description = 'reads channel width from routing log'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("routing_log",help="Routing log file to load")
    args = p.parse_args()

    with open(args.routing_log,"r") as f:
        for line in f:
            if line.startswith("Circuit successfully routed with a channel width factor of"):
                line_list = line.split()
                metric = line_list[-1]
                metric = metric[:-1]
                print("{}".format(metric))
                return
####################################################################################
if __name__ == "__main__":
    main()