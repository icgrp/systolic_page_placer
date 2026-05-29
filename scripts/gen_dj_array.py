import argparse
####################################################################################
def gen_systolic_grid_info(w,h,file_name):

    with open(file_name,"w") as f:

        f.write(f"{h} by {w}\n")
        f.write(f"type\tcx\tcy\tx\ty\n")
        for x in range(w):
            for y in range(h):
                f.write(f"clb\t\t{x}\t{y}\t{x+1}\t{y+1}\n")
####################################################################################
def main():

    description = "Creates a simple monolithic systolic_grid_info file"
    p = argparse.ArgumentParser(description = description)
    p.add_argument("width",help="width of array")
    p.add_argument("height",help="height of array")
    p.add_argument("systolic_grid_info",help="file to generate")
    args = p.parse_args()

    gen_systolic_grid_info(int(args.width),int(args.height),args.systolic_grid_info)

####################################################################################
if __name__ == "__main__":
    main()