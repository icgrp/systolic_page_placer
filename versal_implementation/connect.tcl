connect -url tcp:127.0.0.1:3121
targets -set -nocase -filter {name =~"Versal*"}
rst -system
after 3000
targets -set -filter {jtag_cable_name =~ "Xilinx VCK190 FT4232H 592036123983A" && name=="PMC" && jtag_device_ctx=="jsn-VCK190 FT4232H-592036123983A-04ca8093-0"}
device program versal_implementation/prebuilt_binaries/design_1_wrapper.pdi
targets -set -nocase -filter {name =~ "*A72*#0"}
rst -processor
dow versal_implementation/prebuilt_binaries/heterogeneous_k10_35_35.elf
targets -set -nocase -filter {name =~ "*A72*#0"}
con
