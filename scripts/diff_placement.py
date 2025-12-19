import argparse
import log
####################################################################################
def read_placement(placement_file):
    placement = {}
    with open(placement_file,"r") as f:
    
        # go through the header 
        for line in range(5):
            f.readline()

        for line in f:
            blk_name, x, y, subblk, layer, blk_id = line.split()
            placement[blk_name] = (x, y, subblk, layer, blk_id)

    return placement
####################################################################################
def main():

    description = "Diffs two placement files"
    p = argparse.ArgumentParser(description = description)
    p.add_argument("placement_1",help="first placement file")
    p.add_argument("placement_2",help="second placement file")
    args = p.parse_args()

    log.blue("[Comparing {} to {}]".format(args.placement_1,args.placement_2))

    p1 = read_placement(args.placement_1)
    p2 = read_placement(args.placement_2)

    if(p1 != p2):
        log.red("[Error: placements differ]")
        print(len(p1))
        print(len(p2))
        for k in p1:
            if(p1[k] != p2[k]):
                print(p1[k])
                print(p2[k])
                print()
    else:
        log.green("[Placements are equivalent]")
####################################################################################
if __name__ == "__main__":
    main()