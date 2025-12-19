from collections import Counter
from shell import *
import argparse
import string
import textwrap
import grid_info as gi
import arch_info as ai
import placer_params as pp
import loc
import math
import log

# Utilities
################################################################################################
def get_template_str(filename):
    with open(filename, "r") as f:
        template_str = f.read()
        return template_str
################################################################################################
def get_format_keys(s):
    # A utility that returns a list of keys in a format string
    return set([x[1] for x in string.Formatter().parse(s) if x[1] != None])
################################################################################################


# Sub-placer functions
################################################################################################
def create_pe_array(grid_info,placer_params,sub_placer_params,loc_to_adjusted_specialization):

    # get some parameters for easy access
    width = sub_placer_params.W_t
    height = sub_placer_params.H_t
    bus_width = placer_params.BUS_WIDTH

    # initilize the the pe_array string
    pe_array = ""
    row_seperator = "\n//"+("#"*144)+"\n"+"// Row {pe_y}\n"

    # loop in a grid to generate each PE
    for pe_y in range(height):
        
        # add a seperator after each row of PEs in the Verilog
        pe_array += textwrap.indent(row_seperator.format(pe_y=pe_y),4*" ")
        for pe_x in range(width):
        
            # Note: Even and Odd are with respect to the zero index
            odd_row = bool(pe_y % 2)
            even_row = not odd_row
            odd_col = bool(pe_x % 2)
            even_col = not odd_col

            # determine the particular specialization for the PE at this location
            p0,p1,p2,p3 = loc_to_adjusted_specialization[loc.PE_Loc(pe_x,pe_y)]
            module_name = "pe_{}_{}_{}_{}_{}".format(sub_placer_params.ty,p0,p1,p2,p3)


            # calculate the illegal swap phases for the PE
            phase_0_illegal = 1 if ((pe_x == width-1) and (pe_x%2 == 0)) else 0
            phase_1_illegal = 1 if (pe_y == 0) or ((pe_y == height-1) and (pe_y%2 == 1)) else 0
            phase_2_illegal = 1 if (pe_x == 0) or ((pe_x == width-1) and (pe_x%2 == 1)) else 0
            phase_3_illegal = 1 if ((pe_y == height-1) and (pe_y%2 == 0)) else 0
        
            ###############################################################################################
            # calculate the main bus input and output connections as well as the hot_move signals

            # initial right
            in_right = "pe_x{pe_x}_y{pe_y}_in_right".format(pe_x=pe_x,pe_y=pe_y)
            out_right = "pe_x{pe_x}_y{pe_y}_out_right".format(pe_x=pe_x,pe_y=pe_y)

            # initlal up
            in_up = "pe_x{pe_x}_y{pe_y}_in_up".format(pe_x=pe_x,pe_y=pe_y)

            # initial left
            in_left = "pe_x{x_old}_y{pe_y}_out_right".format(x_old=(pe_x-1),pe_y=pe_y)
            in_hot_move_left = "pe_x{x_old}_y{pe_y}_out_hot_move_right".format(x_old=(pe_x-1),pe_y=pe_y)
            out_left = "pe_x{x_old}_y{pe_y}_in_right".format(x_old=(pe_x-1),pe_y=pe_y)

            # initial down
            in_down = "pe_x{pe_x}_y{y_old}_out_up".format(pe_x=pe_x,y_old=(pe_y-1))
            in_hot_move_down = "pe_x{pe_x}_y{y_old}_out_hot_move_up".format(pe_x=pe_x,y_old=(pe_y-1))
            out_down = "pe_x{pe_x}_y{y_old}_in_up".format(pe_x=pe_x,y_old=(pe_y-1))

            # LEVEL 1 Adjustments 
            if(pe_x == 0):
                in_left = "{}'d0".format(bus_width)
                in_hot_move_left = "1'd0"
                out_left = ""

            if(pe_y == 0):
                in_down = "{}'d0".format(bus_width)
                in_hot_move_down = "1'd0"
                out_down = ""

            if(pe_x == width-1):
                in_right = "{}'d0".format(bus_width)

            if(pe_y == height-1):
                in_up = "completed_sum"

            # LEVEL 2 Adjustments 
            if(pe_x == 0 and pe_y == 0):
                in_left = "load_pipe_in"
                out_left = "unload_pipe_out"

            if(pe_y == height-1):
                if(even_row and (pe_x == width-1)):
                    out_right = "load_pipe_out"
                    in_right = "unload_pipe_in"

                elif(odd_row and (pe_x == 0)):
                    out_left = "load_pipe_out"
                    in_left = "unload_pipe_in"

            ###############################################################################################
            # calculate load_enable_in and load_enable_out

            # In the following, we say that a PE "defines" wire(s), but what is actually meant is
            # that wires are defined alongside a PE instantiation and labeled with its coordinates:
            # This next section of rtl generation is complex because some PEs define new wires for only
            # their inputs, while other only define new wires for their outputs, and yet others define
            # wires for both their inputs and their outputs. Each PE will connect 
            # its input and output to a wire (though that PE might might not have defined that signal).
            # This complexity is because the load_enable signal propegates through the array in a
            # snake-like order, but the PEs in the Verilog are instantiated in a regular grid pattern.
            # This, allong with the fact that Verilog wires must be defined before their use
            # (at least with Icarus), this makes the RTL generation quite difficult.

            def_wire_load_enable_in = ""
            def_wire_load_enable_out = ""

            if(even_row):
                # load_enable_in
                if(pe_x == 0 and pe_y == 0):
                    load_enable_in = "load_enable_in"
                elif(pe_x == 0 and pe_y != 0):
                    load_enable_in = "pe_x{pe_x}_y{pe_y}_load_enable_out".format(pe_x=pe_x,pe_y=pe_y-1)
                else:
                    load_enable_in = "pe_x{pe_x}_y{pe_y}_load_enable_out".format(pe_x=pe_x-1,pe_y=pe_y)

                # load_enable_out
                if(pe_x == (width - 1) and pe_y == (height - 1)):
                    load_enable_out = "load_enable_out"
                else:
                    def_wire_load_enable_out = "wire pe_x{pe_x}_y{pe_y}_load_enable_out;".format(pe_x=pe_x,pe_y=pe_y)
                    load_enable_out = "pe_x{pe_x}_y{pe_y}_load_enable_out".format(pe_x=pe_x,pe_y=pe_y)
                
            else:
                # load_enable_in
                if(pe_x == (width - 1)):
                    load_enable_in = "pe_x{pe_x}_y{pe_y}_load_enable_out".format(pe_x=pe_x,pe_y=pe_y-1)
                else:
                    load_enable_in = "pe_x{pe_x}_y{pe_y}_load_enable_in".format(pe_x=pe_x,pe_y=pe_y)

                # load_enable_out
                if(pe_x == 0 and pe_y == (height-1)):
                    def_wire_load_enable_in = "wire pe_x{pe_x}_y{pe_y}_load_enable_in;".format(pe_x=pe_x,pe_y=pe_y)
                    load_enable_out = "load_enable_out"
                elif(pe_x == 0):
                    def_wire_load_enable_in = "wire pe_x{pe_x}_y{pe_y}_load_enable_in;".format(pe_x=pe_x,pe_y=pe_y)
                    def_wire_load_enable_out = "wire pe_x{pe_x}_y{pe_y}_load_enable_out;".format(pe_x=pe_x,pe_y=pe_y)
                    load_enable_out = "pe_x{pe_x}_y{pe_y}_load_enable_out".format(pe_x=pe_x,pe_y=pe_y)
                else:
                    if(pe_x != (width-1)):
                        def_wire_load_enable_in = "wire pe_x{pe_x}_y{pe_y}_load_enable_in;".format(pe_x=pe_x,pe_y=pe_y)

                    load_enable_out = "pe_x{pe_x}_y{pe_y}_load_enable_in".format(pe_x=pe_x-1,pe_y=pe_y)

            ###############################################################################################
            # calculate the load and unload phases

            load_phase = -1
            unload_phase = -1
            if(even_row):
                if(even_col):
                    load_phase = 2      # left 
                    unload_phase = 0    # right
                else:
                    load_phase = 0      # left
                    unload_phase = 2    # right

                # override if needed
                
                if(pe_x == 0 and pe_y != 0):
                    load_phase = 1      # down

                if(pe_x == (width - 1) and pe_y != (height - 1)):
                    unload_phase = 3    # up

            else:
                if(even_col):
                    load_phase = 0      # right
                    unload_phase = 2    # left
                else:
                    load_phase = 2      # right
                    unload_phase = 0    # left
                
                # override if needed

                if(pe_x == (width - 1)):
                    load_phase = 3      # down

                if(pe_x == 0 and pe_y != (height - 1)):
                    unload_phase = 1    # up

            ###############################################################################################
            # configure the "complete" signal

            if(pe_x == 0 and pe_y == 0):
                complete = "complete"
            else:
                complete = ""
            ###############################################################################################
            # set the block coordinates for the PE

            blk_loc = grid_info.grid[sub_placer_params.ty].pe_loc_to_blk_loc[loc.PE_Loc(pe_x,pe_y)]
            blk_x = blk_loc.x
            blk_y = blk_loc.y

            ###############################################################################################
            # calculate the two synchronization delays needed for loading  

            home_blk_id = grid_info.grid[sub_placer_params.ty].get_home_blk_id(loc.PE_Loc(pe_x,pe_y))

            load_delay = (placer_params.N + 2 - (sub_placer_params.blk_id_offset + home_blk_id))

            start_delay = (placer_params.N - (sub_placer_params.blk_id_offset + home_blk_id)) + (placer_params.B - max(blk_x,blk_y))

            pe_array += "\n"
            
            ###############################################################################################
            # take all these calculated values and add them to a PE instantiation template and 
            # appened the populated template to the pe_array string

            # read in the pe template
            pe_inst_template = get_template_str("rtl_templates/pe_inst_template.sv")

            # populate the template
            pe_inst_str = pe_inst_template.format(module_name=module_name,
                                                pe_x=pe_x,  # pe_x vs blk_x needs to get fixed (is this still the case?)
                                                pe_y=pe_y,
                                                blk_x=blk_x,
                                                blk_y=blk_y,
                                                complete=complete,
                                                def_wire_load_enable_in=def_wire_load_enable_in,
                                                def_wire_load_enable_out=def_wire_load_enable_out,
                                                load_enable_in=load_enable_in,
                                                load_enable_out=load_enable_out,
                                                in_left=in_left,
                                                in_up=in_up,
                                                in_right=in_right,
                                                in_down=in_down,
                                                in_hot_move_left=in_hot_move_left,
                                                in_hot_move_down=in_hot_move_down,
                                                out_left=out_left,
                                                out_right=out_right,
                                                out_down=out_down,
                                                phase_0_illegal=phase_0_illegal,
                                                phase_1_illegal=phase_1_illegal,
                                                phase_2_illegal=phase_2_illegal,
                                                phase_3_illegal=phase_3_illegal,
                                                load_phase=load_phase,
                                                unload_phase=unload_phase,
                                                load_delay=load_delay,
                                                start_delay=start_delay)

            pe_array += textwrap.indent(pe_inst_str," "*4)

    return pe_array
################################################################################################
def sum_tree_node_inst(level,node,prev_level,in_a,in_b):

    # read in the template
    sum_tree_node_inst_template = get_template_str("rtl_templates/sum_tree_node_inst_template.sv")

    # populate the template
    sum_tree_node_inst_str = sum_tree_node_inst_template.format(level=level,
                                                                node=node,
                                                                prev_level=prev_level,
                                                                in_a=in_a,
                                                                in_b=in_b)

    return sum_tree_node_inst_str
################################################################################################
def create_summing_tree(placer_params,sub_placer_params):
    width = sub_placer_params.W_t
    height = sub_placer_params.H_t
    summing_tree = " "
    prev_node_count = width

    for i in range(0,max(1,math.ceil(math.log2(width)))):
        summing_tree += "\n//************************************************************************\n"
        summing_tree += "// Level {level}\n".format(level=i)

        node_count = math.ceil(prev_node_count/2)
        for j in range(0, node_count):
            in_a = "out_level{prev_level}_node{node}".format(prev_level=(i-1),node=j*2)
            in_b = "out_level{prev_level}_node{node}".format(prev_level=(i-1),node=(j*2 + 1))
            
            if(i == 0):
                in_a = "pe_x{col}_y{last_y}_out_up".format(last_y=height-1,col=(j*2))
                in_b = "pe_x{col}_y{last_y}_out_up".format(last_y=height-1,col=(j*2) + 1)

            in_b = in_b if ((j*2) + 1) <= (prev_node_count - 1) else "{}'d0".format(placer_params.BUS_WIDTH)
            summing_tree += sum_tree_node_inst(i,j,i-1,in_a,in_b)
        prev_node_count = node_count


    summing_tree += "\n\nassign partial_sum_out = out_level{level}_node0;".format(level=i)
    summing_tree = textwrap.indent(summing_tree," "*4)
    return summing_tree
################################################################################################
def create_sub_placer(sub_placer_params,pe_array,summing_tree):

    # read in the template
    sub_placer_template = get_template_str("rtl_templates/sub_placer_template.sv")

    # populate the template
    sub_array_str = sub_placer_template.format(ty=sub_placer_params.ty,
                                               blk_id_offset=sub_placer_params.blk_id_offset,
                                               W_t=sub_placer_params.W_t,
                                               H_t=sub_placer_params.H_t,
                                               B_t=sub_placer_params.B_t,
                                               R_t=sub_placer_params.R_t,
                                               pe_array=pe_array,
                                               summing_tree=summing_tree)

    return sub_array_str
################################################################################################


# Placer functions
################################################################################################
def create_tree_of_trees(ty_list,bus_width):
    tree_of_trees = " "
    prev_node_count = len(ty_list)
    for i in range(0,max(1,math.ceil(math.log2(len(ty_list))))):
        tree_of_trees += "\n//************************************************************************\n"
        tree_of_trees += "// Level {level}\n".format(level=i)

        node_count = math.ceil(prev_node_count/2)
        for j in range(0, node_count):
            in_a = "out_level{prev_level}_node{node}".format(prev_level=(i-1),node=j*2)
            in_b = "out_level{prev_level}_node{node}".format(prev_level=(i-1),node=(j*2 + 1))
            
            if(i == 0):
                in_a = "{}_partial_sum_out".format(ty_list[j*2])
                if ((j*2) + 1) <= (prev_node_count - 1):
                    in_b = "{}_partial_sum_out".format(ty_list[(j*2) + 1])

            in_b = in_b if ((j*2) + 1) <= (prev_node_count - 1) else "{}'d0".format(bus_width)
            tree_of_trees += sum_tree_node_inst(i,j,i-1,in_a,in_b)
        prev_node_count = node_count


    tree_of_trees += "\n\nassign tree_of_trees_out = out_level{level}_node0;".format(level=i)
    tree_of_trees = textwrap.indent(tree_of_trees," "*4)
    return tree_of_trees
################################################################################################
# Create the fixed_pe instantiation
def fixed_pe_inst(placer_params,RAM_CYCLES,MULT_CYCLES,fixed_pe_load_enable_in,fixed_pe_load_pipe_in):
    # read in the template
    fixed_pe_inst_template = get_template_str("rtl_templates/fixed_pe_inst_template.sv")

    sum_ram_fixed_x_delay_cycles = RAM_CYCLES + MULT_CYCLES + placer_params.MSAD + max(1,math.ceil(math.log2(placer_params.T))) - 1
    sum_ram_fixed_y_delay_cycles = RAM_CYCLES + MULT_CYCLES + placer_params.MSAD + max(1,math.ceil(math.log2(placer_params.T))) - 1

    # populate the template
    fixed_pe_inst_str = fixed_pe_inst_template.format(load_enable_in=fixed_pe_load_enable_in,
                                                      load_in=fixed_pe_load_pipe_in,
                                                      sum_ram_fixed_x_delay_cycles=sum_ram_fixed_x_delay_cycles,
                                                      sum_ram_fixed_y_delay_cycles=sum_ram_fixed_y_delay_cycles)

    fixed_pe_inst_str = textwrap.indent(fixed_pe_inst_str," "*4)

    return fixed_pe_inst_str
################################################################################################
# Create the entire placer
def create_placer(systolic_grid_info_file,
                  systolic_arch_info_file,
                  output_dir,
                  N_io, F_io,
                  RAM_CYCLES,
                  MULT_CYCLES,
                  FIXED_SUM_CYCLES):
    #########################################
    def direction_to_phase(pe_loc,direction_vector):

        # direction_vector format: [right, down, left, up]
        phase_vector = [0,0,0,0]

        if (pe_loc.x%2 == 0):
            phase_vector[0] = direction_vector[0]
            phase_vector[2] = direction_vector[2]
        else:
            phase_vector[0] = direction_vector[2]
            phase_vector[2] = direction_vector[0]

        if (pe_loc.y%2 == 0):
            phase_vector[1] = direction_vector[1]
            phase_vector[3] = direction_vector[3]
        else:
            phase_vector[1] = direction_vector[3]
            phase_vector[3] = direction_vector[1]
        
        return tuple(phase_vector)
    #########################################
    # Figure out specializations stuff
    def get_specializations(grid_info,ty):
        
        specializations = set()
        loc_to_specialization = {}

        width = grid_info.grid[ty].width
        height = grid_info.grid[ty].height

        for x in range(width):
            for y in range(height):

                # Get current locs
                pe_loc = loc.PE_Loc(x,y)
                blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[pe_loc]

                # Init swap dists
                left_swap_dist = 0
                right_swap_dist = 0
                up_swap_dist = 0
                down_swap_dist = 0

                # Compute swap dists
                if x > 0:
                    sense_pe_loc = loc.PE_Loc(x-1,y)
                    sense_blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[sense_pe_loc]
                    left_swap_dist = blk_loc.x - sense_blk_loc.x
                if x + 1 <= width - 1:
                    sense_pe_loc = loc.PE_Loc(x+1,y)
                    sense_blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[sense_pe_loc]
                    right_swap_dist = sense_blk_loc.x - blk_loc.x
                if y > 0:
                    sense_pe_loc = loc.PE_Loc(x,y-1)
                    sense_blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[sense_pe_loc]
                    down_swap_dist = blk_loc.y - sense_blk_loc.y
                if y + 1 <= height - 1:
                    sense_pe_loc = loc.PE_Loc(x,y+1)
                    sense_blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[sense_pe_loc]
                    up_swap_dist = sense_blk_loc.y - blk_loc.y

                swap_dists = (right_swap_dist,down_swap_dist,left_swap_dist,up_swap_dist)
                phase_vector = direction_to_phase(pe_loc,swap_dists)
                specializations.add(phase_vector)
                loc_to_specialization[pe_loc] = phase_vector

        return (specializations, loc_to_specialization)
    #########################################
    # Returns list of exclusive sets
    def get_exclusive_set_list(pe_types):
        #########################################    
        # returns true if two vectors aren't compatible
        def is_incompatible(v1, v2):
            for v1_i, v2_i in zip(v1, v2):
                if v1_i != v2_i and (v1_i != 0 and v2_i != 0):
                    return True
            return False
        #########################################
        # returns true if vector not compatible with a set
        def is_exclusive(s, v):
            for s_i in s:
                if is_incompatible(v, s_i):
                    return True
            return False
        #########################################
        exclusive_set_list = []
        for k in pe_types:
            added = False
            for s in exclusive_set_list:
                if not is_exclusive(s, k):
                    s.add(k)
                    added = True
                    break
            if not added:
                new_set = set()
                new_set.add(k)
                exclusive_set_list.append(new_set)
        return exclusive_set_list
    #########################################
    # Builds and returns a map of vectors (possibly unconstrained) to fully constrained vectors
    def get_vector_adjustment_map(exclusive_set_list):
        #########################################
        # returns the most constrained vector from a set
        def get_most_constrained(s):
            e = next(iter(s))
            mc = tuple([0 for x in range(len(e))])
            lz = len(e)
            for v in s:
                zero_count = v.count(0)
                if zero_count < lz:
                    lz = zero_count
                    mc = v
            return mc
        #########################################
        vector_adjustment_map = {}
        for s in exclusive_set_list:
            most_constrained = get_most_constrained(s)

            count = Counter(most_constrained)
            most_common_component = count.most_common(1)[0][0]
            most_common_component = 1 if most_common_component == 0 else most_common_component
            adjusted_vector = tuple([most_common_component if x == 0 else x for x in most_constrained])

            for v in s:
                vector_adjustment_map[v] = adjusted_vector

        return vector_adjustment_map
    #########################################
    # Creates verilog multipliers to be used in specialized pe modules
    def create_multiplier(factor):
        ctrl_str = bin(factor)[2:]
        reversed_ctrl_str = ctrl_str[::-1]

        not_empty = False
        multiplier_str = ""
        for i,x in enumerate(reversed_ctrl_str):
            if x == "1":
                if(not_empty):
                    multiplier_str += " + "
                multiplier_str += "(k << {})".format(i)
                not_empty = True

        return multiplier_str
    #########################################
    def create_specialized_pe_modules(grid_info):
        ty_to_loc_to_adjusted_specialization = {}
        ty_to_adjusted_specializations = {}
        for ty in grid_info.grid_types:
            specializations, loc_to_specialization = get_specializations(grid_info,ty)
            exclusive_set_list = get_exclusive_set_list(specializations)
            vector_adjustment_map = get_vector_adjustment_map(exclusive_set_list)
            ty_to_adjusted_specializations[ty] = set([x for x in vector_adjustment_map.values()])

            loc_to_adjusted_specialization = {}
            for loc in loc_to_specialization.keys():
                loc_to_adjusted_specialization[loc] = vector_adjustment_map[loc_to_specialization[loc]]

            ty_to_loc_to_adjusted_specialization[ty] = loc_to_adjusted_specialization

            # read in the template
            pe_template = get_template_str("rtl_templates/pe_template.sv")
            shell("mkdir -p {}".format(output_dir+"specialized_pe_modules/"),silent=True)
            for v in set(vector_adjustment_map.values()):
                module_name = "pe_{}_{}_{}_{}_{}".format(ty,v[0],v[1],v[2],v[3])
                log.magenta("[Generating {}]".format(module_name))
                with open(output_dir+"specialized_pe_modules/"+module_name+".sv", "w") as f:
                    phase_0_mult = create_multiplier(v[0])
                    phase_1_mult = create_multiplier(v[1])
                    phase_2_mult = create_multiplier(v[2])
                    phase_3_mult = create_multiplier(v[3])
                    pe = pe_template.format(name=module_name,phase_0_mult=phase_0_mult,phase_1_mult=phase_1_mult,phase_2_mult=phase_2_mult,phase_3_mult=phase_3_mult)
                    f.write(pe)
        return ty_to_adjusted_specializations, ty_to_loc_to_adjusted_specialization
    #########################################
    # Compute placer and all sub_placer parameters
    def compute_params(grid_info,arch_info,N_io,F_io,ty_to_adjusted_specializations):        
        #########################################    
        # Values used to compute placer params
        H_m, R_m, B_io = 0,0,0

        # Values to compute sub_placer params
        blk_id_offset = 0

        # Pre-packaged placer params
        K,P,D,B,MSAD,T,WSRD,V,BUS_WIDTH,N,T = 0,0,0,0,0,0,0,0,0,0,0

        ty_to_sub_placer_params = {}

        for ty in grid_info.grid:
            
            # Set W_t and H_t
            W_t = grid_info.grid[ty].width
            H_t = grid_info.grid[ty].height

            # Calculate B_t
            extreme_blk_loc = grid_info.grid[ty].pe_loc_to_blk_loc[loc.PE_Loc(W_t-1,H_t-1)]
            B_t = max(extreme_blk_loc.x,extreme_blk_loc.y)

            # Calculate R_t
            R_t = 0
            for vector in ty_to_adjusted_specializations[ty]:
                R_t = max(R_t,max(vector))

            # Read F_t
            F_t = arch_info.arch_types_to_fanin[ty]

            # Compute N_t
            N_t = W_t*H_t

            # Partially compute V
            V = max(V, F_t)

            # Partially compute K
            K += F_t * N_t

            # Partially compute P
            P += F_t * N_t * B_t

            # Partially compute D
            D = max(D,W_t,H_t)

            # Partially compute B
            B = max(B,B_t)

            # Partially compute MSAD
            MSAD = max(MSAD,H_t + math.ceil(math.log2(W_t)))

            # Partially compute T
            T += 1

            # Partially compute H_m
            H_m = max(H_m, H_t)

            # Partially compute R_m
            R_m = max(R_m, R_t)

            # Wrap up the sub placer params
            ty_to_sub_placer_params[ty] = pp.SubPlacerParams(ty,blk_id_offset,W_t,H_t,N_t,B_t,R_t,F_t)

            # Update blk_id_offset
            blk_id_offset += N_t

        # IO specific info
        B_io = max(grid_info.total_width, grid_info.total_height)

        # compute N
        N = blk_id_offset

        # complete the computation of V
        V *= 2

        # update K and P with the above IO information
        K += F_io * N_io
        P += F_io * N_io * B_io

        # Compute WSRD
        WSRD = H_m - 1

        # Compute SCD
        SCD = RAM_CYCLES + MULT_CYCLES + MSAD + max(1,math.ceil(math.log2(T))) + FIXED_SUM_CYCLES

        # Compute the bus width
        # Note: 16 is a lower bound because of how the loading circuit was implimented
        BUS_WIDTH = max(math.ceil(math.log2(2*P + K*R_m + 1)) + 1, 16)

        # Package the placer params
        placer_params = pp.PlacerParams(N,N_io,F_io,T,V,K,P,D,B,MSAD,WSRD,SCD,BUS_WIDTH)

        return (placer_params, ty_to_sub_placer_params)
    #########################################
    # Create the sub_placer module files
    def create_sub_placer_modules(grid_info,
                                  placer_params,
                                  ty_to_sub_placer_params,
                                  ty_to_loc_to_adjusted_specialization):

        for ty in grid_info.grid:
            sub_placer_params = ty_to_sub_placer_params[ty]

            W_t = sub_placer_params.W_t
            H_t = sub_placer_params.H_t
            log.magenta("[Building {} sub array: {} by {}]".format(ty,W_t,H_t))
            sub_placer_params.print()

            # Create sub_placer modules
            pe_array = create_pe_array(grid_info,placer_params,sub_placer_params,ty_to_loc_to_adjusted_specialization[ty])
            summing_tree = create_summing_tree(placer_params,sub_placer_params)
            sub_placer = create_sub_placer(sub_placer_params,pe_array,summing_tree)

            # Output the sub_placer module files
            shell("mkdir -p {}".format(output_dir+"sub_placer_modules/"),silent=True)
            with open(output_dir+"sub_placer_modules/sub_placer_{}.sv".format(ty),"w") as f:
                f.write(sub_placer)
    ############################################################
    # Create the placer

    # Load systolic grid info
    log.blue("[Loading systolic_grid_info]")
    grid_info = gi.Grid_info(systolic_grid_info_file)

    # Load systolic arch info 
    log.blue("[Loading systolic_arch_info_file]")
    arch_info = ai.Arch_info(systolic_arch_info_file)

    # Create specilized PE modules
    log.blue("[Creating specilized PE modules]")
    ty_to_adjusted_specializations, ty_to_loc_to_adjusted_specialization = create_specialized_pe_modules(grid_info)
    log.green("[Creation of specilized PE modules complete]")

    # Compute RTL parameters
    log.blue("[Computing RTL parameters]")
    placer_params, ty_to_sub_placer_params = compute_params(grid_info,arch_info,N_io,F_io,ty_to_adjusted_specializations)
    log.green("[Computation of parameters complete]")
    pp.write_params_to_file("{}params.txt".format(output_dir),placer_params,[x for x in ty_to_sub_placer_params.values()])
    log.blue("[Parameters written to file]")
    placer_params.print()

    # Create the sub_placer modules
    log.blue("[Creating sub_placer modules]")
    create_sub_placer_modules(grid_info,placer_params,ty_to_sub_placer_params,ty_to_loc_to_adjusted_specialization)
    log.green("[Creation of sub_placer modules complete]")

    # Read in the template files
    placer_template = get_template_str("rtl_templates/placer_template.sv")
    sub_placer_inst_template = get_template_str("rtl_templates/sub_placer_inst_template.sv")

    # Create the sub_placer instances
    log.blue("[Creating sub_placer instances]")
    sub_placers = ""

    ty_nt_offset_lst = pp.get_ty_nt_offset_lst(ty_to_sub_placer_params)

    old_ty = ""
    for tripple in ty_nt_offset_lst:
        ty, N_t, offset = tripple

        load_pipe_out = "{}_load_pipe_out".format(ty)
        unload_pipe_in = "{}_unload_pipe_in".format(ty)

        partial_sum_out = "{}_partial_sum_out".format(ty)

        if(old_ty == ""):
            load_enable_in = "load_enable_in"
            load_pipe_in = "load_in"
            unload_pipe_out = "unload_out"
        else:
            load_enable_in = "load_enable_out_{}".format(old_ty)
            load_pipe_in = "{}_load_pipe_out".format(old_ty)
            unload_pipe_out = "{}_unload_pipe_in".format(old_ty)

        sub_placer_inst = sub_placer_inst_template.format(ty=ty,partial_sum_out=partial_sum_out,load_enable_in=load_enable_in,load_pipe_in=load_pipe_in,load_pipe_out=load_pipe_out,unload_pipe_in=unload_pipe_in,unload_pipe_out=unload_pipe_out)
        sub_placers += sub_placer_inst + "\n\n"
        old_ty = ty

    fixed_pe_load_enable_in = "load_enable_out_{}".format(old_ty)
    fixed_pe_load_pipe_in = "{}_load_pipe_out".format(old_ty)

    sub_placers.rstrip()
    sub_placers = textwrap.indent(sub_placers," "*4)
    log.green("[Creation of sub_placer instances complete]")

    # Create the tree of trees
    log.blue("[Creating tree of trees]")
    tree_of_trees = create_tree_of_trees(list(grid_info.grid_types),placer_params.BUS_WIDTH)
    log.green("[Creation of tree of trees complete]")

    # Create the fixed PE
    log.blue("[Creating fixed_pe]")
    fixed_pe = fixed_pe_inst(placer_params,RAM_CYCLES,MULT_CYCLES,fixed_pe_load_enable_in,fixed_pe_load_pipe_in)
    log.green("[Creation of fixed_pe complete]")

    # Generate the complete signal
    complete = "complete_{}".format(ty_nt_offset_lst[0][0])

    # Create placer module
    log.blue("[Creating placer module]")
    placer = placer_template.format(N=placer_params.N,T=placer_params.T,D=placer_params.D,B=placer_params.B,V=placer_params.V,MAX_K=placer_params.K,P=placer_params.P,N_io=N_io,F_io=F_io,
                                    MSAD=placer_params.MSAD,WSRD=placer_params.WSRD,RAM_CYCLES=RAM_CYCLES,MULT_CYCLES=MULT_CYCLES,FIXED_SUM_CYCLES=FIXED_SUM_CYCLES,SCD=placer_params.SCD,
                                    BUS_WIDTH=placer_params.BUS_WIDTH,MAX_NUM_OF_UPDATES=500,MAX_SWAPS_PER_UPDATE=500,
                                    sub_placers=sub_placers,tree_of_trees=tree_of_trees,fixed_pe=fixed_pe,complete=complete)
    
    # Output the placer module file
    with open(output_dir+"placer.sv","w") as f:
        f.write(placer)

    log.green("[Creation of placer module complete]\n")
################################################################################################


# Testbench functions
################################################################################################
def create_testbench(output_dir,
                     params_file,
                     systolic_grid_info_file):

    def make_display_and_write_strings(grid_info,sub_placer_params_dict,state):
        tb_display_str = ""
        tb_write_str = ""
        # Generate the display and fwrite commands 
        for ty in grid_info.grid_types:
            for pe_x in range(grid_info.grid[ty].width):
                for pe_y in range(grid_info.grid[ty].height):
                    tb_display_str += textwrap.indent(tb_display_template.format(ty_str="\"{}\"".format(ty),
                                                                                 state_str="\"{}\"".format(state),
                                                                                 pe_x_str="\"{}\"".format(pe_x),
                                                                                 pe_y_str="\"{}\"".format(pe_y),
                                                                                 x=pe_x,
                                                                                 y=pe_y,
                                                                                 ty=ty,
                                                                                 B_t=sub_placer_params_dict[ty].B_t),8*" ")
                    tb_write_str += textwrap.indent(tb_write_template.format(ty=ty,state=state,x=pe_x,y=pe_y,B_t=sub_placer_params_dict[ty].B_t),8*" ")
        return (tb_display_str, tb_write_str)

    # Load the parameters
    placer_params, sub_placer_params_dict = pp.read_params_from_file(params_file)

    # Read in the systolic_grid_info file
    grid_info = gi.Grid_info(systolic_grid_info_file)
    
    # Read in the template files
    tb_template = get_template_str("rtl_templates/tb_template.sv")
    tb_display_template = get_template_str("rtl_templates/tb_display.sv")
    tb_write_template = get_template_str("rtl_templates/tb_write.sv")

    sense_sub_array = "sub_placer_"+next(iter(grid_info.grid_types))+"_inst"

    sort_display_str, sort_write_str = make_display_and_write_strings(grid_info,sub_placer_params_dict,"post_sort")
    sum_display_str, sum_write_str = make_display_and_write_strings(grid_info,sub_placer_params_dict,"post_sum")
    swap_display_str, swap_write_str = make_display_and_write_strings(grid_info,sub_placer_params_dict,"post_swap")

    # Populate the testbench template and create the testbench file
    with open(output_dir+"tb.sv","w") as f:
        f.write(tb_template.format(BUS_WIDTH=placer_params.BUS_WIDTH,
                                   N=placer_params.N,
        
                                   sense_sub_array=sense_sub_array,
                                    
                                   sort_display_str=sort_display_str,
                                   sum_display_str=sum_display_str,
                                   swap_display_str=swap_display_str,

                                   sort_write_str=sort_write_str,
                                   sum_write_str=sum_write_str,
                                   swap_write_str=swap_write_str,

                                   trace_file="trace.csv",
                                   unload_file="unload.txt"))
################################################################################################


# Vivado Interface functions
################################################################################################
def create_vivado_interface(output_dir,params_file):

    # Load the parameters
    placer_params, sub_placer_params_dict = pp.read_params_from_file(params_file)

    placer_interface_template = get_template_str("rtl_templates/placer_interface_template.sv")
    with open(output_dir+"placer_interface.sv","w") as f:
        f.write(placer_interface_template.format(BUS_WIDTH=placer_params.BUS_WIDTH,N=placer_params.N))
################################################################################################


# Main
################################################################################################
def main():

    description = 'Generates Verilog and RAM init files for the systolic placer'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("grid_info",help="grid_info file")
    p.add_argument("arch_info",help="arch_info file")
    p.add_argument("-o", help="output dir",default="generated_rtl/")
    p.add_argument("--n_io", help="number of io", default=100)
    p.add_argument("--f_io", help="io fanin", default=1)
    p.add_argument("--ram_cycles", help="ram cycles", default=1)
    p.add_argument("--mult_cycles", help="mult cycles", default=0)
    p.add_argument("--fixed_sum_cycles", help="fixed sum cycles", default=1)
    args = p.parse_args()

    # sanitize the output dir name
    output_dir = args.o if args.o[-1] == "/" else (args.o + "/")

    shell("mkdir -p {}".format(output_dir))

    # Create the Placer RTL
    create_placer(args.grid_info,
                  args.arch_info,
                  output_dir,
                  int(args.n_io),
                  int(args.f_io),
                  int(args.ram_cycles),
                  int(args.mult_cycles),
                  int(args.fixed_sum_cycles))    

    # Create the Vivado interface RTL
    create_vivado_interface(output_dir,
                            output_dir+"params.txt")

    # Create the testbench RTL
    create_testbench(output_dir,
                     output_dir+"params.txt",
                     args.grid_info)
################################################################################################
if __name__ == "__main__":
    main()