import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict as odict

import matplotlib.pyplot as plt
import numpy as np

import utils as U

"""
plot 2 properties in one axes using along_var, e.g. rg_c_alpha upup along
temperature in vacuo
"""

@U.is_plotmp_type
def grped_along_var_2prop(data, A, C, **kw):
    pt_dd = U.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type)
    dsets = group_datasets(data, pt_dd['grp_REs'])

    fig = plt.figure()
    for c, propi in enumerate(dsets.keys()):
        i = c+1                 # i tracks whether it's prop1 or prop2
        subdsets = dsets[propi]
        if c == 0:
            ax1 = fig.add_subplot(111)            
            ax_plot(ax1, subdsets, pt_dd, A, i)
            decorate_ax(ax1, pt_dd, i)
        else:
            ax2 = ax1.twinx()
            ax_plot(ax2, subdsets, pt_dd, A, i)
            decorate_ax(ax2, pt_dd, i)
    plt.savefig(U.gen_output_filename(A, C))

def ax_plot(ax, dsets, pt_dd, A, i):
    """i tracks whether it's prop1 or prop2"""
    for c, dsetk in enumerate(dsets.keys()):
        dset = dsets[dsetk]
        means = np.array([dset[kk][0] for kk in dset.keys()])
        stds  = np.array([dset[kk][1] for kk in dset.keys()])
        params = get_params(dsetk, pt_dd, i)
        if A.v: logger.info('params for {0}: {1}'.format(dsetk, params))
        xs = pt_dd.get('xs', range(len(dset.keys())))
        ax.plot(xs, means, **params)
        ax.fill_between(xs, means-stds, means+stds,
                        where=None, facecolor=params.get('color'), alpha=0.3)

def group_datasets(data, grp_REs):
    dsets = odict() # dsets: meaning further grouping, based on which
                          # ploting will be done
    # Structure of dsets: dict of dict of dict ...
    # dset = {
    #     'prop1': {
    #         'dset0': {
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #         'dset1': {
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #         ...
    #         },
    #     'prop2':{
    #         'dset0': {
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #         'dset1': {
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #         ...
    #         }
    #     }
        
    for propi in data.keys():
        dsets[propi] = odict()
        for c, RE in enumerate(grp_REs):
            dsetk = 'dset{0}'.format(c)                   # k means key
            _ = dsets[propi][dsetk] = odict()
            for key in data[propi].keys():
                if re.search(RE, key):
                    _.update({key:data[propi][key]})
    return dsets

def get_params(gk, pt_dd, i):
    params = {}
    _ = 'colors{0}'.format(i)
    if _ in pt_dd:
        params['color'] = U.get_param(pt_dd[_], gk)

    _ = 'markers{0}'.format(i)
    if _ in pt_dd:
        params['marker'] = U.get_param(pt_dd[_], gk)

    _ = 'labels{0}'.format(i)
    if _ in pt_dd:
        params['label'] = U.get_param(pt_dd[_], gk)
    else:
        params['label'] = gk
    return params

def decorate_ax(ax, pt_dd, i):
    _ = 'grid{0}'.format(i)
    if _ in pt_dd: ax.grid(**pt_dd[_])
    _ = 'xlim{0}'.format(i)
    if _ in pt_dd: ax.set_xlim(**pt_dd[_])
    _ = 'ylim{0}'.format(i)
    if _ in pt_dd: ax.set_ylim(**pt_dd[_])
    _ = 'xlabel{0}'.format(i)
    if _ in pt_dd: ax.set_xlabel(**pt_dd[_])
    _ = 'ylabel{0}'.format(i)
    if _ in pt_dd: ax.set_ylabel(**pt_dd[_])
    _ = 'legend{0}'.format(i)
    if _ in pt_dd: ax.legend(**pt_dd[_])
