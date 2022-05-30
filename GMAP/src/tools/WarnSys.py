import sys


def Warning(message, exitbool=False):
    print(prettifier(message))
    if exitbool:
        sys.exit()


def prettifier(str, deslen=79):
    startlst = str.split("\n")
    endlst = []

    for item in startlst:
        if len(item) > deslen:
            itemlst = item.split(" ")
            buildstr = ""
            for subitem in itemlst:
                if len(buildstr) + len(subitem) >= deslen:
                    endlst.append(buildstr)
                    buildstr = subitem
                else:
                    if len(buildstr) == 0:
                        buildstr = subitem
                    else:
                        buildstr += " " + subitem
            endlst.append(buildstr)
        else:
            endlst.append(item)

    return "\n".join(endlst)
