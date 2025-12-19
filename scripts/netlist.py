from collections import Counter
########################################################################################
class Block:
    def __init__(self,name,blk_type,blk_id,connections):
        self.name = name
        self.type = blk_type
        self.id = blk_id
        self.connections = set(connections)
        self.weights = Counter(connections)
########################################################################################
class Netlist:
    name = ""
    file_hash = ""

    name_to_block = {}
    name_to_vtr_blk_id = {}

    systolic_type_id_to_name = {}
    netlist_types = set()
    ####################################################################################
    def __init__(self,filename):
        with open(filename,"r") as f:
            _, self.name, _, self.hash = f.readline().split()
            f.readline()

            # used to create unique systolic ids for each block of a given type
            type_to_id_count = {}

            # read each line in systolic_netlist_info
            for line in f:

                line = line.strip()
                line = line.split(",")

                blk_name, ty, vtr_blk_id = line[0].split(" ")
                
                # map the block's name to the block's vtr_blk_id
                self.name_to_vtr_blk_id[blk_name] = vtr_blk_id

                # if the block is of a new type, initilize the id count for that block
                # and initilize the map from the type and id to the block's name
                if ty not in self.netlist_types:
                    self.netlist_types.add(ty)
                    type_to_id_count[ty] = 0
                    self.systolic_type_id_to_name[ty] = {}

                # set the block's systolic id, and map the type and id to the block's name
                systolic_blk_id = type_to_id_count[ty]
                self.systolic_type_id_to_name[ty][systolic_blk_id] = blk_name
                type_to_id_count[ty] += 1

                # get the names of the connected blocks
                connected_blk_names = line[1:]

                # add the block to a name_to_block map
                self.name_to_block[blk_name] = Block(blk_name,ty,systolic_blk_id,connected_blk_names)
    ####################################################################################
    def validate(self):
        # check that the netlist is valid
        for blk_name in self.name_to_block.keys():
            for connection in self.name_to_block[blk_name].connections:
                if(connection not in self.name_to_block):
                    return (False,"Error: {a} connected to {b} that does not exist".format(a=blk_name,b=connection))
                elif(blk_name not in self.name_to_block[connection].connections):
                    return (False,"Error: {a} connected to {b}, but {b} is not connected to {a}".format(a=blk_name,b=connection))
                elif(self.name_to_block[blk_name].weights[connection] != self.name_to_block[connection].weights[blk_name]):
                    return (False,"Error: {a} connected to {b} with weight {w_a}, but {b} is connected to {a} with weight {w_b}".format(
                            a=blk_name,
                            b=connection,
                            w_a=self.name_to_block[blk_name].weights[connection],
                            w_b=self.name_to_block[connection].weights[blk_name]))
        return (True,"")
    ####################################################################################
    def stats(self):

        blk_counts = {}
        unique_connections = {}
        weights = {}

        for ty in self.netlist_types:
            blk_counts[ty] = 0
            unique_connections[ty] = []
            weights[ty] = []

        for block in self.name_to_block.values():
            blk_counts[block.type] += 1
            unique_connections[block.type].append(len(block.weights.items()))
            weights[block.type] += [x[1] for x in block.weights.items()]

        return (blk_counts, unique_connections, weights)
    ####################################################################################