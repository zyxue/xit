import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt

import utils

@utils.is_plot_type
def distr(data, A, C, **kw):
    """data: is an OrderedDict"""
    logger.info('start plotting distr...')

    fig = plt.figure(figsize=(12,9))
    pt_dd = utils.get_pt_dd(C, A.property, A.plot_type)
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
        col, row = utils.gen_rc(len(data.keys()))
        logger.info('col: {0}, row; {1}'.format(col, row))
        for c, gk in enumerate(data.keys()):
            ax = fig.add_subplot(row, col, c+1)
            da = data[gk]
            params = get_params(gk, pt_dd)
            # ax.errorbar(da[0], da[1], yerr=da[2], **params)
            ax.plot(da[0], da[1], **params)
            ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                            where=None, facecolor=params.get('color'), alpha=.3)

            decorate_ax(ax, pt_dd)

    plt.savefig(utils.gen_output_filename(A, C))

def get_params(gk, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = utils.get_col(utils.get_param(pt_dd['colors'], gk))
    if 'legends' in pt_dd:
        params['label'] = utils.get_param(pt_dd['legends'], gk)
    else:
        params['label'] = gk
    return params

def decorate_ax(ax, pt_dd):
    leg = ax.legend(loc='best')
    ax.grid(which="major")
    if 'xlim' in pt_dd: 
        ax.set_xlim(**utils.float_params(pt_dd['xlim'], 'left', 'right'))
    if 'ylim' in pt_dd:
        ax.set_ylim(**utils.float_params(pt_dd['ylim'], 'bottom', 'top'))
    if 'xlabel' in pt_dd: ax.set_xlabel(pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(pt_dd['ylabel'], labelpad=10)
    if 'xscale' in pt_dd: ax.set_xscale(pt_dd['xscale'])

    if 'legend_linewidth' in pt_dd:
        for l in leg.legendHandles:
            l.set_linewidth(float(pt_dd['legend_linewidth']))
