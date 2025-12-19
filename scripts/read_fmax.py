import argparse
####################################################################################
def main():
    description = 'reads fmax from routing log output'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("routing_log",help="Routing log file to load")
    args = p.parse_args()

    metric = "-1"
    units = "-1"
    with open(args.routing_log,"r") as f:
        for line in f:
            if line.startswith("Final critical path delay (least slack):"):
                line_list = line.split()
                metric = line_list[9]
                units = line_list[10]
                print("{} {}".format(metric,units))
                return
        print("{} {}".format(metric,units))
####################################################################################
if __name__ == "__main__":
    main()