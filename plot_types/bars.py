import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import numpy as np
from pprint import pformat

import utils

@utils.is_plot_type
def bars(grps, A, C, **kw):
    dd = utils.get_pt_dd(C, A.property, A.plot_type)
    logger.debug('\n{0}'.format(pformat((dict(grps)))))
    bar_width = 1.
    type_of_bars = 1                 # i.e. w, m
    space = 0.35                     # space between neigbouring groups of bars

    # x coordinates for bars
    min_, max_ = 0, len(grps.items()) * (bar_width * type_of_bars + space)
    step  = bar_width * type_of_bars + space
    xlocs = np.arange(min_, max_, step)[:len(grps.items())]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    means = [i[0] for i in grps.values()]
    stds  = [i[1] for i in grps.values()]

    ax.bar(xlocs, means, bar_width, yerr=stds,
           color='white', hatch="\\")

    # decorate a bit
    ax.set_xlim((0 - 2 *space), (len(grps.items()) * (bar_width * type_of_bars + space) + space))
    ax.set_xticks(xlocs + bar_width/2.)                     # /2. to make it in the middle
    ax.set_xticks(xlocs + bar_width/2.)                     # /2. to make it in the middle
    ax.grid(which="major", axis='y')

    if 'grid' in dd:   ax.grid(**dd['grid'])
    if 'xlim' in dd:   ax.set_xlim(**dd['xlim'])
    if 'ylim' in dd:   ax.set_ylim(**dd['ylim'])
    if 'xlabel' in dd: ax.set_xlabel(**dd['xlabel'])
    if 'ylabel' in dd: ax.set_ylabel(**dd['ylabel'])
    if 'title' in dd:  ax.set_title(**dd['title'])
    if 'legend' in dd: ax.legend(**dd['legend'])

    if 'xticklabels' in dd:
        ax.set_xticklabels(**dd['xticklabels'])
    else:
        ax.set_xticklabels(grps.keys(), rotation=20)

    plt.savefig(utils.gen_output_filename(A, C))
