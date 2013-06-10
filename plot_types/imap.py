import os
import logging
logger = logging.getLogger(__name__)

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.axes_grid1 import ImageGrid

import utils as U

matplotlib.rcParams['xtick.direction'] = 'out' 
matplotlib.rcParams['ytick.direction'] = 'out' 

@U.is_plot_type
def imap(data, A, C, **kw):
    """imap: interaction map"""
    logger.info('start plotting interaction map...')

    fig = plt.figure(figsize=(12,9))
    col, row = U.gen_rc(len(data.keys()))
    col, row = row, col
    grid = ImageGrid(fig, 111, nrows_ncols = (row, col), 
                     axes_pad = 0.3, 
                     add_all=True, label_mode = "L")

    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)

    normalize(data)
    max_ = get_max(data)
    for k, gk in enumerate(data.keys()):
        ax = grid[k]

        da = data[gk]
        rda = da
        rda[-1][-1] = max_
        rda[0][-1] = max_
        # sophisticated reversal to make x axis donor, y axis acceptor
        # rda = np.array([i[::-1] for i in da.transpose()[::-1]])

        # sophisticated reversal to make x axis acceptor, y axis donor
        # rda = np.array([i[::-1] for i in da[::-1]])

        # printer friendly color maps: Orange
        im = ax.imshow(rda, origin="lower", cmap="gist_heat",
                  vmin=0, vmax=1, interpolation="nearest")
        im.set_clim(0, max_)

        ax.minorticks_on()
        decorate_ax(ax, pt_dd, gk)

    plt.colorbar(im, shrink=.5, orientation='vertical', anchor=(1.3, 0))
    plt.savefig(U.gen_output_filename(A, C))

def get_max(data):
    max_ = []
    for i in data:
        max_.append(data[i].max(axis=0).max())
    return max(max_)
                    
def normalize(data):
    for i in data:
        data[i] = data[i] / np.sum(data[i])

def decorate_ax(ax, pt_dd, gk):
    if 'xlabel' in pt_dd: ax.set_xlabel(pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(pt_dd['ylabel'])
    
    if 'titles' in pt_dd:
        ax.set_title(U.get_param(pt_dd['titles'], gk))
    else:
        ax.set_title(gk)