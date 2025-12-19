def red(string="",end="\n"):
    print("\u001b[31m" + string + "\u001b[0m",end=end)

def green(string="",end="\n"):
    print("\u001b[32m" + string + "\u001b[0m",end=end)

def blue(string="",end="\n"):
    print("\033[0;34m" + string + "\u001b[0m",end=end)

def magenta(string="",end="\n"):
    print("\u001b[35m" + string + "\u001b[0m",end=end)

def yellow(string="",end="\n"):
    print("\u001b[33m" + string + "\u001b[0m",end=end)