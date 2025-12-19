import argparse
####################################################################################
def main():
    description = 'reads wire cost time from pysim cost log output'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("cost_log",help="cost log file to load")
    args = p.parse_args()

    cost = 0
    with open(args.cost_log,"r") as f:
        for line in f:
            cost = int(float(line.strip()))
    print(cost)
####################################################################################
if __name__ == "__main__":
    main()