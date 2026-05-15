import argparse
import log


def runlength_compress(input_file, output_file):
    uncompressed_words = 0
    compressed_runs = 0

    with open(input_file, "r") as in_f, open(output_file, "w") as out_f:
        # process the header
        header = in_f.readline().strip()
        packet_length = int(header,16) + 8
        out_f.write(f"1\n{header}\n")
        uncompressed_words += 1
        compressed_runs += 1


        previous_word = None
        run_length = 0
        process_length = 0

        for line in in_f:
            word = line.strip()

            # skip if word is empty
            if word == "":
                continue

            # increment stuff
            process_length += 1
            uncompressed_words += 1

            if process_length == packet_length + 1:
                out_f.write(f"{hex(run_length)[2:]}\n{previous_word}\n")
                compressed_runs += 1
                previous_word = word
                run_length = 1
                process_length = 1

            else:
                if word == previous_word:
                    run_length += 1
                else:
                    if previous_word is None:
                        previous_word = word
                        run_length = 1
                    else:
                        out_f.write(f"{hex(run_length)[2:]}\n{previous_word}\n")
                        compressed_runs += 1
                        previous_word = word
                        run_length = 1

        if previous_word is not None:
            out_f.write(f"{hex(run_length)[2:]}\n{previous_word}\n")
            compressed_runs += 1

    return uncompressed_words, compressed_runs


def main():

    description = "Run-length compresses a bitstream file"
    p = argparse.ArgumentParser(description = description)
    p.add_argument("bitstream",help="bitstream to compress")
    p.add_argument("compressed_bitstream",help="compressed bitstream")
    args = p.parse_args()

    uncompressed_words, compressed_runs = runlength_compress(args.bitstream, args.compressed_bitstream)
    log.green(f"[Compressed bitstream to {int((compressed_runs*2)/uncompressed_words*100)}%]")


if __name__ == "__main__":
    main()