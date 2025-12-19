import subprocess
################################################################################################
def shell(command,silent=False,capture=False):
    output = subprocess.run(command,shell=True,capture_output=capture,text=True)
    if not silent and output.stdout:
        print(output.stdout,end="")
    return output
################################################################################################