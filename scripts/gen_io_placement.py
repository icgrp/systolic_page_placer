import argparse
import log
####################################################################################
def main():
    description = 'generates io placement file from complete placement file and a netlist file'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("place_file",help="Placement file to load")
    p.add_argument("netlist_file",help="Netlist file to load")
    p.add_argument("output_file",help="Output file for IO placement")
    args = p.parse_args()

    ###############################################################################
    io_blk_names = set()
    with open(args.netlist_file,"r") as f:
        f.readline()
        f.readline()
        for line in f:
            line = line.split(",")
            blk_name, blk_type, blk_id = line[0].split(" ")
            if(blk_type == "io"):
                io_blk_names.add(blk_name)
    ###############################################################################
    io_placement_lst = []
    with open(args.place_file,"r") as f:
        for i in range(5):
            f.readline()
        for line in f:
            blk_name, x, y, subblk, layer, blk_id = line.split()
            if(blk_name in io_blk_names):
                io_placement_lst.append("{blk_name: <50}{x: <8}{y: <8}{subblk: <8}{layer: <8}{blk_id: <8}\n".format(blk_name=blk_name,x=x,y=y,subblk=subblk,layer=layer,blk_id=blk_id))
    ###############################################################################
    if(len(io_blk_names) != len(io_placement_lst)):
        log.red("[Error: Not all io blks found in the netlist are in the given placement file!]")
        print(io_blk_names)
        print(io_placement_lst)
        return
    ###############################################################################
    with open(args.output_file,"w") as f:
        for p in io_placement_lst:
            f.write(p)
    log.blue("[Generated io placement file]")
####################################################################################
if __name__ == "__main__":
    main()