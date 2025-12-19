from multiprocessing import Pool
from matplotlib import pyplot as plt
from matplotlib import patches as patches
import subprocess
import numpy as np
import random
import log

# Utilities 
####################################################################################
def shell(command,silent=False,capture=False):
    output = subprocess.run(command,shell=True,capture_output=capture,text=True)
    if not silent and output.stdout:
        print(output.stdout,end="")
    return output
####################################################################################
def get_working_dir():
     return shell("pwd",silent=True,capture=True).stdout.strip() + "/"
####################################################################################





####################################################################################
def create_arch(suite_name,width,height,arch_template):
    shell("mkdir -p {suite}/arch".format(suite=suite_name))
    shell("python3 scripts/gen_arch.py {width} {height} {template} {suite}/arch/systolic.xml".format(suite=suite_name,width=width,height=height,template=arch_template))
####################################################################################
def synth(suite_name,verilog_file,name):
    working_dir = get_working_dir()
    shell("$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py {verilog_file} {suite}/arch/systolic.xml -start parmys -end abc -temp_dir {w_dir}/{suite}/{name}".format(verilog_file=verilog_file,suite=suite_name,w_dir=working_dir,name=name))
    shell("mv {w_dir}/{suite}/{name}/{name}.abc.blif {w_dir}/{suite}/{name}/{name}.blif".format(w_dir=working_dir,suite=suite_name,name=name))
####################################################################################






####################################################################################
suite_name = "synth"

# benchmark_names = ["arm_core",
#                    "bgm",
#                    "blob_merge",
#                    "mkSMAdapter4B",
#                    "or1200",
#                    "raygentop",
#                    "sha",
#                    "stereovision0"]

benchmark_names = ["LU32PEEng",
                   "mcml",
                   "stereovision2",
                   "hetero_placer"]

benchmark_names = ["hetero_placer"]

# create the arch
arch_template = get_working_dir()+"vtr_integration/arch/heterogeneous_k10.xml"
create_arch(suite_name,100,100,arch_template)

# synth the benchmarks
for name in benchmark_names:
    #verilog_file = "$VTR_ROOT/vtr_flow/benchmarks/verilog/{}.v".format(name)
    verilog_file = "/home/ept/research/systolic_placer/meta_synth/{}.sv".format(name)
    synth(suite_name,verilog_file,name)
####################################################################################