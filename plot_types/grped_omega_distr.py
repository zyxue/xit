import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.pyplot as plt

import utils as U

from grped_distr import grp_datasets

@U.is_plot_type
def grped_omega_distr(data, A, C, **kw):
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)

    dsets = grp_datasets(data, pt_dd)
    if 'bins' in pt_dd:
        i, j, s = [float(_) for _ in pt_dd['bins']]
    else:
        i, j, s = [-0.1, 1.1, 0.1]

    bins = np.arange(i, j, s)

    fig = plt.figure(figsize=pt_dd.get('figsize', (12,9)))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])
    ncol, nrow = U.gen_rc(len(dsets.keys()), pt_dd)
    logger.info('Chosen # of cols: {0}, # of rows; {1}'.format(ncol, nrow))
    for c, dsetk in enumerate(dsets):
        dset = dsets[dsetk]
        ax = fig.add_subplot(nrow, ncol, c+1)
        if 'text' in dset:
            ax.text(s=dset['text'], **pt_dd['text'])
        for gk in dsets[dsetk]['data']:
            da = dsets[dsetk]['data'][gk]
            params = get_params(gk, pt_dd)
            ax.hist(da, bins=bins, normed=False, alpha=0.3, **params)

        decorate_ax(ax, pt_dd, ncol, nrow, c)
    plt.savefig(U.gen_output_filename(A, C))

def get_params(key, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], key)
    if 'labels' in pt_dd:
        params['label'] = U.get_param(pt_dd['labels'], key)
    return params

def decorate_ax(ax, pt_dd, ncol, nrow, c):

    """c: counter"""
    if c < (ncol * nrow - ncol):
        ax.set_xticklabels([])
        # ax.get_xaxis().set_visible(False)                   # this hide the whole axis
    else:
        if 'xlabel' in pt_dd: 
            ax.set_xlabel(**pt_dd['xlabel'])

    if c % ncol == 0:
        if 'ylabel' in pt_dd:
            ax.set_ylabel(**pt_dd['ylabel'])
    else:
        ax.set_yticklabels([])

    if 'grid' in pt_dd:   ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xscale' in pt_dd: ax.set_xscale(**pt_dd['xscale'])
    if 'legend' in pt_dd: ax.legend(**pt_dd['legend'])
