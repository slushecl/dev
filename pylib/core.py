#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, argparse
import matplotlib as mpl, matplotlib.pyplot as plt, os.path as path

def save_fig():
    '''Saves figure in in the indicated directory.
    Directory will be made if it does not exist.
    '''
    if path.isdir(path.abspath(path.expanduser(savedir))):
        savedir = path.abspath(path.expanduser(savedir))
    else:
        savedir = path.abspath(path.expanduser(savedir))
        print('Making directory {}'.format(savedir))
        os.makedirs(savedir)

    pat1 = re.compile('pub', re.IGNORECASE)
    if style.strip().lower() == 'all':
        files = [f for f in os.listdir(savedir)]
        files = [f1 for f1 in files if not re.search(pat1, f1)]
    print('Saving figure to {}'.format(savedir))

    if path.isdir(path.abspath(path.expanduser(fname))):
        fname = path.abspath(path.expanduser(fname))

def parse_arguments():
    '''Parses arguments sent to the script.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('outpath',
                        help='Directory in which to save plot(s).',
                        default='./figs')
    parser.add_argument('inpath',
                        help='Directory containg data file(s) to be plotted.',
                        nargs='+',
                        default='.')
    parser.add_argument('file',
                        help='Name of file where figure(s) will be saved.',
                        deffault='plot')
    parser.add_argument('type',
                        help='Select file type to save plot as.',
                        choices=['jpg','png','eps','svg','pdf','tiff'],
                        nargs='+',
                        default=['jpg','png','svg','tiff'])
    parser.add_argument('options',
                        help='Select any options to enable.',
                        choices=['show', 'publish'],
                        default='show')
    args = parser.parse_args()

    inpath = args.inpath
