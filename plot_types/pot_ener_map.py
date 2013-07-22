import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

import utils as U

@U.is_plot_type
def pot_ener_map(data, A, C, **kw):
    adjust_minima(data)

    logger.info('start potential energy map...')
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)
    
    fig = plt.figure(figsize=pt_dd.get('figsize', (12,9)))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])

    ncol, nrow = U.gen_rc(len(data.keys()), pt_dd)

    for c, gk in enumerate(data.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        [phis, psis], da = data[gk]

        # this is just for determining the proper levels
        logger.info('min, max of the original map: {0}, {1}'.format(da.min(), da.max()))

        # further process da, mainly about removing peaks
        if 'levels' in pt_dd:
            min_, max_, step = pt_dd['levels']
            for i in range(da.shape[0]):
                for j in range(da.shape[1]):
                    v = da[i][j]
                    if v > max_:
                        da[i][j] = min_ - 100 * step # make it white arbitrarily

        params = get_params(gk, pt_dd)

        contour = ax.contourf(phis, psis, da, **params)
        plt.colorbar(contour, shrink=0.6, extend='both')
        decorate_ax(ax, gk, pt_dd, ncol, nrow, c)

    plt.savefig(U.gen_output_filename(A, C), **pt_dd.get('savefig', {}))

def get_params(gk, pt_dd):
    params = {}
    if 'cmaps' in pt_dd:
        params['cmap'] = getattr(cm, U.get_param(pt_dd['cmaps'], gk))
    if 'levels' in pt_dd:
        _ = U.get_param(pt_dd['levels'], gk)
        if _: 
            min_, max_, step = _
            # +1 so that max_ will be included in the final levels
            params['levels'] = range(min_, max_+1, step)

    # the potential energy map usually does not need color and label decoration
    return params

def decorate_ax(ax, gk, pt_dd, ncol, nrow, c):
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

    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
    else:
        ax.grid(which='both')
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xscale' in pt_dd: ax.set_xscale(**pt_dd['xscale'])
    if 'titles' in pt_dd:
        ax.set_title(U.get_param(pt_dd['titles'], gk))


def adjust_minima(data):
    """adjust the minmum values of data and make them have the same minimum"""
    if len(data.keys()) <= 1:
        return

    das = [data[i][1] for i in data.keys()]

    diff = [0]
    for i in das[1:]:
        diff.append(das[0].min() - i.min())

    logger.info('diff between minima: {0}'.format(diff))

    for k, key in enumerate(data.keys()):
        data[key][1] = data[key][1] + diff[k]
