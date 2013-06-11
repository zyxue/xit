import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt

import utils as U

@U.is_plot_type
def distr(data, A, C, **kw):
    """data: is an OrderedDict"""
    logger.info('start plotting distr...')

    fig = plt.figure(figsize=(12,9))
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)
    if A.merge:
        ax = fig.add_subplot(111)
        for c, gk in enumerate(data.keys()):
            da = data[gk]
            params = get_params(gk, pt_dd)
            ax.plot(da[0], da[1], **params)
            # facecolor uses the same color as ax.plot
            ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                            where=None, facecolor=params.get('color'), alpha=.3)
        decorate_ax(ax, pt_dd)
    else:
        col, row = U.gen_rc(len(data.keys()))
        for c, gk in enumerate(data.keys()):
            ax = fig.add_subplot(row, col, c+1)
            da = data[gk]
            params = get_params(gk, pt_dd)
            # ax.errorbar(da[0], da[1], yerr=da[2], **params)
            ax.plot(da[0], da[1], **params)
            ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                            where=None, facecolor=params.get('color'), alpha=.3)

            decorate_ax(ax, pt_dd)

    plt.savefig(U.gen_output_filename(A, C))

def get_params(gk, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], gk)
    if 'legends' in pt_dd:
        params['label'] = U.get_param(pt_dd['legends'], gk)
    else:
        params['label'] = gk
    return params

def decorate_ax(ax, pt_dd):
    if 'grid' in pt_dd:   ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    if 'xscale' in pt_dd: ax.set_xscale(**pt_dd['xscale'])
    if 'legend' in pt_dd: ax.legend(**pt_dd['legend'])

    # if 'legend_linewidth' in pt_dd:
    #     for l in leg.legendHandles:
    #         l.set_linewidth(float(pt_dd['legend_linewidth']))
