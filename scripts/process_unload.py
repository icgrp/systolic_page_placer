import argparse
import placer_params as pp
import grid_info as gi
import netlist as nl
import log

####################################################################################
def write_placement(grid_info,netlist,placement_lst,filename):
    with open(filename,"w") as f:
        f.write("Netlist_File: {} Netlist_ID: {}\n".format(netlist.name,netlist.hash))
        f.write("Array size: {} x {} logic blocks\n".format(grid_info.total_width,grid_info.total_height)) # we add 2 to account for io perimeter 
        f.write("\n")
        f.write("{:<50}{:<8}{:<8}{:<8}{:<8}{:<8}\n".format("#block name","x","y","subblk","layer","block number"))
        f.write("{:<50}{:<8}{:<8}{:<8}{:<8}{:<8}\n".format("#----------","--","--","------","-----","------------"))

        for entry in placement_lst:
            blk_name, vtr_blk_id, blk_coords = entry
        
            f.write("{blk_name: <50}{x: <8}{y: <8}{subblk: <8}{layer: <8}#{blk_id: <8}\n".format(x=blk_coords.x,y=blk_coords.y,subblk="0",layer="0", blk_name=blk_name, blk_id=vtr_blk_id))
####################################################################################
def main():
    description = 'Creates VTR placement file from unload.txt'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("grid_info",help="systolic_grid_info file to load")
    p.add_argument("netlist",help="Netlist file to load")
    p.add_argument("placer_params",help="Placer parameters file to load")
    p.add_argument("unload_txt",help="unload.txt to load")
    p.add_argument("placement_file",help="Placement file to write")
    args = p.parse_args()
    ################################################################################
    log.blue("[Loading placer parameters]")
    placer_params, sub_placer_params_dict = pp.read_params_from_file(args.placer_params)

    log.blue("[Loading grid info]")
    grid_info = gi.Grid_info(args.grid_info)

    log.blue("[Loading netlist]")
    netlist = nl.Netlist(args.netlist)

    # (ty, N_t, blk_offset)
    ty_nt_offset_lst = pp.get_ty_nt_offset_lst(sub_placer_params_dict)
    ################################################################################
    # list of: (blk_name, vtr_blk_id, blk_coords)
    placement_lst = []

    log.blue("[Loading unload.txt file]")
    with open(args.unload_txt, "r") as f:

        for tripple in ty_nt_offset_lst:
            ty, N_t, blk_offset = tripple

            for home_id in range(N_t):
                blk_id = int(f.readline())

                if(ty in netlist.systolic_type_id_to_name and
                blk_id in netlist.systolic_type_id_to_name[ty]):
                    
                    blk_name = netlist.systolic_type_id_to_name[ty][blk_id]
                    vtr_blk_id = netlist.name_to_vtr_blk_id[blk_name]

                    pe_coords = grid_info.grid[ty].get_home_pe_coords(home_id)
                    blk_coords = grid_info.grid[ty].pe_loc_to_blk_loc[pe_coords]

                    placement_lst.append((blk_name, vtr_blk_id, blk_coords))

    log.blue("[Writing placement file]")
    write_placement(grid_info,netlist,placement_lst,args.placement_file)
####################################################################################
if __name__ == "__main__":
    main()
