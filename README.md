# systolic_page_placer

## Makefile

- Run `make synth` to synthesize the benchmark blif file from a Verilog benchmark. 
- Run `make init` to create systolic info based off of the benchmark blif file.
- Run `make pysim` to run a Python behavioral simulation of the systolic placer, and validate the trace.
- Run `make rtl` to create the RTL for the systolic placer and the testbench.
- Run `make bit` to create the bitstream for the RTL simulation or Versal accelerator.
- Run `make rtlsim` to run the RTL simulation of the systolic placer, and validate the trace.
- Run `make diff_trace` to compare the trace files between the behavioral simulation and the RTL simulation.
- Run `make route pysim` to route the design placed by the behavioral simulator.
- Run `make route rtlsim` to route the design placed by the RTL simulator.
- Run `make vtr` to place and route the benchmark blif with VTR.

## Scripts
The diagram below indicates which files a script takes in, and which files are produced as outputs.


![workflow](resources/workflow_3.png)

## VTR Integration
Currently uses VTR commit: a632849110cf2dfea3d126993dbf46f010c84072

## License

This project is licensed under the MIT License.

It includes third-party code released under the MIT License by their respective authors. See source file headers for details.
