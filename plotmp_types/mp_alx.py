import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import matplotlib.pyplot as plt

import utils

@utils.is_plotmp_type
def mp_alx(data, A, C, **kw):
    """alx for multiple properties (mp)"""
    pt_dd = utils.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type)
    dsets = grp_datasets(data, pt_dd)

    fig = plt.figure(figsize=(12,9))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**utils.float_params(
                pt_dd['subplots_adjust'], 'hspace', 'wspace'))

    ncol, nrow = utils.gen_rc(len(dsets.keys()))
    logger.info('Chosen # of cols: {0}, # of rows; {1}'.format(ncol, nrow))
    for c, sys_key in enumerate(dsets.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        for prop_key in dsets[sys_key]:
            da = dsets[sys_key][prop_key]

            params = get_params(sys_key, prop_key, pt_dd)
            ax.plot(da[0], da[1], **params)
            ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                            where=None, facecolor=params.get('color'), alpha=.3)

        if 'texts' in pt_dd:
                ax.text(**utils.float_params(pt_dd['texts'][sys_key], 'x', 'y'))

        decorate_ax(ax, pt_dd, ncol, nrow, c)
    plt.savefig(utils.gen_output_filename(A, C))

def get_params(dsetk, prop_key, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = pt_dd['colors'][prop_key]
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
    if 'legends' in pt_dd:
        leg = ax.legend(loc='best')
    if 'xlim' in pt_dd: 
        ax.set_xlim(**utils.float_params(pt_dd['xlim'], 'left', 'right'))
    if 'ylim' in pt_dd:
        ax.set_ylim(**utils.float_params(pt_dd['ylim'], 'bottom', 'top'))

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
