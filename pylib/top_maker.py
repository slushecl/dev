# file: top_maker_v1.py
# description: Topology file maker
# by: Craig Slusher

import fileinput, numpy as np, sys

class Redirect:
    """Redirects print output so as to have the output written to a file"""
 
    def __init__(self, out_new):
        self.out_new = out_new
 
    def __enter__(self):
        self.out_old = sys.stdout
        sys.stdout = self.out_new
 
    def __exit__(self, *args):
        sys.stdout = self.out_old  

top_path = "/home/slushecl/projects/compare/nan_orig/MT.top"
out_path = "/home/slushecl/projects/compare/new_MT.top"

with open(top_path, mode='r') as mt_file, open(out_path, mode='w') as out_file, Redirect(out_file):
    for line in mt_file:
        if "native" not in line:
            print(line, end="")
        else:
            print("[ native ]\n;  ai    aj funct\tc0\tc1\tc2\tc3\n")
            break
    array1 = np.loadtxt(mt_file, skiprows=1)
    array1 = array1.tolist()
    for val in array1:
        val[0] = int(val[0])
        val[1] = int(val[1])
        val[2] = int(val[2])
        x = val[0] // 866
        y = val[1] // 866
        if (y - x) == 0:
            val.append(1.9)
        elif (((y - x) == 12) or ((y -x) == 13) or ((y -x) == 14)):
            val.append(1.0)
        elif (y-x) == 1:
            val.append(0.9)
        else:
            val.append(0.9)
        print( val[0], val[1], val[2], '% 8.5f' % val[3], '% 8.5f' % val[4], sep ='\t')
