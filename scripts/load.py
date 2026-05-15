import argparse
import serial
from calc_runtime import compute_runtime
import time
import log
###########################################################################
def main():

    description = 'Loads bitstream onto placer and retrieves completed placement'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("bitstream",help="bitstream.txt file to load")
    p.add_argument("unload",help="unloaded placement file to write")
    p.add_argument("placer_params",help="placer_params file")
    p.add_argument("num_of_updates",help="num_of_updates")
    p.add_argument("swaps_per_update",help="swaps_per_update")
    p.add_argument("frequency",help="frequency_of_placer")
    args = p.parse_args()

    placement = []

    ser = serial.Serial('/dev/ttyUSB1',115200)
    ser.reset_input_buffer()

    # Indicate the loader is ready
    ser.write(b'\n')

    with open(args.bitstream,'r') as f:
        
        # Read parameter N from the bitstream header
        f.readline() # get rid of the header run_length
        N = int(f.readline(),16)
        NUM_OF_PACKETS = N + 2
        PACKET_LENGTH = 8 + N

        log.blue("[Loading placer]")
        start_load_time = time.perf_counter()

        packet_counter = 0
        read_count = 2
        while(1):
            
            # Wait for packet request
            request = ser.readline()

            # send the packet
            sent_size = 0
            while(1):
                run_length = f.readline()
                val = f.readline()
                read_count += 2
                
                ser.write(str.encode(run_length))
                ser.write(str.encode(val))

                sent_size += int(run_length,16)
                if(sent_size == PACKET_LENGTH):
                    break

            packet_counter += 1
            end_load_time = time.perf_counter()
            log.magenta("[Finished loading packet {}]".format(packet_counter))

            if(packet_counter == NUM_OF_PACKETS):
                log.blue("[Running placement]")
                break

    log.blue("[Reading placement]")
    start_read_time = time.perf_counter()
    for x in range(N):
        blk_id = ser.readline()
        blk_id = blk_id.decode()
        placement.append(blk_id)
    end_read_time = time.perf_counter()
    log.green("[Finished reading placement]")

    runtime = compute_runtime(args.placer_params,
                          int(args.num_of_updates),
                          int(args.swaps_per_update),
                          int(args.frequency))

    log.yellow(f"[Loading Time: {(end_load_time - start_load_time):.4f} (seconds)]")
    log.yellow(f"[Compute Time: {runtime:.6f} (seconds)]")
    log.yellow(f"[Read Time: {(end_read_time - start_read_time):.4f} (seconds)]")

    with open(args.unload,'w') as f:
        for blk_id in placement:
            f.write(blk_id)

    log.blue("[Wrote unloaded data to file]")
###########################################################################
if __name__ == "__main__":
    main()