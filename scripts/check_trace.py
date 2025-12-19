import netlist as nl
import io_placement as io
import log
import argparse
import math
from matplotlib import pyplot as plt 
import trace
import grid_info as gi
from loc import *
########################################################################################
def check_number_of_blocks(grid_info,netlist,io_placement,state):
    # make sure there are the right numbers of enteries in the state, given the grid
    measured_n = {}
    golden_n = {}
    for ty in grid_info.grid_types:
        measured_n[ty] = 0
        golden_n[ty] = grid_info.grid[ty].width * grid_info.grid[ty].height

    for entry in state:
        measured_n[entry.pe_ty] += 1

    for ty in grid_info.grid_types:
        if measured_n[ty] != golden_n[ty]:
            log.red("\tfailed: expected {} {} entries, but got {}".format(golden_n[ty],ty,measured_n[ty]))
            return 1
########################################################################################
def check_extra_blk_ids(grid_info,netlist,io_placement,state):
    golden_n = {}
    for ty in grid_info.grid_types:
        golden_n[ty] = grid_info.grid[ty].width * grid_info.grid[ty].height

    golden_blk_id_sets = {}
    for ty in grid_info.grid_types:
        golden_blk_id_sets[ty] = set()
        for i in range(golden_n[ty]):
            golden_blk_id_sets[ty].add(i)

    for entry in state:
        golden_blk_id_sets[entry.pe_ty].discard(entry.blk_id)

    for ty in grid_info.grid_types:
        if len(golden_blk_id_sets[ty]) > 0:
            log.red("\tfailed: bad {} block ids detected".format(ty))
            return 1
        
    return 0
########################################################################################
def check_missing_blk_ids(grid_info,netlist,io_placement,state):
    golden_n = {}
    for ty in grid_info.grid_types:
        golden_n[ty] = grid_info.grid[ty].width * grid_info.grid[ty].height

    golden_blk_id_sets = {}
    measured_blk_id_sets = {}
    for ty in grid_info.grid_types:
        golden_blk_id_sets[ty] = set()
        measured_blk_id_sets[ty] = set()
        for i in range(golden_n[ty]):
            golden_blk_id_sets[ty].add(i)

    for entry in state:
        measured_blk_id_sets[entry.pe_ty].add(entry.blk_id)

    for ty in grid_info.grid_types:
        if(len(golden_blk_id_sets[ty] - measured_blk_id_sets[ty]) > 0):
            log.red("\tfailed: missing blk ids detected")
            return 1
########################################################################################
def check_sorted_temp_blk_ids(grid_info,netlist,io_placement,state):
    for entry in state:

        ty = entry.pe_ty

        measured_pe_loc = PE_Loc(entry.pe_x,entry.pe_y)
        golden_pe_loc = grid_info.grid[ty].get_home_pe_coords(entry.temp_blk_id)

        if(measured_pe_loc != golden_pe_loc):
            log.red("\tfailed: In {} sub-array, temp_blk_id {} at ({}), but should be at ({})".format(ty,entry.temp_blk_id,measured_pe_loc,golden_pe_loc))
            return 1
        
    return 0
########################################################################################
def check_temp_loc_with_temp_blk_id(grid_info,netlist,io_placement,state):
    ty_to_blk_id_to_blk_loc = {}
    for entry in state:
        ty = entry.pe_ty
        if ty not in ty_to_blk_id_to_blk_loc:
            ty_to_blk_id_to_blk_loc[ty] = {}

        ty_to_blk_id_to_blk_loc[ty][entry.blk_id] = BLK_Loc(entry.blk_x,entry.blk_y)

    for entry in state:
        ty = entry.pe_ty
        measured_temp_blk_loc = BLK_Loc(entry.temp_x,entry.temp_y)
        golden_temp_blk_loc = ty_to_blk_id_to_blk_loc[ty][entry.temp_blk_id]
        if(measured_temp_blk_loc != golden_temp_blk_loc):
            log.red("\tfailed: The {} block at PE loc {} has a temp_blk_id of {}.".format(ty,PE_Loc(entry.pe_x,entry.pe_y),entry.temp_blk_id))
            log.red("\t\tThe expected (temp_x, temp_y) at this location was {}, but got {}.".format(golden_temp_blk_loc,measured_temp_blk_loc))
            return 1
########################################################################################
def check_sums(grid_info,netlist,io_placement,state):
    
    placement_dict = {} # build a mapping: blk_name -> BLK_Loc
    sum_dict = {}       # build a mapping: blk_name -> (px, py)

    for entry in state:
        if entry.pe_ty not in netlist.netlist_types:
            continue
        elif entry.blk_id in netlist.systolic_type_id_to_name[entry.pe_ty]:
            entry_name = netlist.systolic_type_id_to_name[entry.pe_ty][entry.blk_id]
            placement_dict[entry_name] = BLK_Loc(entry.blk_x,entry.blk_y)
            sum_dict[entry_name] = (entry.px, entry.py)

    placement_dict = placement_dict | io_placement

    # Note: this only checks the blocks *in* the netlist, and doesn't check that empty blocks have (px,py) == (0,0)
    # but we really should check this too, because it might actually impact swapping
    for block in netlist.name_to_block.values():
        calc_px = 0
        calc_py = 0

        clb_px = 0
        clb_py = 0
        memory_px = 0
        memory_py = 0
        mult_36_px = 0
        mult_36_py = 0
        io_px = 0
        io_py = 0
        
        for connection_name in block.connections:
            calc_px += block.weights[connection_name]*(placement_dict[connection_name].x)
            calc_py += block.weights[connection_name]*(placement_dict[connection_name].y)
            if(netlist.name_to_block[connection_name].type == "clb"):
                clb_px += block.weights[connection_name]*(placement_dict[connection_name].x)
                clb_py += block.weights[connection_name]*(placement_dict[connection_name].y)
            elif(netlist.name_to_block[connection_name].type == "memory"):
                memory_px += block.weights[connection_name]*(placement_dict[connection_name].x)
                memory_py += block.weights[connection_name]*(placement_dict[connection_name].y)
            elif(netlist.name_to_block[connection_name].type == "mult_36"):
                mult_36_px += block.weights[connection_name]*(placement_dict[connection_name].x)
                mult_36_py += block.weights[connection_name]*(placement_dict[connection_name].y)
            elif(netlist.name_to_block[connection_name].type == "io"):
                io_px += block.weights[connection_name]*(placement_dict[connection_name].x)
                io_py += block.weights[connection_name]*(placement_dict[connection_name].y)
        
        # note, we don't have to check px and py for io blocks (or any other fixed blocks), since they aren't calculated/stored in the systolic placer
        if(block.type != "io" and (((sum_dict[block.name])[0],(sum_dict[block.name])[1]) != (calc_px,calc_py))):
            log.red("\tfailed: measured sums for block_id {} of type {} = ({},{})".format(block.id,block.type,(sum_dict[block.name])[0],(sum_dict[block.name])[1]))
            log.red("\t\tcalculated sums for block_id {} of type {} = ({},{})".format(block.id,block.type,calc_px,calc_py))
            log.yellow("clb {} {}".format(clb_px,clb_py))
            log.yellow("memory {} {}".format(memory_px,memory_py))
            log.yellow("mult_36 {} {}".format(mult_36_px,mult_36_py))
            log.yellow("io {} {}".format(io_px,io_py))
            return 1
        
    return 0
########################################################################################
def calc_cost(grid_info,netlist,io_placement,state):
    cost = 0
    two_way_cost = 0
    one_way_cost = 0
    ####################################################################################

    # create mapping: blk_name -> BLK_Loc
    placement_dict = {}
    for entry in state:
        if entry.pe_ty not in netlist.netlist_types:
            continue
        elif entry.blk_id in netlist.systolic_type_id_to_name[entry.pe_ty]:
            entry_name = netlist.systolic_type_id_to_name[entry.pe_ty][entry.blk_id]
            placement_dict[entry_name] = BLK_Loc(entry.blk_x,entry.blk_y)

    # add the io placement to this mapping. Note this only has: blk_name -> BLK_Loc
    placement_dict = placement_dict | io_placement
    ####################################################################################
    two_way_cost = 0
    for block in netlist.name_to_block.values():
        for connection_name in block.connections:
            two_way_cost += math.pow(((placement_dict[block.name].x - placement_dict[connection_name].x))*netlist.name_to_block[block.name].weights[connection_name],2)
            two_way_cost += math.pow(((placement_dict[block.name].y - placement_dict[connection_name].y))*netlist.name_to_block[block.name].weights[connection_name],2)
    cost = (two_way_cost/2)
    return cost
########################################################################################
def calc_stale(state, old_placement):

    # This really isn't great because it doesn't take into account the weights
    # of the different connections. It really depends on what we mean by "staleness"

    new_placement = {}  # (blk_ty, blk_id) -> BLK_Loc

    stale = 0
    for entry in state:
        if old_placement:
            stale_x = abs(old_placement[(entry.pe_ty, entry.blk_id)].x - entry.blk_x)
            stale_y = abs(old_placement[(entry.pe_ty, entry.blk_id)].y - entry.blk_y)
            stale += stale_x + stale_y

        new_placement[(entry.pe_ty, entry.blk_id)] = BLK_Loc(entry.blk_x, entry.blk_y)

    return (stale, new_placement)
########################################################################################
def post_swap_suite(grid_info,netlist,io_placement,state):
    
    tests = [check_number_of_blocks,
             check_extra_blk_ids,
             check_missing_blk_ids]

    # returns 1 if any of the tests fail, 0 otherwise
    return any([f(grid_info,netlist,io_placement,state) for f in tests])
########################################################################################
def post_sort_suite(grid_info,netlist,io_placement,state):

    tests = [check_number_of_blocks,
             check_extra_blk_ids,
             check_missing_blk_ids,
             check_sorted_temp_blk_ids,
             check_temp_loc_with_temp_blk_id]

    # returns 1 if any of the tests fail, 0 otherwise
    return any([f(grid_info,netlist,io_placement,state) for f in tests])
########################################################################################
def post_sum_suite(grid_info,netlist,io_placement,state):

    tests = [check_number_of_blocks,
             check_extra_blk_ids,
             check_missing_blk_ids,
             check_sums]

    # returns 1 if any of the tests fail, 0 otherwise
    return any([f(grid_info,netlist,io_placement,state) for f in tests])
########################################################################################
def check_state(grid_info,netlist,io_placement,state):

    test_suite_dict = {"post_sort" : post_sort_suite,
                       "post_swap" : post_swap_suite,
                       "post_sum" : post_sum_suite}

    state_ty = state[0].state_ty
    if state_ty == "null":
        return
    log.magenta("  [Running {:<6} tests]".format(state_ty),end="")
    if not (test_suite_dict[state_ty](grid_info,netlist,io_placement,state)):
        log.green("\tpassed")
########################################################################################
def write_placement(grid_info,netlist,state,filename):
    with open(filename,"w") as f:
        f.write("Netlist_File: {} Netlist_ID: {}\n".format(netlist.name,netlist.hash))
        f.write("Array size: {} x {} logic blocks\n".format(grid_info.total_width,grid_info.total_height)) # we add 2 to account for io perimeter 
        f.write("\n")
        f.write("{} {:<8}{:<8}{:<8}{:<8}{:<8}\n".format("#block name","x","y","subblk","layer","block number"))
        f.write("{} {:<8}{:<8}{:<8}{:<8}{:<8}\n".format("#----------","--","--","------","-----","------------"))
        for entry in state:
            if entry.pe_ty not in netlist.netlist_types:
                continue
            elif entry.blk_id in netlist.systolic_type_id_to_name[entry.pe_ty]:
                blk_name = netlist.systolic_type_id_to_name[entry.pe_ty][entry.blk_id]
                vtr_blk_id = netlist.name_to_vtr_blk_id[blk_name]
                f.write("{blk_name} {x: <8}{y: <8}{subblk: <8}{layer: <8}#{blk_id: <8}\n".format(x=entry.blk_x,y=entry.blk_y,subblk="0",layer="0", blk_name=blk_name, blk_id=vtr_blk_id))
########################################################################################
def main():

    description = 'Checks a trace file for runtime errors'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("grid_info",help="grid_info file")
    p.add_argument("netlist",help="Netlist file")
    p.add_argument("io_placement",help="IO placement file to load")
    p.add_argument("trace_file",help="The trace file")
    p.add_argument("output_dir",help="The output directory")
    p.add_argument("--acceptance_ratio_history", help="acceptance ratio history file")
    args = p.parse_args()

    output_dir = args.output_dir if args.output_dir[-1] == "/" else (args.output_dir + "/")
    ####################################################################################
    log.blue("[Reading systolic_grid_info]")
    grid_info = gi.Grid_info(args.grid_info)
    for ty in grid_info.grid_types:
        log.blue("[{} height {}]".format(ty,grid_info.grid[ty].width))
        log.blue("[{} width {}]".format(ty,grid_info.grid[ty].height))

    log.blue("[Loading netlist]")
    netlist = nl.Netlist(args.netlist)

    log.blue("[Loading io placement]")
    io_placement = io.get_io_placement(args.io_placement)

    log.blue("[Loading trace]")
    state_list = trace.get_state_list(args.trace_file)
    cost_history = []
    temperature_history = []
    stale_history = []
    ####################################################################################
    log.blue("[Checking trace]")

    old_placement = {}

    tpb = 0
    blk_counts, _, _ = netlist.stats()
    for ty in blk_counts:
        if(ty != "io"):
            tpb += blk_counts[ty]

    last_swap_state = None
    for i,state in enumerate(state_list):
        check_state(grid_info,netlist,io_placement,state)
        if(state[0].state_ty == "post_sum"):
            cost_history.append(calc_cost(grid_info,netlist,io_placement,state))
            temperature_history.append(state[0].temperature)

            stale, plcmnt = calc_stale(state,old_placement)
            old_placement = plcmnt
            stale_history.append(stale/tpb)
        if(state[0].state_ty == "post_swap"):
            last_swap_state = state

    scaled_temperature_history = [(x/65535.0)*100.0 for x in temperature_history]
    ####################################################################################
    log.blue("[Writing cost history]")
    with open(output_dir+"cost_history.txt","w") as f:
        for cost in cost_history:
            f.write(str(cost) + "\n")
    ####################################################################################
    log.blue("[Writing temperature history]")
    with open(output_dir+"temperature_history.txt","w") as f:
        for temperature in temperature_history:
            f.write(str(temperature) + "\n")
    ####################################################################################
    log.blue("[Writing initial placement file]")
    write_placement(grid_info,netlist,state_list[0],output_dir+"initial_systolic.place")
    
    log.blue("[Writing final placement file]")
    write_placement(grid_info,netlist,last_swap_state,output_dir+"final_systolic.place")
    ####################################################################################
    log.blue("[Plotting figures]")
    ####################################################################################
    # Cost convergence
    plt.figure(plt.gcf().number + 1)
    plt.plot(range(1,len(cost_history) + 1), cost_history,marker=".")
    plt.title("Squared Manhattan Wire Length vs Number of Updates")
    plt.xlabel("Number of Updates")
    plt.ylabel("Squared Manhattan Wire Length")
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.ylim(ymin=0)
    plt.savefig(output_dir+"cost_history.png",dpi=300)
    ####################################################################################
    # Temperature profile
    plt.figure(plt.gcf().number + 1)
    plt.plot(range(1,len(scaled_temperature_history) + 1), scaled_temperature_history,marker=".")
    plt.title("Annealing Temperature Profile")
    plt.xlabel("Number of Updates")
    plt.ylabel("Temperature (%)")
    plt.ylim(ymin=0,ymax=100)
    plt.savefig(output_dir+"temperature_history.png",dpi=300)
    ####################################################################################
    # Staleness
    plt.figure(plt.gcf().number + 1)
    plt.plot(range(1,len(stale_history) + 1), stale_history,marker=".")
    plt.title("Average Block Staleness Contribution vs Number of Updates")
    plt.xlabel("Number of Updates")
    plt.ylabel("Average Block Staleness Contribution")
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.ylim(ymin=0)
    plt.savefig(output_dir+"stale_history.png",dpi=300)
    ####################################################################################
    # ratio and temp
    if not args.acceptance_ratio_history:
        return
    acceptance_ratio_history = []
    with open(output_dir+"acceptance_ratio_history.txt","r") as f:
        for line in f:
            acceptance_ratio_history.append(float(line.strip()))
    # Create the figure
    plt.figure(plt.gcf().number + 1)
    plt.title("Annealing Temperature Profile with Acceptance Ratio")

    ax1 = plt.gca()
    ax1.plot(range(1, len(scaled_temperature_history) + 1), scaled_temperature_history, marker=".", color="tab:blue")
    ax1.set_xlabel("Number of Updates")
    ax1.set_ylabel("Temperature (%)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.set_ylim(ymin=0,ymax=100)

    ax2 = ax1.twinx()
    ax2.plot(range(1, len(acceptance_ratio_history) + 1), acceptance_ratio_history, marker=".", color="tab:orange")
    ax2.set_ylabel("Acceptance Ratio", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")
    ax2.set_ylim(ymin=0,ymax=1)

    plt.savefig(output_dir + "combo_history.png", dpi=300)
    ####################################################################################

########################################################################################
if __name__ == "__main__":
    main()