import argparse
import log
############################################################################################################################
def make_arch(width,height,template,output):
    width = str(int(width) + 2)
    height = str(int(height) + 2)
    with open(template,"r") as t:
        with open(output,"w") as o:
            for line in t:
                o.write(line.replace("systolic_width",width).replace("systolic_height",height))
############################################################################################################################
def main():

    description = 'Generates a VTR arch'
    p = argparse.ArgumentParser(description = description)
    p.add_argument("width",help="The width of the arch")
    p.add_argument("height", help="The height of the arch")
    p.add_argument("template",help="Arch template file to load")
    p.add_argument("output",help="Arch output file to write")

    args = p.parse_args()
    make_arch(args.width,args.height,args.template,args.output)
    log.blue("[Created Arch File]")
############################################################################################################################
if __name__ == "__main__":
    main()