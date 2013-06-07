import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt

import utils as U
from plot_types import grped_along_var

@U.is_plotmp_type
def mp_grped_along_var(data, A, C, **kw):
    """along a variable, like var2 e.g. solvent"""
    pt_dd = U.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type, A.vv)

    fig = plt.figure(figsize=(12,9))
    if 'subplots_adjust' in pt_dd: fig.subplots_adjust(**pt_dd['subplots_adjust'])

    ncol, nrow = U.gen_rc(len(A.properties), pt_dd)
    for c, pt in enumerate(A.properties):
        dsets = grped_along_var.group_datasets(data[pt], pt_dd['grp_REs'])

        ax = fig.add_subplot(nrow, ncol, c+1)
        grped_along_var.ax_plot(ax, dsets, pt_dd, A)
        decorate_ax(ax, pt_dd, pt, ncol, nrow, c)

    if 'figlegend' in pt_dd:
        leg = fig.legend(handles=ax.lines, **pt_dd['figlegend'])
        if 'legend_linewidth' in pt_dd:
            for _ in leg.legendHandles:
                _.set_linewidth(pt_dd['legend_linewidth'])

    plt.savefig(U.gen_output_filename(A, C))

def decorate_ax(ax, pt_dd, pt, ncol, nrow, c):
    """c: counter"""
    if 'grid' in pt_dd:   ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    if 'legend' in pt_dd: ax.legend(**pt_dd['legend'])
    if 'xscale' in pt_dd: ax.set_xscale(**pt_dd['xscale'])

    # specify text in axis coords (0,0 is lower-left and 1,1 is upper-right
    # http://matplotlib.org/api/axes_api.html?highlight=axes.text#matplotlib.axes.Axes.text
    if 'texts' in pt_dd:  ax.text(
        horizontalalignment='center', verticalalignment='center',
        transform = ax.transAxes, **pt_dd['texts'][pt])

    if c < (ncol * nrow - ncol):
        ax.set_xticklabels([])
        # ax.get_xaxis().set_visible(False)                   # this hide the whole axis
    else:
        if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
        if 'xaxis_ticks' in pt_dd: ax.xaxis.set_ticks(**pt_dd['xaxis_ticks'])
        if 'xticklabels' in pt_dd: ax.set_xticklabels(**pt_dd['xticklabels'])

    if c % ncol == 0:
        if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    else:
        ax.set_yticklabels([])
