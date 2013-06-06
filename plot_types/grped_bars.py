import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np

import utils as U

@U.is_plot_type
def grped_bars(data, A, C, **kw):
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)
    grp_REs = pt_dd['grp_REs']
    dsets = OrderedDict() # dsets: meaning further grouping, based on which ploting
                  # will be done

    # structure of dsets: dict of dict of dict ...
    # dset = {
    #     'dset0': {'data': [
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #                  'color': 'red',
    #                  ...
    #                  },
    #     'dset1': {'data': {
    #             'groupkey0': ('mean0', 'std0'),
    #             'groupkey1': ('mean1', 'std1'),
    #             ...
    #             },
    #                  'color': 'blue',
    #                  ...
    #                  },
    #     ...
    #     }
        
    for c, RE in enumerate(grp_REs):
        dsetk = 'dset{0}'.format(c)                   # k means key
        _ = dsets[dsetk] = {}
        _['data'] = OrderedDict()
        for key in data.keys():
            if re.search(RE, key):
                _['data'].update({key:data[key]})
        if 'colors' in pt_dd:
            _.update(color=U.get_col(pt_dd['colors'][c]))
        if 'legends' in pt_dd:
            _.update(legend=pt_dd['legends'][c])

    bar_width = 1.
    type_of_bars = len(dsets)   # i.e. w, m
    space = 0.35                     # space between neigbouring groups of bars  

    xlocs = np.arange(0, (len(data) / type_of_bars) * (bar_width * type_of_bars + space),
                      bar_width * type_of_bars + space)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    rectss = []                                             # plural of rects
    for k, dsetk in enumerate(dsets.keys()):
        dset = dsets[dsetk]
        means = [_[0] for _ in dset['data'].values()]
        stds  = [_[1] for _ in dset['data'].values()]
        if 'denorminators' in pt_dd:
            denorms = [float(i) for i in pt_dd['denorminators']]
            normalize = lambda x: [i/d for (i, d) in zip(x, denorms)]
            means = normalize(means)
            stds  = normalize(stds)
        rects = ax.bar(xlocs+(k * bar_width), means, bar_width, yerr=stds,
                       color=dset.get('color'),
                       label=dset.get('legend'))
        rectss.append(rects)

    ax.grid(which="major", axis='y')
    ax.set_xticks(xlocs + bar_width)

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%float(height),
                    ha='center', va='bottom')

    for rects in rectss:
        autolabel(rects)

    if 'ylim' in pt_dd:
        ax.set_ylim(**U.float_params(pt_dd['ylim'], 'bottom', 'top'))
    if 'xlabel' in pt_dd: 
        ax.set_xlabel(pt_dd['xlabel'])
    if 'ylabel' in pt_dd:
        ax.set_ylabel(**U.float_params(pt_dd['ylabel'], 'labelpad'))
    if 'xticklabels' in pt_dd:
        ax.set_xticklabels(**pt_dd['xticklabels'])
    if 'title' in pt_dd:
        ax.set_title(pt_dd['title'])
    if 'legends' in pt_dd: 
        ax.legend(loc='best')

    plt.savefig(U.gen_output_filename(A, C))
