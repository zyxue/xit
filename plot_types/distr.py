import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr

import utils as U

@U.is_plot_type
def distr(data, A, C, **kw):
    """data: is an OrderedDict"""
    logger.info('start plotting distr...')

    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)
    fig = plt.figure(figsize=pt_dd.get('figsize', (12,9)))
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
        col, row = U.gen_rc(len(data.keys()), pt_dd)
        for c, gk in enumerate(data.keys()):
            ax = fig.add_subplot(row, col, c+1)
            da = data[gk]
            params = get_params(gk, pt_dd)
            # ax.errorbar(da[0], da[1], yerr=da[2], **params)
            xs, ys, es = da[0], da[1], da[2] # es: errors

            ax.plot(xs, ys, **params)
            ax.fill_between(xs, ys-es, ys+es, 
                            where=None, facecolor=params.get('color'), alpha=.3)

            # do a gaussian fit
            if pt_dd.get('gaussian_fit'):
                # maybe it's better to use p0 for curve_fit
                popt, pcov = curve_fit(gaussian, xs, ys)
                _, mu, sigma = popt
                logger.info('mean of the fitted normal distribution: {0}'.format(mu))
                new_ys = gaussian(xs, *popt)
                # pearsonr creates different value from that by calc_r2
                # corr, p_val = pearsonr(ys, new_ys)
                r2 = U.calc_r2(ys, new_ys)
                ax.plot(xs, new_ys, linewidth="2", 
                        color='black', 
                        label='r$^2$ = {0:.3f}'.format(r2))
                
            decorate_ax(ax, pt_dd)

    output = U.gen_output_filename(A, C)
    logger.info('saving to {0}'.format(output))
    plt.savefig(output)

def get_params(gk, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], gk)
    if 'labels' in pt_dd:
        params['label'] = U.get_param(pt_dd['labels'], gk)
    else:
        params['label'] = gk
    return params

def decorate_ax(ax, pt_dd):
    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
    else:
        ax.grid(which='both')
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    if 'xscale' in pt_dd: ax.set_xscale(**pt_dd['xscale'])
    if 'legend' in pt_dd: 
        ax.legend(**pt_dd['legend'])
    else:
        ax.legend(loc='best')

def gaussian(x, A, mu, sigma):
    # A helps adjust the normalization
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

