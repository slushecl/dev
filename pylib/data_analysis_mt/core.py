#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# module imports
import os, sys, re, argparse, time, os.path as path, numpy as np
from math import ceil, floor

def moving_average(x, n, t='simple'):
    """Compute an n period moving aving average.
    Type can be 'simple' or 'exponential'
    """
    x = np.asarray(x)
    if t != 'exponential':
        weights = np.exp(np.linspace(-1., 0., n))
    else:
        weights = np.ones(n)
    weights /= weights.sum()
    a = np.convolve(x, weights, mode='full')[:len(x)]
    ma = a[n:]
    return ma

def path_split(fp):
    #fplst = str(path.split(str(fp))[0]).split('/')
    patterns = re.compile(r"""/
    (?P<model>mt)/
    (?P<direction>pulling)/
    (?P<tail>noctt|ctt)/
    (?P<protein1>[ab])(?=[0-9][0-9])
    (?<=[ab])(?P<residue1>[0-9][0-9])
    (?<=[ab][0-9][0-9])?(?P<protein2>[ab])?(?=[0-9][0-9])?
    (?<=[ab][0-9][0-9][ab])?(?P<residue2>[0-9][0-9])?/?
    (?P<method>single)?/?
    run?(?P<runnum>[0-9])?/?""", flags=re.X)
    matches = re.search(patterns, fp)
    reslst, protlst = [], []
    if matches:
        dct = matches.groupdict()
        for k, v in sorted(dct.copy().items()):
                # if not v:
                #     del dct[k]
            if v: # Checks that the value evaluates True / is not None (False)
                if k == 'model':
                    if v == 'mt':
                        dct[k] = 'Microtubule'
                if k == 'force':
                    if v == 'pulling':
                        dct[k] = 'Pulling'
                if k == 'tail':
                    if v == 'noctt':
                        dct[k] = 'Without CTT'
                    if v == 'ctt':
                        dct[k] = 'With CTT'
                if 'protein' in k:
                    if v == 'a':
                        dct[k] = 'Alpha'
                    if v == 'b':
                        dct[k] = 'Beta'
                    protlst.append(dct[k])
                if k == 'method':
                    if v == 'single':
                        dct[k] = 'Single Point'
                if 'residue' in k:
                    dct[k] = 'Residue ' + v
                    reslst.append(dct[k])
                if k == 'runnum':
                    dct[k] = 'Run ' + v
        dct['prots'] = ', '.join(['{} {}'.format(a, reslst[i]) \
                                  for i, a in enumerate(protlst)])
        #for val in dct.items():
        #    print(val)
        return dct

def dimensions(n=1):
    k = 1
    while n > k**2:
        k += 1
    j = k
    if ceil((n+n%2)/k) == k-1:
        j -= 1
    return (j, k)

class FindFiles():
    """The Locator of files
    """
    def __init__(self, **kwargs):
        """Initializes the FindFiles class' global variables values to None."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, 'lst'):
            self.lst = []
        if not hasattr(self, 'dirs'):
            self.dirs = []
        if not hasattr(self, 'ftypes'):
            self.ftypes = []
        if not hasattr(self, 'rmpats'):
            self.rmpats = []
        if not hasattr(self, 'uniqdirs'):
            self.uniqdirs = []
        self.parse()
        self.find()
        self.remove()
        self.sort()

    def find(self): # , dirs=[], ftypes=[]):
        """\
        Finds all files which are within the indicated directories.  Defaults to
        the current directory.
        """
        fileslist, ftypes = self.lst, self.ftypes
        dirs = [d1 for d1 in [path.abspath(path.expanduser(str(d0))) \
                              for d0 in self.dirs[:]] if path.exists(d1)]
        for directory in dirs:
            for rootdir, subdirs, files in os.walk(directory):
                for subd in subdirs[:]:
                    if 'common' in subd or 'fail' in subd or 'example' in subd:
                        subdirs.remove(subd)
                for vfile in files[:]:
                    if 'fail' in vfile or 'part' in vfile or 'bad' in vfile:
                        files.remove(vfile)
                for vfile in files:
                    for n, ftype in enumerate(ftypes[:]):
                        self.ftypes[n] = ftype.strip().lstrip('*.')
                        if ftype == '*' and \
                           path.join(rootdir, vfile) not in fileslist:
                            fileslist.append(path.join(rootdir, vfile))
                        # if ftype.startswith('*'):
                        #     ftype.lstrip('*')
                        # if ftype.startswith('.'):
                        #     ftype = '.' + ftype
                        if vfile.endswith(ftype) and path.join(rootdir, vfile) not in fileslist:
                            fileslist.append(path.join(rootdir, vfile))
        self.lst = fileslist

    # def info(self):
    #     """/
    #     Prints the current files which are stored in 'self.lst'.
    #     """
    #     lst = self.lst
    #     for item in lst:
    #         print(item)

    # def refine(self, pats=[], bydir=True):
    #     """\
    #     """
    #     lst, fileslist = self.lst, []
    #     if hasattr(self, 'pats'):
    #         pats = self.pats
    #     if hasattr(self, 'bydir'):
    #         bydir = self.bydir
    #     for pat in pats:
    #         pat = str(pat).strip()
    #         for f in lst[:]:
    #             f = str(f).strip()
    #             if bydir == True:
    #                 if pat in path.dirname(f) and f not in fileslist:
    #                     fileslist.append(f)
    #             elif bydir == False:
    #                 if pat in path.basename(f) and f not in fileslist:
    #                     fileslist.append(f)
    #             else:
    #                 self.lst = lst
    #                 print("Option bydir must evaluate to True or False.")
    #     if len(fileslist) < 1:
    #         if len(self.lst) > 0:
    #             print('No matches found. Retaining current file list.')
    #         else: # Occurs when no files matched & current file list is empty
    #             self.lst = []
    #     else: # Occurs when at least 1 file has been matched
    #         self.lst = fileslist

    def remove(self):
        lst, rmpats = self.lst, self.rmpats
        for rmpat in rmpats:
            for item in lst[:]:
                if re.search(str(rmpat), str(item)) != None:
                   lst.remove(item)
        self.lst = lst

    def sort(self):
        # 'self.lst' contains a list of path names to match. 'fts' is the list
        # of file types to use for matching.
        l = self.lst
        m = re.compile(r'(.*/run[0-9])/?(.*).*')
        c = path.commonpath(l)
        dctslst = [{'type': path.splitext(p)[1][1:], 'path': p, \
            'root': re.search(m, path.dirname(p.replace(c, '', 1))).group(1), \
            'dir': re.search(m, path.dirname(p.replace(c, '', 1))).group(2)} \
            for p in l]
        uniq = [{'uname': 'dir' + str(n), 'uid': u} \
                for n, u in enumerate({d['root'] for d in dctslst})]
        for vals in uniq:
            if not hasattr(self, vals['uname']):
                setattr(self, vals['uname'], [])
                self.uniqdirs.append([vals['uname'], vals['uid']])
            tmpattr = getattr(self, vals['uname'])
            for dct in dctslst:
                if dct['root'] == vals['uid']:
                    tmpattr.append(dct)
            setattr(self, vals['uname'], tmpattr)

        # fpsuniq = {d['id'] for d in dctslst}
        # fpdctlst = [{n : {k : v for k, v in d.items()} for d in dctslst if d['id']==f} for n, f in enumerate(fpsuniq)]
        # for q in fpdctlst:
        #     print(q)

        # dctslst = [{'type': t, 'path': p, \
        #  'id': re.search(m, path.dirname(p.replace(c, '', 1))).group(1), \
        #  'dir': re.search(m, path.dirname(p.replace(c, '', 1))).group(2)} \
        #  for t in fts for p in l if p.endswith(t)]
        # idlst = [{d['type'] : {'path': d['path'], 'dir': d['dir']} \
        #          for d in dctslst if d['dir'] != b['dir'] if d['id'] == b['id']} for b in dctslst]
        # fpdctlst = []
        # for info in fpdctlst:
        #    while info not in fpdctlst and len(info) == len(fts):
        #        fpdctlst.append(info)
        # self.lst = idlst

    def parse(self):
        """Parses arguments
        """
        parser = argparse.ArgumentParser(formatter_class = \
                                         argparse.RawTextHelpFormatter)
        parser.add_argument('-d', '--dirs',
                            help='''\
Recursively searches within indicated directory or
directories.
Default Value: ./''',
                            nargs='*',
                            type=str,
                            default=['.'],
                            dest='dirs')
        parser.add_argument('-f', '--filetypes',
                            help='''\
Matches against indicated file endings.
Default Value: dat, sop''',
                            nargs='*',
                            type=str,
                            default=['dat', 'sop'],
                            dest='ftypes')
#        parser.add_argument('-S', '--searchstrings',
#                            help='''\
# Matches string(s) against files' path names excluding
# file base names, returning any files which contain any
# listed string, and which fit all other restraints, in
# absence of the '-b' flag.  If the '-b' flag is present
# then the listed string(s) are tested against file base
# names excluding the rest of the files' paths.  If no
# files are found this flag does nothing.
# Default Value: ""''',
#                             nargs='*',
#                             type=str,
#                             default=[''],
#                             dest='pats')
        parser.add_argument('-R', '--removefile',
                            help='''\
Removes specified file path from the file list.
Default Value: ""''',
                            nargs='*',
                            type=str,
                            default=['/dat/'],
                            dest='rmpats')
        parser.add_argument('-x', '--xvar',
                            help="""\
Indicates variable to plot on the X-axis.
Default Value: time""",
                            choices=['timepico', 'timenano', 'timemicro', \
                                     'timemilli', 'forcepico', 'forcenano', \
                                     'frame', 'extension', 'endtoend'],
                            nargs='?', # '*',
                            type=str,
                            default='timenano',
                            dest='xvar')
        parser.add_argument('-y', '--yvar',
                            help="""\
Indicates variable to plot on the Y-axis.
Default Value: force""",
                            choices=['timepico', 'timenano', 'timemicro', \
                                     'timemilli', 'forcepico', 'forcenano', \
                                     'frame', 'extension', 'endtoend'],
                            nargs='?', # '*',
                            type=str,
                            default='forcenano',
                            dest='yvar')
        parser.add_argument('-m', '--ma',
                            help="""\
Indicates the rang of data over which a simple moving
average of the data should be taken.
Default value: 1000""",
                            nargs='?',
                            const=1000,
                            default=1000,
                            type=int,
                            dest='ma')
        parser.add_argument("-b", "-begin",
                            help="""\
Indicates the start frame for data visualization. Negative
values indicate how frames before the stop frame to set the
start frame. Positive and zero values indicate how many
frames after the first frame to set the start frame. Frame
number for the start frame must be less than that of the
stop frame.
Default Value: 0""",
                            nargs='?',
                            const=9E12,
                            default=9E12,
                            type=int,
                            dest='start')
        parser.add_argument("-e", "--end",
                            help="""\
Indicates the stop frame for data visualization.  If the number of total frames
is less than the value indicated then the this option is considered to be equal
to the number of frames. Negative values indicate how many frames before the
final frame to set the stop frame. Positive and zero values indicate how many
frames after the first frame to set the start frame. Frame number of the stop
frame must be greater than that of the start frame.
Default Value: -1""",
                            nargs='?',
                            const=9E12,
                            default=9E12,
                            type=int,
                            dest="stop")
        parser.add_argument('-o', '--overlay',
                            help='''\
Flag indicating that the figure should overlay each plot onto the same figure.
Can be used up to two times. The first use indicates that only plots with the
same y-axis and x-axis should be overlaid. The second indicates that all plots
should be overlaid.''',
                            action='count',
                            default=0,
                            dest='overlay')
        parser.add_argument('-P', '--noplot',
                            help='''\
Flag indicating that the created plot should not be shown.''',
                            action='store_true',
                            dest='plotbool')
        #args = parser.parse_args()
        for key, val in vars(parser.parse_args()).items(): #args._get_kwargs():
            setattr(self, key, val)



# class Plotter():
#     """\
#     Data Plotting / Processing Class
#     """
#     def __init__(self, **kwargs):
#         """\
# Initialization of key parameters.
#         --> start
#         --> stop
#         --> ma

#         plot = Plotter()
#         """
#         # Assigns each variable it's value
#         for key, value in kwargs.items():
#             setattr(self, key, value)

#     def print_class(self):
#         for key in dir(self):
#             print(key, getattr(self, key))

#     def load_data(self, dct=dict(), **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#         for value in dct.values():
#             print(value)
#             if value['type'] == 'dat' and value['dir'] == 'pull':
#                 pth = value['path']
#                 pthnpy = pth.replace('.dat', '.npy', 1)
#                 print("""\
# ================================================
# =======  Force vs. Extension/Time/Frame  =======
# ================================================
# DAT File:\t{0}
# DAT: time last modified:\t{1!s}
# NPY File:\t{2}""".format(pth, time.ctime(path.getmtime(pth)), pthnpy))
#                 try:
#                     print("""\
# NPY: time last modified:\t{}""".format(time.ctime(path.getmtime(pthnpy))))
#                     if path.getmtime(pth) <= path.getmtime(pthnpy):
#                         print('DATFILE: is older than npy... Continue.')
#                     else:
#                         print('DATFILE: is newer than npy... Remaking.')
#                         os.remove(pthnpy)
#                 except OSError:
#                     pass
#                 if path.exists(pthnpy):
#                     dat = np.load(pthnpy)
#                 else:
#                     dat = np.loadtxt(pth)
#                     np.save(pthnpy, dat)
#                 print(dat.shape)
#         for value in dct.values():
#             if value['type'] == 'sop':
#                 pth = value['path']
#                 with open(pth) as fp:
#                     for line in fp:
#                         if '#' in line:
#                             line = line[:line.find('#')]
#                         lst = line.strip().split(maxsplit=1)
#                         if len(lst) == 2:
#                             setattr(self, lst[0], lst[1])
#                 print("""\
# SOP File:\t{}
#         """.format(pth))
#                 if hasattr(self, 'timestep'):
#                     self.timestep = float(self.timestep)
#                 if hasattr(self, 'nav'):
#                     self.nav = int(self.nav)
#                 if hasattr(self, 'dcdfreq'):
#                     self.dcdfreq = int(self.dcdfreq)
#                 if hasattr(self, 'ma'):
#                     self.ma = int(self.ma)
#                 if not hasattr(self, 'step'):
#                     self.step = int(self.ma) // int(self.nav)
#                     if self.step < 1:
#                         self.step = 1
#                 col0 = dat[::, 0]
#                 col1 = dat[::, 1]
#                 col2 = dat[::, 2]
#                 col3 = dat[::, 3]
#                 nlines = len(col0)
#                 #frame_last = len(col0) * self.step / self.dcdfreq / self.nav
#                 if self.start != None:
#                     self.start *= self.dcdfreq / self.nav
#                     if self.start >= nlines:
#                         return
#                 if self.stop != None:
#                     self.stop *= self.dcdfreq / self.nav
#                     if self.stop >= nlines:
#                         return
#                 if self.start == None:
#                     self.start = 0.0
#                 if self.stop == None:
#                     self.stop = nlines
#                 if self.start < 0.0: # if start negative
#                     self.start += nlines
#                 if self.stop <= 0.0: # if stop negative
#                     self.stop += nlines
#                 if self.start >= self.stop: # if start more than or equal to stop
#                     return
#                 if self.start < 0.0: # if start less than zero
#                     self.start = 0.0
#                 if self.start >= nlines: # if start more than line count
#                     self.start = nlines - self.ma
#                 if self.stop <= 0.0: # if stop less than or equal to zero
#                     self.stop = self.ma
#                 if self.stop > nlines: # if stop more than line count
#                     self.stop = nlines
#                 self.start = floor(self.start)
#                 self.stop = ceil(self.stop)
#                 nsteps = self.stop - self.start
#                 startframe = self.start / self.dcdfreq * self.nav
#                 stopframe = self.stop / self.dcdfreq * self.nav
#                 e_to_e = dat[self.start:self.stop:self.step, 2] * 0.1 # A > nm
#                 ext_raw = e_to_e - col2[0] * 0.1
#                 ext = moving_average(ext_raw, self.ma)
#                 size_arr = len(e_to_e) - self.ma
#                 f_raw = dat[self.start:self.stop:self.step, 3] # kcal/(mol*A)
#                 f70 = f_raw * 70.0 # kcal/(mol*A) > pN
#                 fma = moving_average(f_raw, self.ma) # kcal/(mol*A)
#                 fpico = fma * 70.0 # pN
#                 fnano = fma * 0.07 # nN
#                 starttimeps = self.timestep * self.start * self.nav / self.step
#                 starttimens = starttimeps / 1E3
#                 starttimeus = starttimens / 1E3
#                 starttimems = starttimeus / 1E3
#                 stoptimeps = self.timestep * self.stop * self.nav / self.step
#                 stoptimens = stoptimeps / 1E3
#                 stoptimeus = stoptimens / 1E3
#                 stoptimems = stoptimeus / 1E3
#                 time_array = np.linspace(starttimems, stoptimems, size_arr)
#                 frame = np.linspace(startframe, stopframe, size_arr)
#                 if len(frame) > 1:
#                     nframes = max(frame) - min(frame)
#                 else:
#                     nframes = 0.0
#                 print("""\
# Extension/Force:
#     End to End:\t{1}\t{2}
#     Extension:\t{3}\t{4}
#     Distance:\t{5}
#     Force:\t{6} points of which the max is "{7}"
#     Max Force (pN):\t{8}
#     Max Force (nN):\t{9}
# Frames:
#     Step:\t{10}
#     nav:\t{11}
#     Dcdfreq:\t{12}
#     Output Timing:\t{13}
#     Data Points:\t{14}
#     Column 1:\t{15}\t{16}
#     Total Steps:\t{17}
#     Last Frame:\t{18}
#     Frame {19}, ..., {20}  ({21} total frames)
# Time:
#     Time (ms):\t{22}, ..., {23}
#     Time Array:\t{24}
#     Total Time Points:\t{25}
#     Array Size:\t{26}
# ================================================
# ================================================



# """.format(pth, e_to_e[0], e_to_e[-1], ext[0], ext[-1], ext[-1] - ext[0], \
#            len(f_raw), max(f_raw), max(fpico), max(fnano), self.step, \
#            self.nav, self.dcdfreq, self.outputtiming, len(e_to_e), col0[0], \
#            col0[-1], nsteps, nframes, frame[0], frame[-1], nframes, \
#            starttimems, stoptimems, time_array, len(time_array), size_arr))

#                 self.pth = pth
#                 self.data = dat
#                 self.f_raw = f_raw
#                 self.f70 = f70
#                 self.force = fpico
#                 self.endtoend = e_to_e
#                 self.ext_raw = ext_raw
#                 self.ext = ext
#                 self.extension = ext
#                 self.time = time_array
#                 self.time_array_ms = time_array
#                 self.frame = frame

#                 return 0


class FileReader():
    """\
Reads in information from files and stores it in attributes. Currently supports
.dat & .sop file types."""

    def sopread(self):
        """\
Reads Sop formatted files in line by line. Arguments should be lists."""
        for vals in self.files:
            if vals['type'] == 'sop':
                with open(vals['path']) as filepath:
                    self.sopcheck = True
                    for line in filepath:
                        if '#' in line:
                            line = line[:line.find('#')]
                        lst = line.strip().split(maxsplit=1)
                        if len(lst) == 2:
                            setattr(self, str(lst[0]).lower(), lst[1])


# class DatReader():
#     """\
# Stores data extracted from .dat or .npy files for plotting & calculations."""
    def __init__(self, files, finder, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.files = files
        # if finder is FindFiles:
        self.finder = finder
        self.datcheck = False
        self.sopcheck = False
        self.dat = None
        self.datfileloc = None

        self.datread()
        self.sopread()

        if hasattr(self, 'timestep'):
            self.timestep = float(self.timestep)
        if hasattr(self, 'nav'):
            self.nav = int(self.nav)
        if hasattr(self, 'dcdfreq'):
            self.dcdfreq = int(self.dcdfreq)
        if hasattr(self, 'ma'):
            self.ma = int(self.ma)
        elif hasattr(self, 'finder'):
            self.ma = int(self.finder.ma)
        else:
            self.ma = int(1E3)
        self.maframe = int(self.ma*self.dcdfreq/self.nav)
        if not hasattr(self, 'step'):
            self.step = int(self.ma) // int(self.nav)
            if self.step < 1:
                self.step = 1

    def datread(self):
        """\
Reads in data from .dat or .npy file paths and if .dat is newer than .npy saves
it in .npy format for faster reading in future."""
        for vals in self.files:
            if vals['type'] == 'dat' and vals['dir'] == 'pull':
                # self.datfileloc = vals['dir']
                pth = vals['path']
                pthnpy = pth.replace('.dat', '.npy', 1)
                try:
                    print("""\
DAT File:\t{0}
DAT: time last modified:\t{2}
NPY File:\t{1}
NPY: time last modified:\t{3}""".format(pth, pthnpy, \
                                        time.ctime(path.getmtime(pth)), \
                                        time.ctime(path.getmtime(pthnpy))))
                    if path.getmtime(pth) <= path.getmtime(pthnpy):
                        print('DATFILE: is older than npy... Continue.\n')
                    else:
                        print('DATFILE: is newer than npy... Remaking.\n')
                        os.remove(pthnpy)
                except OSError:
                    pass
                if vals['dir'] == 'pull':
                    self.datcheck = True
                    self.path = pth
                    if path.exists(pthnpy):
                        self.dat = np.load(pthnpy)
                    else:
                        self.dat = np.loadtxt(pth)
                        np.save(pthnpy, self.dat)
