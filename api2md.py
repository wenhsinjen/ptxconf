#! /usr/bin/python3

import pdoc
import sys
import os

modpath = os.path.dirname(os.path.abspath(sys.argv[1]))
modname = os.path.basename(sys.argv[1]).split(".py")[0]

sys.path.append(modpath)
pdoc.import_path.append(modpath)

md = []
for line in pdoc.text(modname).split('\n'):
    md.append(line)
md.append("")

for i, line in enumerate(md):
    if i > len(md) - 2: break
    # first level headings
    if "----" == md[i + 1][0:4]:
        print("#" + line)

    # first level definitions class names / functions
    elif line != "" and "    " != line[0:4] and "----" != line[0:4] and "----" != md[i + 1][0:4]:
        print("##" + line)

    elif "    " == line[0:4] and "----" in md[i + 1][4:8]:
        print("###" + line[4:])
    # methods
    elif "(self" in line:
        print("####" + line[4:])
    # plain text/members
    elif line != "" and "    " == line[0:4] and "----" not in line:
        print(line[4:].strip())
