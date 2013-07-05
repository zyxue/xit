import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict
import pprint

import matplotlib.pyplot as plt

import utils

@utils.is_plot_type
def grped_distr(data, A, C, **kw):
    """
    data structure of data, an OrderedDict
    data = {
        'groupkey0': [[array of bn0, , array of psm0, array of pse0], [mean0, std0]],
        'groupkey1': [[array of bn1, , array of psm1, array of pse1], [mean1, std1]],
        ...
        }
    """

    logger.info('start plotting {0} for \n{1}'.format(A.plot_type, pprint.pformat(data.keys())))

    # This is trying to avoid duplication in .xitconfig, but not very elegant
    if A.plot_type in ['grped_distr', 'grped_distr_ave']:
        _ = 'grped_distr'
    elif A.plot_type in ['grped_alx']:
        _ = 'grped_alx'

    pt_dd = utils.get_pt_dd(C, A.property, _)

    dsets = grp_datasets(data,  pt_dd)

    fig = plt.figure(figsize=pt_dd.get('figsize', (12,9)))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])

    ncol, nrow = utils.gen_rc(len(dsets.keys()))
    logger.info('Chosen # of cols: {0}, # of rows; {1}'.format(ncol, nrow))
    for c, dsetk in enumerate(dsets.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        dset = dsets[dsetk]
        if 'text' in dset:
            ax.text(s=dset['text'], **pt_dd['text'])
        for kkey in dset['data']: # ind: individual
            da = dset['data'][kkey]
            params = get_params(kkey, pt_dd)
            if A.plot_type in ['grped_distr', 'grped_alx']:
                ax.plot(da[0], da[1], **params)
                # facecolor uses the same color as ax.plot
                ax.fill_between(da[0], da[1]-da[2], da[1]+da[2], 
                                where=None, facecolor=params.get('color'), alpha=.3)
            elif A.plot_type == 'grped_distr_ave':
                # the data slicing can be confusing, refer to plot.py to see how to
                # data is structured
                ax.plot(da[0][0], da[0][1], **params)
                # facecolor uses the same color as ax.plot
                ax.fill_between(da[0][0], da[0][1]-da[0][2], da[0][1]+da[0][2], 
                                where=None, facecolor=params.get('color'), alpha=.3)

                # now, plot the vertical bar showing the average value
                m = da[1][0]    # mean
                e = da[1][1]    # error
                ax.plot([m,m], [0,1], color=params.get('color'))
                ax.fill_betweenx([0,1], [m-e, m-e], [m+e, m+e],
                                 where=None, facecolor=params.get('color'), alpha=.3)

        # plot a vertical line if needed, e.g. showing the time of convergence
        if 'vline' in pt_dd:
            vl = pt_dd['vline']
            x = vl['x']
            if 'y' in vl:
                yb, ye = vl['y']
            else:
                yb, ye = ax.get_ylim()
            ax.plot([x, x], [yb, ye], **vl.get('vline_params', {}))

        decorate_ax(ax, pt_dd, ncol, nrow, c)

        # specific case
        if (A.property == 'rg_c_alpha_wl' 
            and dsetk == 'dset0' 
            and A.plot_type == 'grped_alx'
            and sorted(dset['data'].keys()) == ['m300/sq1', 'w300/sq1']):
            print "DO something special"
            ax.set_xlim([0, 500])
            ax.set_xticklabels([str(i) for i in xrange(0,600, 100)])
            for tick in ax.xaxis.get_major_ticks():
                tick.label1On = False
                tick.label2On = True # move the ticks to the top 

    if 'figlegend' in pt_dd:
        leg = fig.legend(handles=ax.lines, **pt_dd['figlegend'])
        if 'legend_linewidth' in pt_dd:
            for _ in leg.legendHandles:
                _.set_linewidth(pt_dd['legend_linewidth'])

    plt.savefig(utils.gen_output_filename(A, C))

def grp_datasets(data, pt_dd):
    grp_REs = pt_dd['grp_REs']
    dsets = OrderedDict()
    for c, RE in enumerate(grp_REs):
        dsetk = 'dset{0}'.format(c)                   # dsetk: dataset key 
        _ = dsets[dsetk] = OrderedDict()
        _['data'] = OrderedDict()
        for key in data.keys():
            if re.search(RE, key):
                _['data'][key] = data[key]
        if 'texts' in pt_dd:
            _.update(text=pt_dd['texts'][c])
    # structure of dsets: dict of dict of dict ...
    # dsets = {
    #     'dset0': {
    #         'data': [
    #             'groupkey0': [[array of bn0, , array of psm0, array of pse0], [mean0, std0]],
    #             'groupkey1': [[array of bn1, , array of psm1, array of pse1], [mean1, std1]],
    #             ...
    #             },
    #         'color': 'red',
    #         ...
    #         },
    #     'dset1': {
    #         'data': {
    #             'groupkey0': [[array of bn0, , array of psm0, array of pse0], [mean0, std0]],
    #             'groupkey1': [[array of bn1, , array of psm1, array of pse1], [mean1, std1]],
    #             ...
    #             },
    #         'color': 'blue',
    #         ...
    #         },
    #     ...
    #     }
    return dsets

@utils.is_plot_type
def grped_distr_ave(data, A, C, **kw):
    """it's a variant of grped_distr by adding mean values in the distribution plot """
    grped_distr(data, A, C, **kw)

def get_params(key, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = utils.get_param(pt_dd['colors'], key)
    if 'labels' in pt_dd:
        params['label'] = utils.get_param(pt_dd['labels'], key)
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
