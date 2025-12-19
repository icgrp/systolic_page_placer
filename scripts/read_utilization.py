import argparse
####################################################################################
def main():
    description = 'reads utilization data from VTR log output'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("vtr_log",help="VTR log file to load")
    args = p.parse_args()

    ty = ""
    netlist_count = 0
    arch_count = 0

    capture = False
    netlist_mode = True
    with open(args.vtr_log,"r") as f:
        for line in f:
            if(capture == False):
                if(line.startswith("Resource usage...")):
                    capture = True
            else:
                if(line == "\n"):
                    capture = False
                    return
                elif(len(line.split()) != 1):
                    if netlist_mode == True:
                        ty = line.split()[-1]
                        netlist_count = int(line.split()[0])
                        netlist_mode = False
                    else:
                        arch_count = int(line.split()[0])
                        print("Type: {:<10} Netlist: {:<5} Arch: {:<5} Utilization: {}".format(ty,netlist_count,arch_count,netlist_count/arch_count*100))
                        netlist_mode = True
                        
####################################################################################
if __name__ == "__main__":
    main()