#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# module imports
import sys, time, argparse, os, re
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt, os.path as path
from matplotlib.gridspec import GridSpec

cwd = os.getcwd()
lib = path.expanduser('~/dev/pylib')
sys.path.insert(0, lib)
import data_analysis_mt.core as core

print('Backend: {}'.format(mpl.get_backend()))
fig = plt.figure(0)

def parse_arguments():
    parser = argparse.ArgumentParser(parents=[core.parse_arguments_main()])
    parser.add_argument('-d', '--dataname',
                        help='Data name: latcenter, longevenwith',
                        choices=['lat', 'long', 'all'],
                        default='all')
    #parser.add_argument('-r', '--roundname',
                         #help='Round name: 1, 2, 3,..., 99',
                         #type=int)
    parser.add_argument('-m', '--multi',
                        help='If multi flag is present set multi to True',
                        action='store_true')
    args = parser.parse_args()
    return args

args = parse_arguments()
#searches = args.searchlist
choice = args.choice
inpath = args.inpath
data = args.dataname
#roundn = args.roundname
multi = args.multi
result = 'gsop'
plot = 'pulling'
for n in range(len(inpath)):
    if path.isfile(path.abspath(path.expanduser(inpath[n]))):
        inpath[n] = path.abspath(path.expanduser(inpath[n]))
    else:
        raise 'File does not exist.'

#combined = '{0!s}_{1!s}_{2!s:0>2}_{3!s}'.format(result, plot, roundn, data)
#combined = '{!s}_{!s}_{!s}'.format(result)
print(cwd)

gs = GridSpec(1,1)
ax1 = plt.subplot(gs[0,:])
ax = [ax1]

if multi:
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax = [ax1, ax2, ax3]

def load_target(wd=cwd, pat=r'.*\.dat\Z'):
    print('cwd:\t' + wd)
    print('pattern:\t' + pat)
    dct_find = {'cwd':wd, 'pattern':pat}
    x = core.FindFiles(dct_find)
    x.get_files()
    #print(x.dct.items())
    print(len(x.dct.keys()), 'of', x.total)
    set9 = x.dct
    set9 = x.remove_dirname('test', None, set9)
#    set9 = x.remove_dirname('fail', None, set9)
    set9 = x.remove_dirname('standard', None, set9)
    set9 = x.remove_dirname('dat', -1, set9)
    print(len(set9.keys()), 'of', x.total)
    set9 = x.sort_dirname(-1, set9)
    print(set9)
    return set9

def get_files(dct, searchstr, n, b=True):
    print('Files entered:\t' + str(len(dct.keys())))
    x = core.FindFiles()
    print(searchstr)
    set9 = x.query_dirname(searchstr, n, dct)
    if b:
        set9 = x.sort_dirname(-1, set9)
        print('Files returned:\t' + str(len(set9.keys())))
        return set9
    else:
        lst = set9.keys()
        return sorted(lst)

dct_dat = load_target()
print(len(dct_dat.keys()))
dct_plot = get_files(dct_dat, '.', -2)
for k, v in dct_plot.items():
    print(k, v['file'])
if data != 'all':
    lst_plot = get_files(dct_plot, '.', -3, False)
else:
    lst_plot = dct_plot.keys()
print(lst_plot)

min_x = 0.0
max_x = 0.0
for k, v in dct_plot.items():
    if k not in lst_plot:
        continue
    print('Plotting ' + str(k))

    D = core.Plotter('mt-pull', start=0, stop=1825000000, ma=100,
                    step=1, ts=0.16, nav=1000, dcdfreq=1000000,
                     seam='down', outputtiming=50000)
    D.load_data(v['file'])

    e8 = D.extension[-1] * 0.05
    t8 = D.time[-1] * 0.05
    f8 = D.frame[-1] * 0.05
    print(e8)
    print(t8)
    print(f8)

    newminx = D.frame[0]-f8 #D.time[0]-t8
    newmaxx = D.frame[-1]+f8#D.time[-1]+t8
    print(newminx, newmaxx)
    if min_x > newminx:
        min_x = newminx
    if max_x < newmaxx:
        max_x = newmaxx
    print("X-min, X-max:\t" + str(min_x) + ', ' + str(max_x))
    ax1.set_xlim(min_x, max_x)

    if multi:
        eline = ax1.plot(D.extension, D.force, 'k-')
        ax2.set_xlim(D.time[0] - t8, D.time[-1] + t8)
        tline = ax1.plot(D.time, D.force, 'b')
        fig.text(0.01, 0.135, 'Time (ms)', color='b', size=16)
        ax2.spines['bottom'].set_color('b')
        ax2.spines['bottom'].set_position(('outward', 70.0))
        ax2.xaxis.set_ticks_position('bottom')
        for tick in ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)

        ax3.set_xlim(D.frame[0] - f8, D.frame[-1] + f8)
        fline = ax3.plot(D.frame, D.force, 'm')
        fig.text(0.01, 0.050, 'Frame #', color='m', size=16)
        ax3.spines['bottom'].set_color('m')
        ax3.spines['bottom'].set_position(('outward', 110.0))
        ax3.xaxis.set_ticks_position('bottom')
        for tick in ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        break
    else:
        plt.plot(D.frame, D.force * 2)
        #plt.plot(D.time, D.force * 2)
        #ax1.set_ylim(-0.05, 0.1)
        ax1.set_xlabel("Step #")
        #ax1.set_xlabel("Time (ms)")
        #ax1.set_xlabel("Indentation Depth (nm)")
        ax1.set_ylabel("Force (pN)")

if choice =='show':
    plt.show()
    sys.exit()
elif choice == 'save':
    core.save_fig(args.outpath, args.fname, args.ftype)
else:
    raise 'ERROR: Something went terribly, terribly wrong.'
