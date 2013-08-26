import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import matplotlib.pyplot as plt

import utils as U

@U.is_plotmp_type
def mp_alx(data, A, C, **kw):
    """alx for multiple properties (mp)"""
    pt_dd = U.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type)
    dsets = grp_datasets(data, pt_dd)

    fig = plt.figure(figsize=(12,9))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])

    ncol, nrow = U.gen_rc(len(dsets.keys()), pt_dd)
    logger.info('Chosen # of cols: {0}, # of rows; {1}'.format(ncol, nrow))
    for c, sys_key in enumerate(dsets.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        for prop_key in dsets[sys_key]:
            da = dsets[sys_key][prop_key]

            params = get_params(sys_key, prop_key, pt_dd, c)
            ax.plot(da[0], da[1], **params)
            ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                            where=None, facecolor=params.get('color'), alpha=.3)

        if 'texts' in pt_dd:
            ax.text(**U.get_param(pt_dd['texts'], sys_key))

        decorate_ax(ax, pt_dd, ncol, nrow, c)
    plt.savefig(U.gen_output_filename(A, C), **pt_dd.get('savefig', {}))

def get_params(dsetk, prop_key, pt_dd, c):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], prop_key)
    if c == 0:                  # to avoid duplicative legends for all subplots
        if 'labels' in pt_dd:
            params['label'] = U.get_param(pt_dd['labels'], prop_key)
    return params

def grp_datasets(data, pt_dd):
    grp_REs = pt_dd['grp_REs']
    dsets = OrderedDict()
    for c, RE in enumerate(grp_REs):
        for prop_key in data.keys():
            for sys_key in data[prop_key].keys():
                if sys_key not in dsets:
                    dsets[sys_key] = OrderedDict()
                if re.search(RE, prop_key):
                    dsets[sys_key][prop_key] = data[prop_key][sys_key]
    # dsets  = {
    #     'w300/sq1': {
    #         'rdf_c1vp': [array of x, array of y, array of ye],
    #         'rdf_c2vp': [array of x, array of y, array of ye],
    #         'rdf_c3vp': [array of x, array of y, array of ye],
    #         },
    #     'm300/sq1': {
    #         'rdf_c1vp': [array of x, array of y, array of ye],
    #         'rdf_c2vp': [array of x, array of y, array of ye],
    #         'rdf_c3vp': [array of x, array of y, array of ye],
    #         },
    #     }
    return dsets

def decorate_ax(ax, pt_dd, ncol, nrow, c):
    """c: counter"""
    ax.grid(which="major")
    if 'legend' in pt_dd: leg = ax.legend(**pt_dd['legend'])
    if 'xlim' in pt_dd: ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd: ax.set_ylim(**pt_dd['ylim'])

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

    if 'xscale' in pt_dd: ax.set_xscale(pt_dd['xscale'])

    if 'legend_linewidth' in pt_dd:
        for l in leg.legendHandles:
            l.set_linewidth(float(pt_dd['legend_linewidth']))
