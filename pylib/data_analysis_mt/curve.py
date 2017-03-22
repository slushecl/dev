#!/home/slushecl/dev/pylib/python3.5/bin/python3
# -*- coding: utf-8 -*-

# module imports
import sys, matplotlib.pyplot as plt, os.path
from matplotlib.gridspec import GridSpec
sys.path.insert(0, os.path.expanduser('~/dev/pylib/data_analysis_mt'))
import core

ff = core.FindFiles()
ff.parse()
ff.find()
ff.refine()
ff.remove()
ff.sort()
fig = plt.figure(facecolor='#ffd8d8')
#gs = GridSpec(1, 1)
#ax1 = plt.subplot(gs[0,:])
minx, maxx, miny, maxy = 0.0, 0.0, 0.0, 0.0
num = [n for n in range(len(ff.lst)*len(ff.yvar), 0, -1)]
lena = len(ff.lst)
lenb, k = len(ff.yvar), 1
while lenb > k**2:
    k += 1
if ff.overlay == 2:
    plt.subplot(1, 1, 1)
lims = dict()
for vy in ff.yvar:
    lims[vy] = {'xmin': 0.0, 'xmax': 0.0, 'ymin': 0.0, 'ymax': 0.0}
for i, dct in enumerate(ff.lst):
    p = core.Plotter(ma=ff.ma)
    p.load_data(dct=dct, stop=ff.stop)
    for h, vary in enumerate(ff.yvar):
        y = getattr(p, vary)
        yf = max(y) * 0.05
        if min(y) - yf < lims[vary]['ymin']:
            lims[vary]['ymin'] = min(y) - yf
        if max(y) + yf > lims[vary]['ymax']:
            lims[vary]['ymax'] = max(y) + yf
        x = getattr(p, ff.xvar)
        xf = max(x) * 0.05
        if min(x) - xf < lims[vary]['xmin']:
            lims[vary]['xmin'] = min(x) - xf
        if max(x) + xf > lims[vary]['xmax']:
            lims[vary]['xmax'] = max(x) + xf
        if ff.overlay == 0:
            plt.subplot(lena, lenb, num.pop())
            plt.plot(x, y, alpha=0.75, \
                     label='Run ' + str(i+1) + ': '+ vary.title())
            plt.legend(loc=0)
            plt.xlim(lims[vary]['xmin'], lims[vary]['xmax'])
            plt.ylim(lims[vary]['ymin'], lims[vary]['ymax'])
            plt.xlabel(ff.xvar.title(), size='x-large')
            plt.ylabel(vary.title(), size='x-large')
            plt.title(vary.title() + ' vs ' + ff.xvar.title(), size='xx-large')
            lims[vary]['xmin'], lims[vary]['xmax'] = 0.0, 0.0
            lims[vary]['ymin'], lims[vary]['ymax'] = 0.0, 0.0
        if ff.overlay == 1:
            plt.subplot(k, k, h+1)
            plt.plot(x, y, alpha=0.75, label='Run ' + str(i+1))
            plt.legend(loc=0)
            plt.xlabel(ff.xvar.title(), size='x-large')
            plt.ylabel(vary.title(), size='x-large')
            plt.title(vary.title() + ' vs ' + ff.xvar.title(), size='xx-large')
            plt.xlim(lims[vary]['xmin'], lims[vary]['xmax'])
            plt.ylim(lims[vary]['ymin'], lims[vary]['ymax'])
        if ff.overlay == 2:
            plt.plot(x, y, alpha=0.75, label='Run '+str(i+1)+': '+vary.title())
            plt.legend(loc=0)
if ff.overlay == 2:
    for a in lims.values():
        if a['xmin'] < minx:
            minx = a['xmin']
        if a['xmax'] > maxx:
            maxx = a['xmax']
        if a['ymin'] < miny:
            miny = a['ymin']
        if a['ymax'] > maxy:
            maxy = a['ymax']
    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)
    plt.xlabel(ff.xvar.title(), size='x-large')
    plt.ylabel(' | '.join(ff.yvar).title(), size='x-large')
    plt.title(', '.join(ff.yvar).title()+' vs '+ff.xvar.title(), \
              size='xx-large')
plt.show()
sys.exit()
