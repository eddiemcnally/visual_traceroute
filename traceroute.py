__author__ = 'eddie'



def parse_traceroute_output(output):
    lines = output.split("\n")

    cleaned = []

    for l in lines:
        if l.startswith("traceroute") is False:
            tempstr = l.split(" ")
            if len(tempstr) >= 4:
                if tempstr[3] != "*":
                    cleaned.append(l)

    retval = []
    for route in cleaned:
        tmpstr = route.split()
        ## print (tmpstr[1])
        ip = tmpstr[2]
        ip = ip.replace("(", "")
        ip = ip.replace(")", "")
        retval.append(ip)

    ## remove first IP address (won't be public)
    retval.pop(0)
    return retval
