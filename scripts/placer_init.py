import log
from loc import *
################################################################################################################
class Placer_init:
    # Reads in a placer_init file, and produces a Placer_init object 
    def __init__(self,filename,grid_info):

        self.ty_loc_to_id = {}
        self.ty_loc_to_seed = {}
        self.ty_id_to_loc = {}

        for ty in grid_info.grid_types:
            self.ty_loc_to_id[ty] = {}
            self.ty_loc_to_seed[ty] = {}
            self.ty_id_to_loc[ty] = {}

        with open(filename,"r") as f:
            header = f.readline()
            for line in f:
                line = line.split()

                ty = line[0]
                cx, cy, seed, id = list(map(int,line[1:]))

                if ty not in grid_info.grid_types:
                    log.red("[Error, unknown PE type: {}]".format(ty))
                else:
                    self.ty_loc_to_id[ty][PE_Loc(cx,cy)] = id
                    self.ty_loc_to_seed[ty][PE_Loc(cx,cy)] = seed
                    self.ty_id_to_loc[ty][id] = PE_Loc(cx,cy)
################################################################################################################