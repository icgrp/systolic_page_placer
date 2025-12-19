import netlist as nl
import grid_info as gi
import placer_params as pp
import placer_init as pi
import io_placement as io
import math
import argparse
import log
from loc import *
from shell import *
####################################################################################
def create_bitstream(netlist,
                     io_placement,
                     grid_info,
                     placer_params,
                     sub_placer_params_dict,
                     placer_init,
                     num_of_updates,
                     swaps_per_update,
                     initial_temp,
                     bitstream_file):

    with open(bitstream_file,"w") as f:
        # first write the header containing the parameter N
        f.write("{}\n".format(hex(placer_params.N)[2:]))

        # (ty, N_t, blk_offset)
        ty_nt_offset_lst = pp.get_ty_nt_offset_lst(sub_placer_params_dict)

        # calculate temp parameters 
        num_temp_steps = (num_of_updates*swaps_per_update) - 1
        temp_dec_step = math.floor(initial_temp/num_temp_steps)
        temp_threshold = initial_temp - temp_dec_step*(num_temp_steps-1)

        for tripple in ty_nt_offset_lst:
            ty, N_t, blk_offset = tripple

            # loop through the ids of the home PEs
            for local_id in range(N_t):

                # get the coords of the PE we are creating a packet for
                home_coords = grid_info.grid[ty].get_home_pe_coords(local_id)

                # look up the block_id set at this location
                blk_id = placer_init.ty_loc_to_id[ty][home_coords]

                # compute k for blk_id
                k = calculate_k(netlist,ty,blk_id)

                # look up the seed set at this location
                seed = placer_init.ty_loc_to_seed[ty][home_coords]

                weight_ram_data = gen_weight_ram_data(netlist,placer_params,ty_nt_offset_lst,ty,local_id)

                f.write("{}\n".format(hex(blk_id)[2:]))
                f.write("{}\n".format(hex(k)[2:]))
                f.write("{}\n".format(hex(seed)[2:]))
                f.write("{}\n".format(hex(initial_temp)[2:]))
                f.write("{}\n".format(hex(temp_dec_step)[2:]))
                f.write("{}\n".format(hex(temp_threshold)[2:]))
                f.write("{}\n".format(hex(swaps_per_update)[2:]))
                f.write("{}\n".format(hex(num_of_updates)[2:]))
                f.write(weight_ram_data)

        x_sums, y_sums = gen_io_ram_data(netlist,io_placement,ty_nt_offset_lst,placer_params)

        cycles_per_swap = 10
        swap_cycle_target = swaps_per_update*cycles_per_swap

        ########
        # write first packet for the fixed pe
        f.write("{}\n".format(hex(swap_cycle_target)[2:]))
        f.write("{}\n".format(hex(num_of_updates)[2:]))
        
        for dummy in range(6):
            f.write("{}\n".format(hex(0)[2:]))

        for x_sum in x_sums:
            f.write("{}\n".format(hex(x_sum)[2:]))
        ########
        # write second packet for the fixed pe
        for dummy in range(8):
            f.write("{}\n".format(hex(0)[2:]))

        for y_sum in y_sums:
            f.write("{}\n".format(hex(y_sum)[2:]))
####################################################################################
def calculate_k(netlist,ty,blk_id):

    k = 0

    # If the block (ty, blk_id) exists in the netlist
    if(ty in netlist.systolic_type_id_to_name and 
       blk_id in netlist.systolic_type_id_to_name[ty]):
        
        blk_name = netlist.systolic_type_id_to_name[ty][blk_id]
        k = sum(netlist.name_to_block[blk_name].weights.values())

    return k
####################################################################################
def gen_weight_ram_data(netlist,placer_params,ty_nt_offset_lst,ty,local_id):

    weight_ram_data = ""
    
    # If the block (ty, local_id) exists in the netlist
    if(ty in netlist.systolic_type_id_to_name and
        local_id in netlist.systolic_type_id_to_name[ty]):
        
        blk_name = netlist.systolic_type_id_to_name[ty][local_id]

        # Loop through all possible connected blocks in the array (may not be in the netlist, or connected to our block)
        for global_order_elem in range(placer_params.N):
            connection_ty, connection_id = pp.global_order_elem_to_ty_and_id(global_order_elem, ty_nt_offset_lst)

            # If the possibly connected block exists in the netlist
            if(connection_ty in netlist.systolic_type_id_to_name and
                connection_id in netlist.systolic_type_id_to_name[connection_ty]):
                
                # Compute the connection weight from our block to this possibly connected block (weight might be 0)
                connection_name = netlist.systolic_type_id_to_name[connection_ty][connection_id]
                weight = netlist.name_to_block[blk_name].weights[connection_name]
            else:
                # Else if the possible connection does not exist in the netlist
                # then set all of its possible connection weights to zero
                weight = 0
            weight_ram_data += "{}\n".format(hex(weight)[2:])
    else:
        # Else if our block (ty, local_id) does not exist in the netlist
        # then set all of its possible connection weights to zero
        weight = 0
        for global_order_elem in range(placer_params.N):
            weight_ram_data += "{}\n".format(hex(weight)[2:])

    return weight_ram_data
####################################################################################
def gen_io_ram_data(netlist,io_placement,ty_nt_offset_lst,placer_params):

    x_sums = []
    y_sums = []
    for global_order_elem in range(placer_params.N):
        
        sum_x = 0
        sum_y = 0

        blk_ty, blk_id = pp.global_order_elem_to_ty_and_id(global_order_elem, ty_nt_offset_lst)
        
        if(blk_ty in netlist.systolic_type_id_to_name and blk_id in netlist.systolic_type_id_to_name[blk_ty]):
            # If the block exists in the netlist
            blk_name = netlist.systolic_type_id_to_name[blk_ty][blk_id]
            io_connections = [x for x in netlist.name_to_block[blk_name].connections if netlist.name_to_block[x].type == "io"]
            for io_connection in io_connections:
                weight = netlist.name_to_block[blk_name].weights[io_connection]
                sum_x += weight*io_placement[io_connection].x
                sum_y += weight*io_placement[io_connection].y

        x_sums.append(sum_x)
        y_sums.append(sum_y)

    return (x_sums, y_sums)
####################################################################################
def main():
    description = 'Generates bitstream from netlist'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("grid_info",help="systolic_grid_info file to load")
    p.add_argument("netlist",help="Netlist file to load")
    p.add_argument("io_placement",help="IO placement file to load")
    p.add_argument("placer_init",help="Placer init file to load")
    p.add_argument("placer_params",help="Placer parameters file to load")
    p.add_argument("bitstream",help="Bitstream file to generate")
    p.add_argument("--num_of_updates", help="num of updates", default=5)
    p.add_argument("--swaps_per_update",help="swaps per update", default=10)
    p.add_argument("--initial_temp",help="initial temp",default=0)
    args = p.parse_args()
    ################################################################################
    # Load and validate the netlist
    netlist_file_name = args.netlist
    log.blue("[Reading netlist]")
    netlist = nl.Netlist(netlist_file_name)
    valid, error = netlist.validate()
    if(not valid):
        log.red(error)
        return
    
    blk_counts, unique_connections, weights = netlist.stats()
    for ty in blk_counts:
        log.magenta("[{} count: {}]".format(ty,blk_counts[ty]))

    log.green("[Netlist loaded and validated]")
    ################################################################################
    # Load the placer and sub_placer parameters
    log.blue("[Reading parameters]")
    placer_params, sub_placer_params_dict = pp.read_params_from_file(args.placer_params)
    ###############################################################################
    # Load the systolic grid info
    grid_info_file_name = args.grid_info
    log.blue("[Reading grid_info]")
    grid_info = gi.Grid_info(grid_info_file_name)

    for ty in grid_info.grid_types:
        max_supported = (grid_info.grid[ty].width * grid_info.grid[ty].height)
        if(ty in blk_counts and blk_counts[ty] > max_supported):
            log.red("[Mapping Failed: Placer can only support {} blocks of type {}]".format(max_supported,ty))
            return
    if("io" in blk_counts and blk_counts["io"] > placer_params.N_io):
        log.red("[Mapping Failed: Placer can only support {} blocks of type io]".format(placer_params.N_io))
        return
    log.green("[Netlist fits placer]")
    ################################################################################
    # Loading placer_init file
    log.blue("[Loading placer_init file]")
    placer_init = pi.Placer_init(args.placer_init,grid_info)
    ################################################################################
    # Load io placement
    log.blue("[Reading io placement]")
    io_placement = io.get_io_placement(args.io_placement)
    ###############################################################################
    # Create bitstream
    create_bitstream(netlist,
                     io_placement,
                     grid_info,
                     placer_params,
                     sub_placer_params_dict,
                     placer_init,
                     int(args.num_of_updates),
                     int(args.swaps_per_update),
                     int(args.initial_temp),
                     args.bitstream)
    ################################################################################
    log.green("[Bitstream generated]")
####################################################################################
if __name__ == "__main__":
    main()
