#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, argparse, fnmatch, glob, time, pickle
import matplotlib as mpl, matplotlib.pyplot as plt, os.path as path, numpy as np

def save_fig(outpath, fname, ftype):
    '''Saves figure in in the indicated directory.
    Directory will be made if it does not exist.
    '''
    if path.isdir(path.abspath(path.expanduser(outpath))):
        outpath = path.abspath(path.expanduser(outpath))
    else:
        outpath = path.abspath(path.expanduser(outpath))
        print('Making directory {}'.format(outpath))
        os.makedirs(outpath)

    pat = re.compile(fname + '-\d+', re.IGNORECASE)
    #Creates a list containing file names which match 'fname' in the 'outpath'
    #  directory after the extension and '-number' component have been removed.
    matching = [f1 for f1 in
                list(set([path.splitext(f2)[0] for f2 in
                          [f3 for f3 in os.listdir(outpath)]
                          if path.isfile(f2)]
                )) if pat.match(f1)]
    fname = fname + '-' + str(len(matching))

#    dpi = 300 #mpl.rcParams['figure.dpi']
    for t in ftype:
        plt.savefig(path.join(outpath, fname) + '.' + t)
        print(path.join(outpath, fname) + '.' + t)

def parse_arguments_main():
    '''Parses arguments sent to plotting scripts.
    '''
    mainparser = argparse.ArgumentParser(add_help=False)
    mainparser.add_argument('-s', '--searchterm',
                            help='Search terms to match to file/dir names',
                            nargs='+',
                            default='*.dat')

    subparsers = mainparser.add_subparsers(title='Figure rendering options',
                                           dest='choice')

    parser_show = subparsers.add_parser('show',
                                        help='Displays figure',
                                        add_help=True)
    parser_show.add_argument('inpath',
                             help='Path to data file(s)',
                             nargs='+')

    parser_save = subparsers.add_parser('save',
                                        help='Saves figure',
                                        add_help=True)
    parser_save.add_argument('outpath',
                             help='Directory in which to save plot(s).')
    parser_save.add_argument('fname',
                             help='Name of file where figure(s) will be saved.')
    parser_save.add_argument('inpath',
                             help='Path to data file(s)',
                             nargs='+')
    parser_save.add_argument('-t', '--type',
                             help='Select file type to save plot as.',
                             choices=['jpg','png','eps','svg','pdf','tiff'],
                             nargs='+',
                             dest='ftype',
                             default=['jpg','png','svg','tiff'])

    return mainparser

def moving_average(x, n, tpe='simple'):
    """Compute an n period moving average.
    Type can be 'simple' or 'exponential'
    """
    x = np.asarray(x)
    if tpe == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))
    weights /= weights.sum()
    a = np.convolve(x, weights, mode='full')[:len(x)]
    ma = a[n:]
    return ma


class FindFiles():
    """File Locator
    """
    def __init__(self, params=None):
        self.cwd = None
        self.pattern = None
        self.dct = {}
        self.total = 0
        self.filelist = []

        if type(params) == dict:
            for k, v in params.items():
                setattr(self, k, v)

    def print_class(self):
        keys = dir(self)
        for key in keys:
            print(key + ':\t', getattr(self, key))

    def print_query(self, dct=None):
        if dct == None:
            dct = self.dct
        print(len(dct.keys()), 'of', self.total)
        for k, v in dct.iteritems():
            print(k+'\t'+v['dirname']+'\t'+v['filename']+'\t\ttype:'+v['type'])

    def get_files(self):
        count = 0
        if self.pattern != None:
            if '*.' in self.pattern and len(re.findall(r'\..*', self.pattern))==1:
                self.pattern = fnmatch.translate(self.pattern)
            pat = re.compile(self.pattern)

        for dpath, basenames, fnames in os.walk(self.cwd):
            for name in fnames:
                if pat.search(name):
                    count += 1
                    fp = path.join(dpath, name)
                    self.filelist.append(fp)
                    self.dct[count] = {}
                    self.dct[count]['type'] = self.pattern
                    self.dct[count]['file'] = fp
                    self.dct[count]['filename'] = name
                    self.dct[count]['dirname'] = dpath
                    self.total = count

    def sort_dirname(self, pos, dct=None):
        if dct == None:
            dct = self.dct
        klist = dct.keys()
        xlist = [dct[k]['dirname'].split('/')[pos] for k in klist]
        slist = sorted(zip(xlist, klist))
        count = 0
        dct_r = {}
        for s in slist:
            dct_r[count] = {}
            dct_r[count]['type'] = dct[s[1]]['type']
            dct_r[count]['file'] = dct[s[1]]['file']
            dct_r[count]['filename'] = dct[s[1]]['filename']
            dct_r[count]['dirname'] = dct[s[1]]['dirname']
            count += 1
        return dct_r
    def sort_filename(self, dct=None):
        if dct == None:
            dct = self.dct
        dlist = [k['filename'] for k in dct.values()]
        dlist2 = [int(re.findall(r'\d+', d)[0]) for d in dlist]
        slist = sorted(zip(dlist, dct.keys()))

        count = 0
        dct_r = {}
        for s in  slist:
            dct_r[count] = {}
            dct_r[count]['type'] = dct[s[1]]['type']
            dct_r[count]['file'] = dct[s[1]]['file']
            dct_r[count]['filename'] = dct[s[1]]['filename']
            dct_r[count]['dirname'] = dct[s[1]]['dirname']
            count += 1
        return dct_r

        print(dlist)
        print(dlist2)
        print(dct.keys())
        print(slist)

        return dct

        xlist = [dct[k]['filename'].split('/')[-1] for k in klist]
        slist = sorted(zip(xlist, klist))
        count = 0
        dct_r = {}
        for s in slist:
            dct_r[count] = {}
            dct_r[count]['type'] = dct[s[1]]['type']
            dct_r[count]['file'] = dct[s[1]]['file']
            dct_r[count]['filename'] = dct[s[1]]['filename']
            dct_r[count]['dirname'] = dct[s[1]]['dirname']
            count += 1
        return dct_r

    def query_file(self, searchstring, dct=None):
        if dct == None:
            dct = self.dct
        return {k:v for k, v in dct.items() if re.search(searchstring, v['file']) != None}
    def query_filename(self, searchstring, dct=None):
        if dct == None:
            dct = self.dct
        return {k:v for k, v in dct.items() if re.search(searchstring, v['filename']) != None}
    def query_dirname(self, searchstring, pos=None, dct=None):
        if dct == None:
            dct = self.dct
        if (pos == None) or (pos == -1):
            return {k:v for k, v in dct.items() if re.search(searchstring, v['dirname']) != None}
        else:
            return {k:v for k, v in dct.items() if re.search(searchstring, v['dirname'].split('/')[pos]) != None}
    def remove_file(self, searchstring, dct=None):
        if dct == None:
            dct = self.dct
        return {k:v for k, v in dct.items() if re.search(searchstring, v['file']) == None}
    def remove_filename(self, searchstring, dct=None):
        if dct == None:
            dct = self.dct
        return {k:v for k, v in dct.items() if re.search(searchstring, v['filename']) == None}
    def remove_dirname(self, searchstring, pos=None, dct=None):
        if dct == None:
            dct = self.dct
        if pos == None:
            return {k:v for k, v in dct.items() if re.search(searchstring, v['dirname']) == None}
        else:
            return {k:v for k, v in dct.items() if re.search(searchstring, v['dirname'].split('/')[pos]) == None}

    def from_dirs_get_files(self, searchstring, dct=None):
        lst_empty = []
        lst_files = []
        if dct == None:
            dct = self.dct
        dct_new = {}
        count = 0
        for k in dct.keys():
            fpall = glob.glob(path.join(dct[k]['dirname'], searchstring))
            if fpall:
                lst_files += fpall
            else:
                lst_empty.append(dct[k]['dirname'])
            for i in range(len(lst_files)):
                dct_new[i] = {}
                dct_new[i]['type'] = searchstring
                dct_new[i]['file'] = lst_files[i]
                dct_new[i]['filename'] = path.basename(lst_files[i])
                dct_new[i]['dirname'] = path.dirname(lst_files[i])
            x = lent(dct_new.keys())
            print(('Returning', len(dct_new)), searchstring, 'files; empty dirs:', len(lst_empty))
            return dct_new, lst_empty
    def rename_file(self, dct=None, modstring=None):
        lst_dirs = []
        if dct == None:
            dct = self.dct
        mod_orig = modstring
        for k in dct.keys():
            os.chdir(dct[k]['dirname'])
            if mod_orig == None:
                modstring = str(0).zfill(2)
            else:
                modstring = str(int(mod_orig)).zfill(2)
            print('Renaming:\t' + dct[k]['filename'])
            newfile = dct[k]['filename'] + '.' + modstring
            while path.exists(newfile):
                modstring = str(int(modstring) + 1).zfill(2)
                print('Mod:\t' + modstring)
                newfile = dct[k]['filename'] + '.' + modstring
            print(newfile)
            os.rename(dct[k]['filename'], newfile)
        return lst_dirs

    def delete_file(self,dct=None):
        if dct == None:
            dct = self.dct
        for k in dct.keys():
            os.chdir(dct[k]['dirname'])
            print(dct[k]['filename'])
            os.remove(dct[k]['filename'])


class Plotter():
    """Class for plotting data.
    """
    def __init__(self, job_type, start=0, stop=2000000, ma=20, step=1, ts=16,
                 nav=50, dcdfreq=1000000, seam='down', outputtiming=1000000):
        """Key parameter initialization.

        function: gsop
        > nav
        > start
        > stop
        > step (skips data points)
        > ma
        > ts
        > dcdfreq
        > outputtiming

        example of usage:
        mylib = os.path.expanduser('~/dev/pylib')
        sys.path.append(mylib)
        from data_analysis_mt.core import Plotter

        plotter = Plotter(job_type='gsop', nav=1000, start=0, stop=1000000,
        ma=50, ts=20.0, dcdfreq=1000000, outputtiming=1000000)
        """
        self.job_type = job_type
        self.start = start
        self.stop = stop
        self.step = step
        self.ts = ts
        self.ma = ma
        self.nav = nav
        self.seam = seam
        self.dcdfreq = dcdfreq
        self.outputtiming = outputtiming
        self.total_time_ms = float(stop) * float(ts) / 1000.0 / float(nav)
        self.time_start = float(start) / float(stop) * self.total_time_ms
        self.time_stop = self.total_time_ms
        print(start, stop, dcdfreq, nav, 1000)
        startf = float(start)
        stopf = float(stop)
        dcdf = float(dcdfreq)
        navf = float(nav)
        print(startf, stopf, dcdf, navf, 1000.0)
        num_frames = stopf /dcdf *1000.0
        print('num_frames:', num_frames)
        self.frame_first = startf / stopf * num_frames
        if self.frame_first == 0:
            self.frame_last = self.frame_first + num_frames
        self.print_class()
    def print_class(self):
        """Print class & its attributes.
        """
        keys = dir(self)
        for key in keys:
            print(str(key) + ':\t' + str(getattr(self, key)))

    def load_data(self, pth):
        print(path.relpath(path.dirname(pth)))
        bn = path.basename(pth)
        fp = path.dirname(pth)
        npy = re.sub(r'.dat', r'.npy', bn)
        fp_npy = re.sub(r'.dat', r'.npy', pth)
        print('DAT: time last modified:\t{!s}'.format(time.ctime(path.getmtime(fp))))
        try:
            print("NPY: time last modified:\t{}".format(time.ctime(path.getmtime(fp_npy))))
            if path.getmtime(fp) <= path.getmtime(fp_npy):
                print('DATFILE: is older than npy... Continue.')
            else:
                print('DATFILE: is newer than npy... Remaking.')
                os.remove(fp_npy)
        except OSError:
            pass

        if path.exists(fp_npy):
            data = np.load(fp_npy)
            print(data.shape)
        else:
            data = np.loadtxt(pth)
            print(data.shape)
            np.save(fp_npy, data)
        self.data = data

        if self.job_type == 'mt-pull':
            f_raw = data[self.start:self.stop:self.step, 3]

            #converts 2nd column from A to nm
            end_to_end = data[self.start:self.stop:self.step, 1] * 0.1
            col1 = data[::, 0]
            size_arr = len(end_to_end) - self.ma
            f70 = f_raw * 70.0
            fma = moving_average(f_raw, self.ma)
            fpico = fma * 70.0
            fnano = fma * 0.07
            ext_raw = end_to_end - end_to_end[0]
            ext = moving_average(ext_raw, self.ma)
            distance = abs(max(ext) - min(ext))
            ext_linear = np.linspace(0, distance, size_arr)
            if (len(fpico) != len(fnano)) or (len(fpico) != size_arr):
                raise 'ERROR: fpico != fnano != size_arr.'
            numlines = len(col1)
            total_steps = numlines * self.nav - self.nav
            timeps = self.ts * total_steps
            timens = timeps * 0.001
            timeus = timens * 0.001
            timems = timeus * 0.001
            time_array = np.linspace(0, timems, size_arr)
            frame_last = total_steps / self.dcdfreq
            frame = np.linspace(1, frame_last, size_arr)
            print('''
Extension/Force:
    End to End:\t{0}\t{1}
    Extension:\t{2}\t{3}
    Distance:\t{4}
    Extension linear:\t{5}\t{6}
    Force:\t{7} points of which the max is "{8}"
    Force (pN):\t{9}
    Force (nN):\t{10}
Frames:
    Dcdfreq:\t{11}
    Output Timing:\t{12}
    Data Points:\t{13}
    Column 1:\t{14}\t{15}
    Total Steps:\t{16}
    Last Frame:\t{17}
    Frame {18}, ..., {19}  ({20} total frames)
Time:
    Time (ms):\t{21}
            Time Array:\t{22}\t({23} Total time points)
    Array Size:\t{24}
'''.format(end_to_end[0], end_to_end[-1], ext[0], ext[-1], distance,
           ext_linear[0], ext_linear[-1], len(f_raw), max(f_raw),
           max(fpico), max(fnano), self.dcdfreq, self.outputtiming,
           len(end_to_end), col1[0], col1[-1], total_steps,
           frame_last, frame[0], frame[-1], len(frame), timems,
           time_array, len(time_array), size_arr))
            self.f_raw = f_raw
            self.f70 = f70
            self.end_to_end = end_to_end
            self.ext_raw = ext_raw
            self.force = fpico
            self.ext = ext
            self.extension = ext
            self.ext_linear = ext_linear
            self.time = time_array
            self.time_array_ms = time_array
            self.frame = frame
            print("""
            ============================================
            =====  Force vs. Extension/Time/Frame  =====
            ============================================
            Force Length:\t{0}; {1}
            Extension Length:\t{2}; {3}
            Linear Extension Length:\t{4}; {5}
            Time:\t{6}; {7}
            Frame:\t{8}; {9}
            """.format(self.force[-1], len(self.force),
                       self.extension[-1], len(self.extension),
                       self.ext_linear[-1], len(self.ext_linear),
                       self.time[-1], len(self.time),
                       self.frame[-1], len(self.frame)))
