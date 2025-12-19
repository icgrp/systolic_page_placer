import argparse
####################################################################################
def main():
    description = 'reads min channel width from routing log output after binary search was used'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("routing_log",help="Routing log file to load")
    args = p.parse_args()

    metric = "-1"
    with open(args.routing_log,"r") as f:
        for line in f:
            if line.startswith("Best routing used a channel width factor of"):
                line_list = line.split()
                metric = line_list[8]
                metric = metric[:-1]
                print("{}".format(metric))
                return
        print("{}".format(metric))
####################################################################################
if __name__ == "__main__":
    main()