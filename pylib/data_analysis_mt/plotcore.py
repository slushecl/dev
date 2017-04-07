#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# module imports
import sys
import os.path
import math
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser('~/dev/pylib/data_analysis_mt'))
import newcore as Core


class PullDataAnalyzer(Core.FileReader):
    """\
Class which performs calculations and stores results using pulling data from
.dat and .sop files"""

    def analyze(self):
        "\
Performs calculations on pulling data."
        if not self.sopcheck == self.datcheck == True:
            return
        col0 = self.dat[::, 0] # Frame number
        col2init = self.dat[0, 2] # Force
        self.nframes = int(len(col0) / self.dcdfreq * self.nav)
        if not hasattr(self, 'start'):
            self.start = 0
        elif self.start is not int:
            int(self.start)
        else:
            if self.start < 0:
                self.start += self.nframes
            elif self.start > self.nframes-self.maframe:
                print('''Indicated start frame out of range.
                Skipping file: {}'''.format(self.path))
                return
            if self.start < self.maframe:
                self.start = 0
        if not hasattr(self, 'stop'):
            self.stop = self.nframes
        elif self.stop is not int:
            int(self.stop)
        else:
            if self.stop > self.nframes:
                self.stop = self.nframes
            elif self.stop < 0:
                self.stop += self.nframes
            if self.stop < self.maframe:
                print('''Indicated stop frame out of range.
                Skipping file: {}'''.format(self.path))
                return
        if self.stop <= self.start:
            print('''Stop less than start.
            Skipping file: {}'''.format(self.path))
            return
        self.numframes = self.stop - self.start
        startline = math.floor(self.start*self.dcdfreq/self.nav)
        stopline = math.ceil(self.stop*self.dcdfreq/self.nav)
        self.endtoend = self.dat[startline:stopline:self.step, 2]*0.1 # A > nm
        self.extension = Core.moving_average(self.endtoend-col2init*0.1,self.ma)
        arraysize = len(self.extension)
        force = self.dat[startline:stopline:self.step, 3] # kcal/(mol*A)
        # f70 = force*70.0 # kcal/(mol*A) > pN
        fma = Core.moving_average(force, self.ma)
        self.forcepico = fma*70.0 # pN
        self.forcenano = fma*0.07 # nN
        starttimepico = self.timestep*self.start
        starttimenano = starttimepico/1E3
        starttimemicro = starttimepico/1E6
        starttimemilli = starttimepico/1E9
        stoptimepico = self.timestep*self.stop
        stoptimenano = stoptimepico/1E3
        stoptimemicro = stoptimepico/1E6
        stoptimemilli = stoptimepico/1E9
        self.timepico = np.linspace(starttimepico, stoptimepico, arraysize)
        self.timenano = np.linspace(starttimenano, stoptimenano, arraysize)
        self.timemicro = np.linspace(starttimemicro, stoptimemicro, arraysize)
        self.timemilli = np.linspace(starttimemilli, stoptimemilli, arraysize)
        self.frame = np.linspace(self.start, self.stop, arraysize)
        #for x for self.finder.xvar:
        self.xmin = float(1E20)
        self.xmax = float(-1E20)
        self.xdelta = 0.0
        #for y for self.finder.yvar:
        self.ymin = 1E20
        self.ymax = -1E20
        self.ydelta = 0.0
        self.datx = getattr(self, self.finder.xvar)
        self.daty = getattr(self, self.finder.yvar)
        if self.xmin > min(self.datx):
            self.xmin = min(self.datx)
        if self.xmax < max(self.datx):
            self.xmax = max(self.datx)
        if self.xdelta < abs(max(self.datx)-min(self.datx))*0.05:
            self.xdelta = abs(max(self.datx)-min(self.datx))*0.05
        if self.ymin > min(self.daty):
            self.ymin = min(self.daty)
        if self.ymax < max(self.daty):
            self.ymax = max(self.daty)
        if self.ydelta < abs(max(self.daty)-min(self.daty))*0.05:
            self.ydelta = abs(max(self.daty)-min(self.daty))*0.05


    def makeplot(self):
        """Makes plots for figures."""
        finder = self.finder
        # if finder.overlay == 0:
        #     dims = Core.dimensions(finder.numvarsx*finder.numvarsy)
        legdct = Core.path_split(self.path)
        if legdct:
            legstr = '{prots} {runnum} - {method} {direction}'.format(**legdct)
        else:
            legstr = self.path
        # for i, varx in enumerate(finder.xvar):
        #     for j, vary in enumerate(finder.yvar):
        if finder.overlay == 1:
            #plt.subplot(dims[0], dims[1], i*finder.numvarsy+j+1)
            plt.plot(self.datx, self.daty, alpha=0.6, label=legstr)
            plt.legend(loc=0, fontsize='small')
            plt.xlabel(finder.xvar.title(), size='x-large')
            plt.ylabel(finder.yvar.title(), size='x-large')


    def summarize(self):
        """\
Prints a summary of the data currently stored in the DatReader() instance."""
        if self.datcheck is True:
            print("""\
{}
================================================
=======  Force vs. Extension/Time/Frame  =======
================================================
""".format(self.datshape))


    def info(self):
        """\
Prints all attributes of the current PullPlotter() instance."""
        for key in dir(self):
            print(key, getattr(self, key))

#P = PullPlotter()
F = Core.FindFiles()
# F.numvarsx = len(F.xvar)
# F.numvarsy = len(F.yvar)
plt.figure()
deltax = 0.0
minx = 1E20
maxx = -1E20
deltay = 0.0
miny = 1E20
maxy = -1E20
for attrname in F.uniqdirs:
    fdata = getattr(F, list(attrname)[0])
    R = PullDataAnalyzer(fdata, F)
    R.analyze()
    if R.datcheck and R.sopcheck:
        R.makeplot()
        if R.finder.overlay == 1:
            if R.xdelta > deltax:
                deltax = R.xdelta
            if R.xmin < minx:
                minx = R.xmin
            if R.xmax > maxx:
                maxx = R.xmax
            if R.ydelta > deltay:
                deltay = R.ydelta
            if R.ymin < miny:
                miny = R.ymin
            if R.ymax > maxy:
                maxy = R.ymax
plt.xlim(minx-deltax, maxx+deltax)
plt.ylim(miny-deltay, maxy+deltay)
plt.show()
sys.exit()
