import json
import log
################################################################################
class PlacerParams:
    def __init__(self,N,N_io,F_io,T,V,K,P,D,B,MSAD,WSRD,SCD,BUS_WIDTH,
                 RAM_CYCLES,SUM_COORD_CYCLES,MULT_CYCLES,CYCLES_PER_SWAP,
                 MAX_NUM_OF_UPDATES,MAX_SWAPS_PER_UPDATE):
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
        self.RAM_CYCLES = RAM_CYCLES
        self.SUM_COORD_CYCLES = SUM_COORD_CYCLES
        self.MULT_CYCLES = MULT_CYCLES
        self.CYCLES_PER_SWAP = CYCLES_PER_SWAP
        self.MAX_NUM_OF_UPDATES = MAX_NUM_OF_UPDATES
        self.MAX_SWAPS_PER_UPDATE = MAX_SWAPS_PER_UPDATE

    def to_dict(self):
        return {
            "N":                   self.N,
            "N_io":                self.N_io,
            "F_io":                self.F_io,
            "T":                   self.T,
            "V":                   self.V,
            "K":                   self.K,
            "P":                   self.P,
            "D":                   self.D,
            "B":                   self.B,
            "MSAD":                self.MSAD,
            "WSRD":                self.WSRD,
            "SCD":                 self.SCD,
            "BUS_WIDTH":           self.BUS_WIDTH,
            "RAM_CYCLES":          self.RAM_CYCLES,
            "SUM_COORD_CYCLES":    self.SUM_COORD_CYCLES,
            "MULT_CYCLES":         self.MULT_CYCLES,
            "CYCLES_PER_SWAP":     self.CYCLES_PER_SWAP,
            "MAX_NUM_OF_UPDATES":  self.MAX_NUM_OF_UPDATES,
            "MAX_SWAPS_PER_UPDATE": self.MAX_SWAPS_PER_UPDATE,
        }

    def print(self):
        log.yellow(f"[N = {self.N}]")
        log.yellow(f"[N_io = {self.N_io}]")
        log.yellow(f"[F_io = {self.F_io}]")
        log.yellow(f"[T = {self.T}]")
        log.yellow(f"[V = {self.V}]")
        log.yellow(f"[K = {self.K}]")
        log.yellow(f"[P = {self.P}]")
        log.yellow(f"[D = {self.D}]")
        log.yellow(f"[B = {self.B}]")
        log.yellow(f"[MSAD = {self.MSAD}]")
        log.yellow(f"[WSRD = {self.WSRD}]")
        log.yellow(f"[SCD = {self.SCD}]")
        log.yellow(f"[BUS_WIDTH = {self.BUS_WIDTH}]")
        log.yellow(f"[RAM_CYCLES = {self.RAM_CYCLES}]")
        log.yellow(f"[SUM_COORD_CYCLES = {self.SUM_COORD_CYCLES}]")
        log.yellow(f"[MULT_CYCLES = {self.MULT_CYCLES}]")
        log.yellow(f"[CYCLES_PER_SWAP = {self.CYCLES_PER_SWAP}]")
        log.yellow(f"[MAX_NUM_OF_UPDATES = {self.MAX_NUM_OF_UPDATES}]")
        log.yellow(f"[MAX_SWAPS_PER_UPDATE = {self.MAX_SWAPS_PER_UPDATE}]")
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

    def to_dict(self):
        return {
            "blk_id_offset": self.blk_id_offset,
            "W_t":           self.W_t,
            "H_t":           self.H_t,
            "N_t":           self.N_t,
            "B_t":           self.B_t,
            "R_t":           self.R_t,
            "F_t":           self.F_t,
        }

    def print(self):
        log.yellow(f"[Type: {self.ty}]")
        log.yellow(f"[blk_id_offset = {self.blk_id_offset}]")
        log.yellow(f"[W_t = {self.W_t}]")
        log.yellow(f"[H_t = {self.H_t}]")
        log.yellow(f"[N_t = {self.N_t}]")
        log.yellow(f"[B_t = {self.B_t}]")
        log.yellow(f"[R_t = {self.R_t}]")
        log.yellow(f"[F_t = {self.F_t}]")
################################################################################
def write_params_to_file(filename, placer_params, sub_placer_params_lst):
    params = {
        "placer_params": placer_params.to_dict(),
        "sub_placer_params": {
            sp.ty: sp.to_dict() for sp in sub_placer_params_lst
        }
    }
    with open(filename, "w") as f:
        json.dump(params, f, indent=4)

def read_params_from_file(filename):
    with open(filename, "r") as f:
        params = json.load(f)

    pp = params["placer_params"]
    placer_params = PlacerParams(
        N                   = pp["N"],
        N_io                = pp["N_io"],
        F_io                = pp["F_io"],
        T                   = pp["T"],
        V                   = pp["V"],
        K                   = pp["K"],
        P                   = pp["P"],
        D                   = pp["D"],
        B                   = pp["B"],
        MSAD                = pp["MSAD"],
        WSRD                = pp["WSRD"],
        SCD                 = pp["SCD"],
        BUS_WIDTH           = pp["BUS_WIDTH"],
        RAM_CYCLES          = pp["RAM_CYCLES"],
        SUM_COORD_CYCLES    = pp["SUM_COORD_CYCLES"],
        MULT_CYCLES         = pp["MULT_CYCLES"],
        CYCLES_PER_SWAP     = pp["CYCLES_PER_SWAP"],
        MAX_NUM_OF_UPDATES  = pp["MAX_NUM_OF_UPDATES"],
        MAX_SWAPS_PER_UPDATE = pp["MAX_SWAPS_PER_UPDATE"],
    )

    sub_placer_params_dict = {}
    for ty, sp in params["sub_placer_params"].items():
        sub_placer_params_dict[ty] = SubPlacerParams(
            ty            = ty,
            blk_id_offset = sp["blk_id_offset"],
            W_t           = sp["W_t"],
            H_t           = sp["H_t"],
            N_t           = sp["N_t"],
            B_t           = sp["B_t"],
            R_t           = sp["R_t"],
            F_t           = sp["F_t"],
        )

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
    log.red(f"[Error: Illegal elem value: {elem}]")
################################################################################
