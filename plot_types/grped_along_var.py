import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict as odict

import matplotlib.pyplot as plt
import numpy as np

import utils as U

@U.is_plot_type
def grped_along_var(data, A, C, **kw):
    pt_dd = C['plot'][A.property][A.plot_type]
    dsets = group_datasets(data, grp_REs = pt_dd['grp_REs'])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # from matplotlib import rc
    # rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    # rc('text', usetex=True)
    ax_plot(ax, dsets, pt_dd, A)

    decorate_ax(ax, pt_dd)
    plt.savefig(U.gen_output_filename(A, C))

def ax_plot(ax, dsets, pt_dd, A):
    for c, dsetk in enumerate(dsets.keys()):
        dset = dsets[dsetk]
        means = np.array([dset[kk][0] for kk in dset.keys()])
        stds  = np.array([dset[kk][1] for kk in dset.keys()])
        params = get_params(dsetk, pt_dd)
        if A.v: logger.info('params for {0}: {1}'.format(dsetk, params))
        xs = pt_dd.get('xs', range(len(dset.keys())))
        ax.plot(xs, means, **params)
        ax.fill_between(xs, means-stds, means+stds,
                        where=None, facecolor=params.get('color'), alpha=0.3)
    
def group_datasets(data, grp_REs):
    dsets = odict() # dsets: meaning further grouping, based on which
                          # ploting will be done

    # structure of dsets: dict of dict of dict ...
    # dset = {
    #     'dset0': {
    #         'groupkey0': ('mean0', 'std0'),
    #         'groupkey1': ('mean1', 'std1'),
    #         ...
    #         },
    #     'dset1': {
    #         'groupkey0': ('mean0', 'std0'),
    #         'groupkey1': ('mean1', 'std1'),
    #         ...
    #         },
    #     ...
    #     }
        
    for c, RE in enumerate(grp_REs):
        dsetk = 'dset{0}'.format(c)                   # k means key
        _ = dsets[dsetk] = odict()
        for key in data.keys():
            if re.search(RE, key):
                _.update({key:data[key]})
    return dsets

def get_params(gk, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], gk)
    if 'markers' in pt_dd:
        params['marker'] = U.get_param(pt_dd['markers'], gk)
    if 'labels' in pt_dd:
        params['label'] = U.get_param(pt_dd['labels'], gk)
    else:
        params['label'] = gk
    return params

def decorate_ax(ax, pt_dd):
    if 'grid' in pt_dd:   ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    if 'legend' in pt_dd: ax.legend(**pt_dd['legend'])

    if 'xaxis_ticks' in pt_dd: ax.xaxis.set_ticks(**pt_dd['xaxis_ticks'])
    if 'xticklabels' in pt_dd: ax.set_xticklabels(**pt_dd['xticklabels'])
