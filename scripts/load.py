import argparse
import serial
import time
import log
###########################################################################
def main():

    description = 'Loads bitstream onto placer and retrieves completed placement'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("bitstream",help="bitstream.txt file to load")
    p.add_argument("unload",help="unloaded placement file to write")
    args = p.parse_args()

    placement = []

    ser = serial.Serial('/dev/ttyUSB1',115200)
    ser.reset_input_buffer()

    # Indicate the loader is ready
    ser.write(b'\n')

    with open(args.bitstream,'r') as f:
        
        # Read parameter N from the bitstream header
        N = int(f.readline(),16)
        NUM_OF_PACKETS = N + 2
        PACKET_LENGTH = 8 + N

        log.blue("[Loading placer]")

        packet_counter = 0
        while(1):
            
            # Wait for packet request
            request = ser.readline()

            for x in range(PACKET_LENGTH):
                line = f.readline()
                ser.write(str.encode(line))
                #time.sleep(0.01)

            packet_counter += 1
            log.magenta("[Finished loading packet {}]".format(packet_counter))
            if(packet_counter == NUM_OF_PACKETS):
                log.blue("[Running placement]")
                break

    log.blue("[Reading placement]")
    for x in range(N):
        blk_id = ser.readline()
        blk_id = blk_id.decode()
        placement.append(blk_id)

    log.green("[Finished reading placement]")

    with open(args.unload,'w') as f:
        for blk_id in placement:
            f.write(blk_id)

    log.blue("[Wrote unloaded data to file]")
###########################################################################
if __name__ == "__main__":
    main()