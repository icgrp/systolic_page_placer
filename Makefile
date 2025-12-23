# Benchmark
BENCHMARK_VERILOG=vtr_integration/dummy_benchmark/dummy_benchmark.v

# Don't touch
BENCHMARK_NAME=$(basename $(notdir $(BENCHMARK_VERILOG)))
BENCHMARK_BLIF=$(CURDIR)/build/synth/$(BENCHMARK_NAME).blif

# Placer parameters
WIDTH=35
HEIGHT=35
N_IO=800
UPDATES=100
SWAPS_PER_UPDATE=10
INITIAL_TEMP=65533

# Don't touch
SYSTOLIC_ARCH_TEMPLATE=vtr_integration/arch/heterogeneous_k10.xml
SYSTOLIC_GRID_INFO=build/pnr/systolic_grid_info
SYSTOLIC_ARCH_INFO=build/pnr/systolic_arch_info
SYSTOLIC_NETLIST_INFO=build/pnr/systolic_netlist_info
SYSTOLIC_IO_PLACE=build/pnr/systolic_io.place
PLACER_INIT=build/placer_init/placer_init

# Router options
ROUTE_CHAN_WIDTH=200


#######################################################################################################################################################################################################
synth:	
	@mkdir -p build/synth
	$$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py $(BENCHMARK_VERILOG) $(SYSTOLIC_ARCH_TEMPLATE) -start parmys -end abc -temp_dir $(CURDIR)/build/synth
	cp build/synth/$(BENCHMARK_NAME).abc.blif build/synth/$(BENCHMARK_NAME).blif
#######################################################################################################################################################################################################
init:
	@mkdir -p build/pnr
	@mkdir -p build/netlist_histograms
	@mkdir -p build/arch
	@mkdir -p build/placer_init
	@python3 scripts/gen_arch.py ${WIDTH} ${HEIGHT} ${SYSTOLIC_ARCH_TEMPLATE} build/arch/systolic.xml
	(cd build/pnr && \
	$$VTR_ROOT/vpr/vpr ../arch/systolic.xml ${BENCHMARK_BLIF} --pack --place --inner_num 1.0)
	@python3 scripts/gen_io_placement.py build/pnr/*.place ${SYSTOLIC_NETLIST_INFO} ${SYSTOLIC_IO_PLACE}
	@python3 scripts/gen_netlist_hist.py ${SYSTOLIC_NETLIST_INFO} build/netlist_histograms
	@python3 scripts/gen_placer_init.py ${SYSTOLIC_GRID_INFO} ${PLACER_INIT}
#######################################################################################################################################################################################################
rtl:
	@mkdir -p build/generated_rtl
	@mkdir -p build/rtl_export
	@python3 scripts/gen_rtl.py ${SYSTOLIC_GRID_INFO} ${SYSTOLIC_ARCH_INFO} -o build/generated_rtl --n_io ${N_IO}
	@cp -r build/generated_rtl/ build/rtl_export
	@mkdir -p build/rtl_export/common
	@cp -r src/* build/rtl_export/common
#######################################################################################################################################################################################################
firmware:
	@mkdir -p build/vitis_firmware_export/
	@python3 scripts/gen_firmware.py build/generated_rtl/params.txt build/vitis_firmware_export/systolic_params.h
	@cp vitis_firmware/main.c build/vitis_firmware_export/
#######################################################################################################################################################################################################
bit:
	@mkdir -p build/bitstream
	@python3 scripts/gen_bitstream.py ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) ${SYSTOLIC_IO_PLACE} $(PLACER_INIT) build/generated_rtl/params.txt build/bitstream/bitstream.txt --num_of_updates $(UPDATES) --swaps_per_update $(SWAPS_PER_UPDATE) --initial_temp $(INITIAL_TEMP)
#######################################################################################################################################################################################################
rtlsim:
#	simulation
	@mkdir -p build/rtlsim_out/
	@iverilog -Wall -o sim.vvp build/generated_rtl/tb.sv build/generated_rtl/placer.sv build/generated_rtl/sub_placer_modules/* build/generated_rtl/specialized_pe_modules/* src/* -s test_tb
	@vvp sim.vvp -fst
	@mv sim.vvp build/rtlsim_out/
	@mv trace.fst build/rtlsim_out/
	@mv trace.csv build/rtlsim_out/
	@mv unload.txt build/rtlsim_out/
	@python3 scripts/process_unload.py ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) build/generated_rtl/params.txt build/rtlsim_out/unload.txt build/rtlsim_out/unload.place
	@cat build/rtlsim_out/unload.place $(SYSTOLIC_IO_PLACE) > build/rtlsim_out/complete_unload.place

#	check   
	@python3 scripts/check_trace.py ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) ${SYSTOLIC_IO_PLACE} build/rtlsim_out/trace.csv build/rtlsim_out/
	@cat build/rtlsim_out/initial_systolic.place $(SYSTOLIC_IO_PLACE) > build/rtlsim_out/complete_initial.place
	@cat build/rtlsim_out/final_systolic.place $(SYSTOLIC_IO_PLACE) > build/rtlsim_out/complete_final.place
	@python3 scripts/diff_placement.py build/rtlsim_out/complete_unload.place build/rtlsim_out/complete_final.place
#######################################################################################################################################################################################################
pysim:
#	simulation
	@mkdir -p build/pysim_out/
	@python3 scripts/pysim.py --updts $(UPDATES) --swps $(SWAPS_PER_UPDATE) --temp $(INITIAL_TEMP) ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) $(SYSTOLIC_IO_PLACE) $(PLACER_INIT) build/pysim_out

#	check
	@python3 scripts/check_trace.py ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) ${SYSTOLIC_IO_PLACE} build/pysim_out/behavioral_trace.csv build/pysim_out/ --acceptance_ratio_history build/pysim_out/acceptance_ratio_history.txt
	@cat build/pysim_out/initial_systolic.place $(SYSTOLIC_IO_PLACE) > build/pysim_out/complete_initial.place
	@cat build/pysim_out/final_systolic.place $(SYSTOLIC_IO_PLACE) > build/pysim_out/complete_final.place
#######################################################################################################################################################################################################
diff_trace:
	@python3 scripts/diff_trace.py build/rtlsim_out/trace.csv build/pysim_out/behavioral_trace.csv
#######################################################################################################################################################################################################
fpga:
	@mkdir -p build/fpga_out/
	@python3 scripts/load.py build/bitstream/bitstream.txt build/fpga_out/unload.txt
	@python3 scripts/process_unload.py ${SYSTOLIC_GRID_INFO} $(SYSTOLIC_NETLIST_INFO) build/generated_rtl/params.txt build/fpga_out/unload.txt build/fpga_out/unload.place
	@cat build/fpga_out/unload.place $(SYSTOLIC_IO_PLACE) > build/fpga_out/complete_unload.place
#######################################################################################################################################################################################################
diff_placement:
	@python3 scripts/diff_placement.py build/fpga_out/complete_unload.place build/pysim_out/complete_final.place
#######################################################################################################################################################################################################
route_pysim:
	@mkdir -p build/pysim_route/
	(cd build/pysim_route && \
	$$VTR_ROOT/vpr/vpr ../arch/systolic.xml ${BENCHMARK_BLIF} \
	--net_file ../pnr/*.net \
	--place_file ../pysim_out/complete_final.place \
	--route \
	--route_chan_width ${ROUTE_CHAN_WIDTH})

route_rtlsim:
	@mkdir -p build/rtlsim_route/
	(cd build/rtlsim_route && \
	$$VTR_ROOT/vpr/vpr ../arch/systolic.xml ${BENCHMARK_BLIF} \
	--net_file ../pnr/*.net \
	--place_file ../rtlsim_out/complete_unload.place \
	--route \
	--route_chan_width ${ROUTE_CHAN_WIDTH})

route_fpga:
	@mkdir -p build/fpga_route/
	(cd build/fpga_route && \
	$$VTR_ROOT/vpr/vpr ../arch/systolic.xml ${BENCHMARK_BLIF} \
	--net_file ../pnr/*.net \
	--place_file ../fpga_out/complete_unload.place \
	--route \
	--route_chan_width ${ROUTE_CHAN_WIDTH} --disp on)

vtr:
	@mkdir -p build/vtr
	(cd build/vtr && \
	$$VTR_ROOT/vpr/vpr ../arch/systolic.xml ${BENCHMARK_BLIF} \
	--place \
	--place_algorithm bounding_box \
	--place_quench_algorithm bounding_box \
	--net_file ../pnr/*.net \
	--fix_clusters ../../${SYSTOLIC_IO_PLACE} \
	--inner_num 1.0 \
	--route \
	--route_chan_width ${ROUTE_CHAN_WIDTH})

clean:
	@rm -rf build/

.PHONY: init rtl bit rtlsim pysim diff physical route_pysim route_rtlsim vtr clean
