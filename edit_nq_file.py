import re

regex = re.compile(fr'\d*[.][0-9]+(")...(http://www.w3.org/2001/XMLSchema#integer)')
regex2 = re.compile(fr'T3+(")...(http://www.w3.org/2001/XMLSchema#integer)')
regex3 = re.compile(fr'0t+(")...(http://www.w3.org/2001/XMLSchema#integer)')

n = 0
with open("rinferatv-aggregate-202210261513.nq", "r", encoding="utf8") as input:
    with open("filtered-rinferatv.nq", "w", encoding="utf8") as output:
        # iterate all lines from file
        for line in input:
            result = regex.search(line)
            result2 = regex2.search(line)
            result3 = regex3.search(line)
            # if text matches then don't write it
            if result is None and result2 is None and result3 is None:
                output.write(line)
            else:
                print("Error found at line: "+str(n)+" // "+str(line))
            n = n+1
