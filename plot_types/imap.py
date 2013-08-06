# -*- coding: utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from mpl_toolkits.axes_grid1 import ImageGrid

import utils as U

matplotlib.rcParams['xtick.direction'] = 'out' 
matplotlib.rcParams['ytick.direction'] = 'out' 

@U.is_plot_type
def imap(data, A, C, **kw):
    """imap: interaction map"""
    logger.info('start plotting interaction map...')
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)

    fig = plt.figure(figsize=(12,9))
    col, row = U.gen_rc(len(data.keys()), pt_dd)
    grid = ImageGrid(fig, 111, nrows_ncols = (row, col), 
                     axes_pad = 0.3, 
                     add_all=True, label_mode = "L")

    if 'denorminators' in pt_dd:
        for gk in data:
            dn = U.get_param(pt_dd['denorminators'], gk)
            logger.info('denorminator: {0}'.format(dn))
            data[gk] = data[gk] / dn

    # used to set up the reference point and the range of color bar
    max_ = get_max(data)
    for k, gk in enumerate(data.keys()):
        ax = grid[k]

        da = data[gk]
        rda = da

        # JUST FOR REFERENCE OF SEEING WHERE THE END POINTS ARE, DEBUGGING USES
        # rda[-1][-1] = max_
        # rda[0][-1] = max_

        # sophisticated reversal to make x axis donor, y axis acceptor
        # rda = np.array([i[::-1] for i in da.transpose()[::-1]])

        # sophisticated reversal to make x axis acceptor, y axis donor
        # rda = np.array([i[::-1] for i in da[::-1]])

        params = get_params(gk, pt_dd)
        logger.info(params)
        # cmap_options: hot, gist_heat, Orange (printer friendly)

        # remove the info about the Hbonding information about first residue,
        # which ACE, this make the final map easier to understand
        rda = np.delete(np.delete(rda, 0, 0), 0, 1)

        im = ax.pcolormesh(rda, **params)

        if 'clim' in pt_dd:
            im.set_clim(**pt_dd['clim'])
        else:
            im.set_clim(0, max_)

        logger.info('shape after removal of the 0th residue: {0}'.format(rda.shape))
        ax.set_xlim([0, rda.shape[0]])
        ax.set_ylim([0, rda.shape[1]])

        ax.minorticks_on()
        decorate_ax(ax, pt_dd, gk)

    plt.colorbar(im, shrink=.5, orientation='vertical', anchor=(1.3, 0))
    plt.savefig(U.gen_output_filename(A, C), **pt_dd.get('savefig', {}))

def get_max(data):
    max_ = []
    for i in data:
        max_.append(data[i].max(axis=0).max())
    return max(max_)

def get_params(gk, pt_dd):
    params = {}
    if 'cmap' in pt_dd:
        params['cmap'] = getattr(cm, pt_dd['cmap'])
    if 'edgecolors' in pt_dd:
        params['edgecolors'] = pt_dd['edgecolors']
    else:
        params['edgecolors'] = 'none'

    # The following only applies to imshow, does not apply to pcolor
    # if 'interpolation' in pt_dd:
    #     params['interpolation'] = pt_dd['interpolation']
        # Acceptable values are None, ‘none’, ‘nearest’, ‘bilinear’, ‘bicubic’,
        # ‘spline16’, ‘spline36’, ‘hanning’, ‘hamming’, ‘hermite’, ‘kaiser’,
        # ‘quadric’, ‘catrom’, ‘gaussian’, ‘bessel’, ‘mitchell’, ‘sinc’,
        # ‘lanczos’

    return params

def decorate_ax(ax, pt_dd, gk):
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    
    if 'titles' in pt_dd:
        ax.set_title(U.get_param(pt_dd['titles'], gk))
    else:
        ax.set_title(gk)

    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
