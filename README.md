# systolic_page_placer

## Makefile

- Run `make init` to create systolic info based off of a benchmark blif file.
- Run `make pysim` to run a Python behavioral simulation of the systolic placer, and validate the trace.
- Run `make rtl` to create the RTL for the systolic placer and the testbench.
- Run `make rtlsim` to run the RTL simulation of the systolic placer, and validate the trace.
- Run `make diff` to compare the trace files between the behavioral simulation and the RTL simulation.
- Run `make route pysim` to route the design placed by the behavioral simulator.
- Run `make route rtlsim` to route the design placed by the RTL simulator.
- Run `make vtr` to place and route the benchmark blif with VTR.

## Scripts
The diagram below indicates which files a script takes in, and which files are produced as outputs.


![workflow](resources/workflow_3.png)

## VTR Integration
Currently uses VTR commit: a632849110cf2dfea3d126993dbf46f010c84072

