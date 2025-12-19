import log
################################################################################
class PlacerParams:
    def __init__(self,N,N_io,F_io,T,V,K,P,D,B,MSAD,WSRD,SCD,BUS_WIDTH):
        self.N = N
        self.N_io = N_io
        self.F_io = F_io
        self.T = T
        self.V = V
        self.K = K
        self.P = P
        self.D = D
        self.B = B
        self.MSAD = MSAD
        self.WSRD = WSRD
        self.SCD = SCD
        self.BUS_WIDTH = BUS_WIDTH

    def __str__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(self.N,
                                                               self.N_io,
                                                               self.F_io,
                                                               self.T,
                                                               self.V,
                                                               self.K,
                                                               self.P,
                                                               self.D,
                                                               self.B,
                                                               self.MSAD,
                                                               self.WSRD,
                                                               self.SCD,
                                                               self.BUS_WIDTH)

    def print(self):
        log.yellow("[N = {}]".format(self.N))
        log.yellow("[N_io = {}]".format(self.N_io))
        log.yellow("[F_io = {}]".format(self.F_io))
        log.yellow("[T = {}]".format(self.T))
        log.yellow("[V = {}]".format(self.V))
        log.yellow("[K = {}]".format(self.K))
        log.yellow("[P = {}]".format(self.P))
        log.yellow("[D = {}]".format(self.D))
        log.yellow("[B = {}]".format(self.B))
        log.yellow("[MSAD = {}]".format(self.MSAD))
        log.yellow("[WSRD = {}]".format(self.WSRD))
        log.yellow("[SCD = {}]".format(self.SCD))
        log.yellow("[BUS_WIDTH = {}]".format(self.BUS_WIDTH))
################################################################################
class SubPlacerParams:
    def __init__(self,ty,blk_id_offset,W_t,H_t,N_t,B_t,R_t,F_t):
        self.ty = ty
        self.blk_id_offset = blk_id_offset
        self.W_t = W_t
        self.H_t = H_t
        self.N_t = N_t
        self.B_t = B_t
        self.R_t = R_t
        self.F_t = F_t

    def __str__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}".format(self.ty,
                                                        self.blk_id_offset,
                                                        self.W_t,
                                                        self.H_t,
                                                        self.N_t,
                                                        self.B_t,
                                                        self.R_t,
                                                        self.F_t)

    def print(self):
        log.yellow("[Type: {}]".format(self.ty))
        log.yellow("[blk_id_offset = {}]".format(self.blk_id_offset))
        log.yellow("[W_t = {}]".format(self.W_t))
        log.yellow("[H_t = {}]".format(self.H_t))
        log.yellow("[N_t = {}]".format(self.N_t))
        log.yellow("[B_t = {}]".format(self.B_t))
        log.yellow("[R_t = {}]".format(self.R_t))
        log.yellow("[F_t = {}]".format(self.F_t))
################################################################################





################################################################################
def write_params_to_file(filename, placer_params, sub_placer_params_lst):
    with open(filename, "w") as f:
        f.write("N, N_io, F_io, T, V, K, P, D, B, MSAD, WSRD, SCD, BUS_WIDTH\n")
        f.write(str(placer_params)+"\n")
        f.write("ty, blk_id_offset, W_t, H_t, N_t, B_t, R_t, F_t\n")
        for sub_placer_params in sub_placer_params_lst:
            f.write(str(sub_placer_params)+"\n")

def read_params_from_file(filename):
    with open(filename, "r") as f:

        # load the placer_params
        f.readline()
        param_str = f.readline()
        param_lst = [int(x) for x in param_str.split(", ")]
        placer_params = PlacerParams(*param_lst)

        # load the sub_placer_params
        f.readline()
        sub_placer_params_dict = {}
        for param_str in f:
            param_str_lst = param_str.split(", ")
            ty = param_str_lst[0]
            int_param_lst = [int(x) for x in param_str_lst[1:]]
            sub_placer_params_dict[ty] = SubPlacerParams(ty,*int_param_lst)
        
        return (placer_params, sub_placer_params_dict)
    
################################################################################
# Creates a sorted list of tuples of type (ty, N_t, blk_offset)
# which will be used to order the sub-placers and to convert a 
# global_order_elem to a blk_ty and blk_id in global_order_elem_to_ty_and_id()
def get_ty_nt_offset_lst(sub_placer_params_dict):
    ty_nt_offset_lst = []
    for sub_placer_params in sub_placer_params_dict.values():
        ty_nt_offset_lst.append((sub_placer_params.ty, sub_placer_params.N_t, sub_placer_params.blk_id_offset))
    ty_nt_offset_lst.sort(key=lambda x:x[2])
    return ty_nt_offset_lst
################################################################################
# This function takes a global order element and returns a type and a local
# block id. For example: The placers might have two sub placers, one for CLBs
# and another for BRAMS. The CLB array might have 100 PEs and the BRAM array
# might only have 10 PEs. When the placer is built, the BRAM array is indexed
# after the CLB array, since it has fewer PEs. If we give a global order element
# (which is sort of like a global blk_id) to this function, it will give us the
# type and local blk_id associated with it. So in this example, if we give it
# elem = 0, it will give us (CLB, 0). If we give it elem = 100, it will give us
# (BRAM, 0).
def global_order_elem_to_ty_and_id(elem, ty_nt_offset_lst):
    for x in ty_nt_offset_lst:
        blk_id_offset = x[2]
        n_t = x[1]
        ty = x[0]
        if elem < blk_id_offset + n_t and elem >= 0:
            return ty, (elem - blk_id_offset)
    log.red("[Error: Illegal elem value: {}]".format(elem))
################################################################################