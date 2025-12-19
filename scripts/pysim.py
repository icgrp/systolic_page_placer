import log
import math
import netlist as nl
import argparse
import grid_info as gi
import placer_init as pi
import io_placement as io
from loc import *
from matplotlib import pyplot as plt
################################################################################################################
class LFSR:
    def __init__(self,seed):
        self.r = [int(x) for x in '{0:016b}'.format(seed)]

    def get_num(self):
        s = ""
        for x in self.r:
            s = s + str(x)
        return int(s,2)

    def gen_num(self):
        feedback = self.r[16-16]^self.r[16-15]^self.r[16-13]^self.r[16-4]
        self.r = self.r[1:]+[feedback]
################################################################################################################
class PE:
    def __init__(self,blk_loc,blk_id=0,seed=0):

        self.blk_loc = blk_loc
        self.blk_id = blk_id
        self.blk_name = ""
        self.seed = seed
        self.lfsr = LFSR(seed)

        self.conn_names = set()
        self.conn_blk_locs = {}     # blk_name -> BLK_Loc
        self.conn_weights = {}      # blk_name -> weight

        self.accepted = 0
        self.rejected = 0

    def __str__(self):
        s = "blk_loc: {}\t\tblk_id: {}\t\tseed: {}".format(self.blk_loc,self.blk_id,self.seed)
        # for conn in self.conn_names:
        #     if conn in self.conn_blk_locs:
        #         loc = str(self.conn_blk_locs[conn])
        #     else:
        #         loc = "None"
        #     s += ("\n" + conn + " " + str(self.conn_weights[conn]) + " " + loc) 

        return s

    def cost_at(self,blk_loc):
        cost = 0

        for conn_name in self.conn_blk_locs.keys():
            conn_blk_loc = self.conn_blk_locs[conn_name]
            conn_weight = self.conn_weights[conn_name]
            #conn_weight = 1
            #conn_weight = math.pow(2,math.ceil(math.log2(conn_weight)))
            #conn_weight = min(math.pow(2,math.ceil(math.log2(conn_weight))), 32)
            #conn_weight = math.pow(conn_weight,2)

            #cost += conn_weight*(abs(blk_loc.x - conn_blk_loc.x)) + conn_weight*(abs(blk_loc.y - conn_blk_loc.y))
            cost += (conn_weight*((blk_loc.x - conn_blk_loc.x)**2)) + (conn_weight*((blk_loc.y - conn_blk_loc.y)**2))

        return cost

    def sum(self):
        px, py = 0, 0

        for conn_name in self.conn_names:
            px += (self.conn_blk_locs[conn_name].x * self.conn_weights[conn_name])
            py += (self.conn_blk_locs[conn_name].y * self.conn_weights[conn_name])

        return (px, py)

    @classmethod
    def swap(cls, pe_0, pe_1, temp):

        # pe_0 is the master pe

        initial_cost = (pe_0.cost_at(pe_0.blk_loc) + pe_1.cost_at(pe_1.blk_loc))
        final_cost = (pe_0.cost_at(pe_1.blk_loc) + pe_1.cost_at(pe_0.blk_loc))
        cost_delta = final_cost - initial_cost

        pe_0_rand = pe_0.lfsr.get_num()
        if(cost_delta < 0 or pe_0_rand < temp):
            pe_0.accepted += 1
            pe_1.accepted += 1

            # swap things
            pe_0.blk_name, pe_1.blk_name = pe_1.blk_name, pe_0.blk_name
            pe_0.blk_id, pe_1.blk_id = pe_1.blk_id, pe_0.blk_id

            pe_0.conn_names, pe_1.conn_names = pe_1.conn_names, pe_0.conn_names
            pe_0.conn_blk_locs, pe_1.conn_blk_locs = pe_1.conn_blk_locs, pe_0.conn_blk_locs
            pe_0.conn_weights, pe_1.conn_weights = pe_1.conn_weights, pe_0.conn_weights

            pe_0.accepted, pe_1.accepted = pe_1.accepted, pe_0.accepted
            pe_0.rejected, pe_1.rejected = pe_1.rejected, pe_0.rejected

        else:
            pe_0.rejected += 1
            pe_1.rejected += 1
################################################################################################################
class Placer:
    def __init__(self,grid_info,placer_init):
        self.temp = None
        self.phase = 0
        self.io_placement = {} # blk_name -> BLK_Loc

        self.acceptance_ratio_history = []

        log.blue("[Loading systolic_grid_info]")
        self.grid_info = gi.Grid_info(grid_info)
        self.pe = {} # pe_ty -> pe_loc -> pe
        for ty in self.grid_info.grid_types:
            log.blue("[{} width {}]".format(ty,self.grid_info.grid[ty].width))
            log.blue("[{} height {}]".format(ty,self.grid_info.grid[ty].height))
            self.pe[ty] = {}

        log.blue("[Loading placer_init]")
        self.placer_init = pi.Placer_init(placer_init,self.grid_info)
        ########################################################################################################
        log.blue("[Creating pysim placer]")

        for ty in self.grid_info.grid_types:
            for cx in range(self.grid_info.grid[ty].width):
                for cy in range(self.grid_info.grid[ty].height):

                    pe_loc = PE_Loc(cx,cy)
                    blk_loc = self.grid_info.grid[ty].pe_loc_to_blk_loc[pe_loc]
                    blk_id = self.placer_init.ty_loc_to_id[ty][pe_loc]
                    seed = self.placer_init.ty_loc_to_seed[ty][pe_loc]
                    self.pe[ty][pe_loc] = PE(blk_loc,blk_id,seed)
    ############################################################################################################
    def load(self,netlist,io_placement):

        # check that the netlist doesn't contain blocks that aren't supported by one of the placer's grids
        unsupported_blk_typs = netlist.netlist_types - (self.grid_info.grid_types | {"io"})
        if unsupported_blk_typs:
            for ty in unsupported_blk_typs:
                log.red("Block(s) of type {} found in netlist, but not supported by placer arch".format(ty))
            return

        placeable_types = netlist.netlist_types - {"io"}
        for ty in placeable_types:
            for cx in range(self.grid_info.grid[ty].width):
                for cy in range(self.grid_info.grid[ty].height):
                    pe_loc = PE_Loc(cx,cy)
                    blk_id = self.pe[ty][pe_loc].blk_id

                    # if the netlist has a blk_name for this ty_blk_id, add it to this PE
                    if blk_id in netlist.systolic_type_id_to_name[ty]:
                        blk_name = netlist.systolic_type_id_to_name[ty][blk_id]
                        self.pe[ty][pe_loc].blk_name = blk_name
                        self.pe[ty][pe_loc].conn_names = netlist.name_to_block[blk_name].connections
                        self.pe[ty][pe_loc].conn_weights = netlist.name_to_block[blk_name].weights

        self.io_placement = io_placement
    ############################################################################################################
    def swap(self):

        def phase_0():
            for ty in self.grid_info.grid_types:
                for cy in range(self.grid_info.grid[ty].height):
                    for cx in range(0,self.grid_info.grid[ty].width,2):
                        if cx == (self.grid_info.grid[ty].width - 1):
                            continue
                        master_pe = self.pe[ty][PE_Loc(cx,cy)]
                        slave_pe = self.pe[ty][PE_Loc(cx+1,cy)]
                        PE.swap(master_pe,slave_pe,self.temp)

        def phase_1():
            for ty in self.grid_info.grid_types:
                for cx in range(self.grid_info.grid[ty].width):
                    for cy in range(1,self.grid_info.grid[ty].height,2):
                        if cy == (self.grid_info.grid[ty].height - 1):
                            continue
                        master_pe = self.pe[ty][PE_Loc(cx,cy)]
                        slave_pe = self.pe[ty][PE_Loc(cx,cy+1)]
                        PE.swap(master_pe,slave_pe,self.temp)

        def phase_2():
            for ty in self.grid_info.grid_types:
                for cy in range(self.grid_info.grid[ty].height):
                    for cx in range(1,self.grid_info.grid[ty].width,2):
                        if cx == (self.grid_info.grid[ty].width - 1):
                            continue
                        master_pe = self.pe[ty][PE_Loc(cx,cy)]
                        slave_pe = self.pe[ty][PE_Loc(cx+1,cy)]
                        PE.swap(master_pe,slave_pe,self.temp)

        def phase_3():
            for ty in self.grid_info.grid_types:
                for cx in range(self.grid_info.grid[ty].width):
                    for cy in range(0,self.grid_info.grid[ty].height,2):
                        if cy == (self.grid_info.grid[ty].height - 1):
                            continue
                        master_pe = self.pe[ty][PE_Loc(cx,cy)]
                        slave_pe = self.pe[ty][PE_Loc(cx,cy+1)]
                        PE.swap(master_pe,slave_pe,self.temp)

        phases = [phase_0, phase_1, phase_2, phase_3]

        phases[self.phase]()
        self.phase = (self.phase + 1) % 4

        for ty in self.grid_info.grid_types:
            for pe in self.pe[ty].values():
                pe.lfsr.gen_num()
    ############################################################################################################
    def update(self):
        blk_name_to_blk_loc = {}

        accepted = 0
        rejected = 0

        # update global blk_name_to_loc map
        for ty in self.grid_info.grid_types:
            for pe in self.pe[ty].values():
                if(pe.blk_name):
                    blk_name_to_blk_loc[pe.blk_name] = pe.blk_loc
                    accepted += pe.accepted
                    rejected += pe.rejected
                pe.accepted = 0
                pe.rejected = 0
        ################################################################################
        total = accepted+rejected
        if(total != 0):
            self.acceptance_ratio_history.append(accepted/total)

            # ratio = self.acceptance_ratio_history[-1]
            # if ratio > 0.96:
            #     self.temp = int(self.temp*0.5)
            # elif (ratio > 0.8) and (ratio <= 0.96):
            #     self.temp = int(self.temp*0.5)
            # elif (ratio > 0.15) and (ratio <= 0.8):
            #     self.temp = int(self.temp*0.95)
            # elif (ratio <= 0.15):
            #     self.temp = int(self.temp*0.8)


        else:
            self.acceptance_ratio_history.append(0)
        ################################################################################
        # update local pe connection maps
        for ty in self.grid_info.grid_types:
            for pe in self.pe[ty].values():
                for blk_name in pe.conn_names:
                    if blk_name in blk_name_to_blk_loc.keys():
                        pe.conn_blk_locs[blk_name] = blk_name_to_blk_loc[blk_name]
                    elif blk_name in self.io_placement.keys():
                        pe.conn_blk_locs[blk_name] = self.io_placement[blk_name]
    ############################################################################################################
    def place(self,num_of_updates,swaps_per_update,initial_temp,trace_file):
        self.temp = initial_temp

        # note num_of_steps is the number of times we *need* to decrement the temp,
        # and is *not* the total number of swaps, but one less.
        num_of_steps = (num_of_updates*swaps_per_update) - 1
        temp_dec_step = math.floor(self.temp/num_of_steps)
        threshold = self.temp - (temp_dec_step*(num_of_steps-1))

        self.write_trace(trace_file,None,header=True)

        update_counter = 0
        for u in range(num_of_updates):
            self.update()
            self.write_trace(trace_file,"post_sum")
            update_counter += 1
            for s in range(swaps_per_update):
                self.swap()
                if(self.temp > threshold):
                    self.temp = self.temp - temp_dec_step
                else:
                    self.temp = 0
            self.write_trace(trace_file,"post_swap")
            log.magenta("  [Update {} completed]".format(update_counter))
    ############################################################################################################
    def write_trace(self,trace_file,state,header=False):
        if header:
            with open(trace_file,"w") as f:
                f.write("state,pe_type,pe_x,pe_y,blk_id,blk_x,blk_y,px,py,temp_blk_id,temp_x,temp_y,temperature\n")
        else:
            with open(trace_file,"a") as f:

                for ty in self.grid_info.grid_types:
                    for pe_x in range(self.grid_info.grid[ty].width):
                        for pe_y in range(self.grid_info.grid[ty].height):
                            pe = self.pe[ty][PE_Loc(pe_x,pe_y)]
                            px, py = pe.sum()
                            f.write("{},{},{},{},{},{},{},{},{},0,0,0,{}\n".format(state,ty,pe_x,pe_y,pe.blk_id,pe.blk_loc.x,pe.blk_loc.y,px,py,self.temp))
                f.write("null,null,0,0,0,0,0,0,0,0,0,0,0\n")
################################################################################################################
def main():
    description = 'Behavioral simulation of systolic placer'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("grid_info",help="grid_info file")
    p.add_argument("netlist",help="Netlist file")
    p.add_argument("io_placement",help="IO placement file to load")
    p.add_argument("placer_init",help="placer_init file")
    p.add_argument("output_dir",help="The output directory")
    p.add_argument("--swps", help="swaps per update. Default 1.",default=1)
    p.add_argument("--updts", help="num of updates. Default 2.",default=2)
    p.add_argument("--temp", help="Initial temperature. Default 0 (greedy).",default=0)
    args = p.parse_args()

    output_dir = args.output_dir if args.output_dir[-1] == "/" else (args.output_dir + "/")

    arry = Placer(args.grid_info,args.placer_init)

    log.blue("[Loading netlist]")
    netlist = nl.Netlist(args.netlist)
    io_placement = io.get_io_placement(args.io_placement)

    log.blue("[Mapping netlist]")
    arry.load(netlist,io_placement)
    
    log.blue("[Running placement]")
    log.blue("[Swaps per Update: {}]".format(int(args.swps)))
    log.blue("[Number of Updates: {}]".format(int(args.updts)))
    arry.place(int(args.updts),int(args.swps),int(args.temp),output_dir+"behavioral_trace.csv")
    log.blue("[Completed placement]")

    log.blue("[Writing acceptance ratio history]")
    with open(output_dir+"acceptance_ratio_history.txt","w") as f:
        for ratio in arry.acceptance_ratio_history:
            f.write(str(ratio) + "\n")

    plt.figure()
    plt.plot(range(1,len(arry.acceptance_ratio_history) + 1),arry.acceptance_ratio_history,marker=".")
    plt.title("Acceptance Ratio vs Number of Updates")
    plt.xlabel("Number of Updates")
    plt.ylabel("Acceptance Ratio")
    plt.ylim(ymin=0,ymax=1)
    plt.savefig(output_dir+"acceptance_ratio_history.png",dpi=300)
################################################################################################################
if __name__ == "__main__":
    main()