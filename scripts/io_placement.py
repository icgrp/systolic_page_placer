from loc import *
####################################################################################
def get_io_placement(placement_file):
    
    # blk_name -> BLK_Loc
    io_placement = {}

    with open(placement_file,"r") as f:
        for line in f:
            blk_name, x, y, subblk, layer, blk_id = line.split()
            io_placement[blk_name] = BLK_Loc(int(x), int(y))

    return io_placement
####################################################################################