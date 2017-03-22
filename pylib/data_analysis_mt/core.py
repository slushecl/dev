#!/home/slushecl/dev/pylib/python3.5/bin/python3
# -*- coding: utf-8 -*-

# module imports
import os, sys, re, glob, time, argparse, os.path as path, numpy as np

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

class FindFiles():
    """The Locator of files
    """
    def __init__(self):
        """Initializes the FindFiles class' global variables values to None."""
        self.lst = []

    def find(self, dirs=[], ftypes=[]):
        """\
        Finds all files of the types indicated which are within the indicated
        directories.  Defaults to '.dat' file types and the current directory.
        """
        fileslist = []
        if hasattr(self, 'dirs'):
            dirs = self.dirs
        if hasattr(self, 'ftypes'):
            ftypes = self.ftypes
        for d in dirs:
            d = path.abspath(path.expanduser(str(d)))
            if path.exists(d):
                for rootdir, subdirs, files in os.walk(d):
                    for d in subdirs[:]:
                        if 'common' in d or 'fail' in d or 'example' in d:
                            subdirs.remove(d)
                    for f in files[:]:
                        if 'fail' in f or 'part' in f or 'bad' in f:
                            files.remove(f)
                    for f in files:
                        for ftype in ftypes:
                            ftype = ftype.strip()
                            if ftype == '*' and \
                               path.join(rootdir, f) not in fileslist:
                                filelist.append(path.join(rootdir, f))
                            if ftype.startswith('*'):
                                ftype.lstrip('*')
                            if not ftype.startswith('.'):
                                ftype = '.' + ftype
                            if path.splitext(f)[1] == ftype and \
                               path.join(rootdir, f) not in fileslist:
                                fileslist.append(path.join(rootdir, f))
        self.lst = fileslist

    def info(self):
        """/
        Prints the current files which are stored in 'self.lst'.
        """
        lst = self.lst
        for item in lst:
            print(item)

    def refine(self, pats=[], bydir=True):
        """\
        """
        lst, fileslist = self.lst, []
        if hasattr(self, 'pats'):
            pats = self.pats
        if hasattr(self, 'bydir'):
            bydir = self.bydir
        for pat in pats:
            pat = str(pat).strip()
            for f in lst[:]:
                f = str(f).strip()
                if bydir == True:
                    if pat in path.dirname(f) and f not in fileslist:
                        fileslist.append(f)
                elif bydir == False:
                    if pat in path.basename(f) and f not in fileslist:
                        fileslist.append(f)
                else:
                    self.lst = lst
                    print("Option bydir must evaluate to True or False.")
        if len(fileslist) < 1:
            if len(self.lst) > 0:
                print('No matches found. Retaining current file list.')
            else: # Occurs when no files matched & current file list is empty
                self.lst = []
        else: # Occurs when at least 1 file has been matched
            self.lst = fileslist

    def remove(self, rmpats=[]):
        lst = self.lst
        if hasattr(self, 'rmpats'):
            rmpats = self.rmpats
        for rmpat in rmpats:
            for item in lst[:]:
                if re.search(str(rmpat), str(item)) != None:
                   lst.remove(item)
        self.lst = lst

    def sort(self):
        lst = self.lst
        dctlst, datlst, soplst = [], [], []
        for pth in lst:
            if pth.endswith('.dat'):
                datlst.append(pth)
            if pth.endswith('.sop'):
                soplst.append(pth)
        for sopp in soplst:
            for datp in datlst:
                if 'run' not in path.relpath(datp, start=path.split(sopp)[0]):
                    dctlst.append(dict({'sop': sopp, 'dat': datp}))
        self.lst = dctlst

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
                            default=['.dat', '.sop'],
                            dest='ftypes')
        parser.add_argument('-s', '--searchstrings',
                            help='''\
Matches string(s) against files' path names excluding
file base names, returning any files which contain any
listed string, and which fit all other restraints, in
absence of the '-b' flag.  If the '-b' flag is present
then the listed string(s) are tested against file base
names excluding the rest of the files' paths.  If no
files are found this flag does nothing.
Default Value: ""''',
                            nargs='*',
                            type=str,
                            default=[''],
                            dest='pats')
        parser.add_argument('-R', '--removefile',
                            help='''\
Removes specified file path from the file list.
Default Value: ""''',
                            nargs='*',
                            type=str,
                            default=[],
                            dest='rmpats')
        parser.add_argument('-x', '--xvar',
                            help="""\
Indicates variable to plot on the X-axis.
Default Value: time""",
                            choices=['time', 'frame', 'force', 'extension', \
                                     'ext', 'lineardistance', 'distlinear', \
                                     'endtoend', 'absendtoend', 'absext', \
                                     'absextension'],
                            nargs='?',
                            type=str,
                            default='time',
                            dest='xvar')
        parser.add_argument('-y', '--yvar',
                            help="""\
Indicates variable to plot on the Y-axis.
Default Value: force""",
                            choices=['time', 'frame', 'force', 'extension', \
                                     'ext', 'lineardistance', 'distlinear', \
                                     'endtoend', 'absendtoend', 'absext', \
                                     'absextension'],
                            nargs='*',
                            type=str,
                            default=['force'],
                            dest='yvar')
        parser.add_argument('-m', '--ma',
                            help="""\
Indicates the value over which a simple moving average of the data should be
taken. Defaults to a value of 1000""",
                            nargs='?',
                            type=int,
                            const=1000,
                            default=1000,
                            dest='ma')
        parser.add_argument("-e", "--end",
                            help="""\
Indicates the stop frame for data visualization.  If the number of total frames
is less than the value indicated then the this option is considered to be equal
to the number of frames.
Default Value: 100000000""",
                            nargs="?",
                            type=int,
                            const=100000000,
                            default=100000000,
                            dest="stop")
        parser.add_argument('-o', '--overlay',
                            help='''\
Indicates that the figure should overlay each plot onto the same figure. Can be
used up to two times. The first use indicates that only plots with the same
y-axis and x-axis should be overlaid. The second indicates that all plots should
be overlaid.''',
                            action='count',
                            default=0,
                            dest='overlay')
        parser.add_argument('-b', '--byfile',
                            help='''\
Flag which triggers altered '-s' flag search behavior.
See help for '-s' for additional details.''',
                            action='store_false',
                            dest='bydir')
        args = parser.parse_args()
        for key, val in args._get_kwargs():
            setattr(self, key, val)

class Plotter():
    """\
    Data Plotting / Processing Class
    """
    def __init__(self, **kwargs):
        """\
Initialization of key parameters.
        --> start
        --> stop
        --> ma

        plot = Plotter()
        """
        # Assigns each variable it's value
        for key, value in kwargs.items():
            setattr(self, key, value)

    def print_class(self):
        for key in dir(self):
            print(key, getattr(self, key))

    def load_data(self, dct=dict(), **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'sop' in dct: # Evaluates true if a sop file entry is in variable dct
            pth = dct['sop']
            with open(pth) as fp:
                for line in fp:
                    if '#' in line:
                        line = line[:line.find('#')]
                    lst = line.strip().split(maxsplit=1)
                    if len(lst) == 2:
                        setattr(self, lst[0], lst[1])
            if hasattr(self, 'timestep'):
                self.timestep = float(self.timestep)
            if hasattr(self, 'nav'):
                self.nav = int(self.nav)
            if hasattr(self, 'dcdfreq'):
                self.dcdfreq = int(self.dcdfreq)
            if hasattr(self, 'ma'):
                self.ma = int(self.ma)
            if hasattr(self, 'stop'):
                self.stop *= self.dcdfreq / self.nav
                self.stop = int(self.stop)
            if not hasattr(self, 'ma'):
                self.ma = 1000
            if not hasattr(self, 'start'):
                self.start = 0
            if not hasattr(self, 'stop'):
                self.stop = int(self.numsteps)
            if not hasattr(self, 'step'):
                self.step = int(self.ma) // int(self.nav)
                if self.step < 1:
                    self.step = 1
        if 'dat' in dct: # Evaluates true if a dat file entry is in variable dct
            #keys = ['data', 'ext_raw', 'ext', 'ext_linear', 'extension', \
            #        'frame', 'force', 'f70', 'f_raw', 'time', 'time_array_ms', \
            #        'end_to_end']
            #for key in keys:
            #    setattr(self, key, [])
            pth = dct['dat']
            pthnpy = pth.replace('.dat', '.npy', 1)
            print('DAT: time last modified:\t{!s}'.\
                  format(time.ctime(path.getmtime(pth))))
            try:
                print("NPY: time last modified:\t{}".\
                      format(time.ctime(path.getmtime(pthnpy))))
                if path.getmtime(pth) < path.getmtime(pthnpy):
                    print('DATFILE: is older than npy... Continue.')
                else:
                    print('DATFILE: is newer than npy... Remaking.')
                    os.remove(pthnpy)
            except OSError:
                pass
            if path.exists(pthnpy):
                dat = np.load(pthnpy)
                print(dat.shape)
            else:
                dat = np.loadtxt(pth)
                print(dat.shape)
                np.save(pthnpy, dat)
            f_raw = dat[self.start:self.stop:self.step, 3]
            abs_etoe = dat[self.start:self.stop:self.step, 1] * 0.1 # A > nm
            absextraw = abs_etoe - abs_etoe[0]
            absext = moving_average(absextraw, self.ma)
            e_to_e = dat[self.start:self.stop:self.step, 2] * 0.1 # A > nm
            col1 = dat[::, 0]
            size_arr = len(e_to_e) - self.ma
            f70 = f_raw * 70.0 # kcal/(mol*A) > pN
            fma = moving_average(f_raw, self.ma)
            fpico = fma * 70.0
            fnano = fma * 0.07
            ext_raw = e_to_e - e_to_e[0]
            ext = moving_average(ext_raw, self.ma)
            distance = abs(max(ext) - ext[0])
            ext_linear = np.linspace(0, distance, size_arr)
            if len(col1) <= self.stop:
                numlines = len(col1)
            else:
                numlines = self.stop
            total_steps = numlines * self.nav
            timeps = self.timestep * total_steps
            timens = timeps / 1E3
            timeus = timens / 1E3
            timems = timeus / 1E3
            time_array = np.linspace(0, timems, size_arr)
            frame_last = total_steps / self.dcdfreq
            frame = np.linspace(1, frame_last, size_arr)
            print("""\
================================================
=======  Force vs. Extension/Time/Frame  =======
================================================
File:\t{0}
Force Length:\t{1}; {2}

Extension Length:\t{3}; {4}

Linear Extension Length:\t{5}; {6}

Time:\t{7}; {8}

Frame:\t{9}; {10}


Extension/Force:
    End to End:\t{11}\t{12}
    Extension:\t{13}\t{14}
    Distance:\t{15}
    Linearized Distance:\t{16}\t{17}
    Force:\t{18} points of which the max is "{19}"
    Max Force (pN):\t{20}
    Max Force (nN):\t{21}

Frames:
    Step:\t{37}
    nav:\t{36}
    Dcdfreq:\t{22}
    Output Timing:\t{23}
    Data Points:\t{24}
    Column 1:\t{25}\t{26}
    Total Steps:\t{27}
    Last Frame:\t{28}
    Frame {29}, ..., {30}  ({31} total frames)

Time:
    Time (ms):\t{32}
    Time Array:\t{33}\t({34} Total time points)
    Array Size:\t{35}
================================================
================================================


""".format(pth, fnano, len(fnano), ext, len(ext), ext_linear, len(ext_linear), \
           time_array, len(time_array), frame, len(frame), e_to_e[0], \
           e_to_e[-1], ext[0], ext[-1], distance, ext_linear[0], \
           ext_linear[-1], len(f_raw), max(f_raw), max(fpico), max(fnano), \
           self.dcdfreq, self.outputtiming, len(e_to_e), col1[0], col1[-1], \
           total_steps, frame_last, frame[0], frame[-1], frame[-1] - frame[0], \
           timems, time_array, len(time_array), size_arr, self.nav, self.step))

            self.data = dat
            self.f_raw = f_raw
            self.f70 = f70
            self.force = fpico
            self.absendtoend = abs_etoe
            self.abs_ext_raw = absextraw
            self.absext = absext
            self.absextension = absext
            self.endtoend = e_to_e
            self.ext_raw = ext_raw
            self.ext = ext
            self.extension = ext
            self.distlinear = ext_linear
            self.lineardistance = ext_linear
            self.time = time_array
            self.time_array_ms = time_array
            self.frame = frame
