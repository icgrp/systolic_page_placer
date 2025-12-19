import argparse
import netlist as nl
from matplotlib import pyplot as plt
import log
############################################################################################################################
def plot(netlist, output_dir):
    netlist = nl.Netlist(netlist)
    blk_counts, unique_connections, weights = netlist.stats()

    log.blue("[Writing netlist block counts to file]")
    with open(output_dir+"block_counts.txt","w") as f:
        for ty in netlist.netlist_types:
            f.write("{:<10}{}\n".format(ty,blk_counts[ty]))

    log.blue("[Generating netlist histograms]")
    for ty in netlist.netlist_types:
        max_weight = max(weights[ty])
        plt.figure(plt.gcf().number + 1)
        plt.hist(weights[ty],range=(0,max_weight + 1), bins=20, align="left", fc='MediumOrchid', ec='black')
        #plt.yscale('log', nonpositive='clip')
        plt.title("Distribution of {} Weights".format(ty.upper()))
        plt.xlabel("Weights")
        plt.ylabel("Frequency")
        plt.savefig(output_dir+"{}_weight_hist.png".format(ty),dpi=300)

        max_unique_connections = max(unique_connections[ty])
        plt.figure(plt.gcf().number + 1)
        plt.hist(unique_connections[ty], bins=20, range=(0,max_unique_connections + 1), align="left", ec='black')       
        #plt.yscale('log', nonpositive='clip')
        plt.title("Distribution of {} Unique Connections".format(ty.upper()))
        plt.xlabel("Unique Connections")
        plt.ylabel("Frequency")
        plt.savefig(output_dir+"{}_unique_connections_hist.png".format(ty),dpi=300)
############################################################################################################################
def main():

    description = 'Plots netlist histograms'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("netlist", help="systolic netlist info file")
    p.add_argument("output_dir",help="output directory")
    args = p.parse_args()

    output_dir = args.output_dir
    output_dir = output_dir if output_dir[-1] == "/" else (output_dir + "/")

    plot(args.netlist, output_dir)
############################################################################################################################
if __name__ == "__main__":
    main()
    