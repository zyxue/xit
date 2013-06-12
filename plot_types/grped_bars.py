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
    dsets = grp_datasets(data, grp_REs)

    bar_width = pt_dd.get('bar_width', 1)
    nbars_per_cluster = len(dsets.keys())
    nclusters = len(data) / nbars_per_cluster
    logger.info('number of clusters: {0}; # bars per cluster: {1}'.format(nclusters, nbars_per_cluster))
    cluster_width = bar_width * nbars_per_cluster

    # space between neigbouring groups of bars
    spacing = pt_dd.get('spacing', 0.35)

    xlocs = np.arange(0, nclusters * (cluster_width + spacing), cluster_width + spacing)
    print xlocs

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    rectss = []                                             # plural of rects
    for c, dsetk in enumerate(dsets.keys()):
        dset = dsets[dsetk]
        for cc, kk in enumerate(dset.keys()):
            mean = dset[kk][0]
            std  = dset[kk][1]
            params = get_params(kk, pt_dd)
            if cc != len(dset.keys()) - 1 and 'label' in params.keys():
                # since you just need one legend for all set of bars
                params.pop('label')
            
            xloc = xlocs[cc] + c * bar_width
            rects = ax.bar(xloc, mean, bar_width, yerr=std, **params)
            rectss.append(rects)

    ax.set_xticks(xlocs + cluster_width / 2.)

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%float(height),
                    ha='center', va='bottom')

    for rects in rectss:
        autolabel(rects)

    decorate_ax(ax, pt_dd)
    plt.savefig(U.gen_output_filename(A, C))

    dsets = OrderedDict() # dsets: meaning further grouping, based on which ploting
                  # will be done

def grp_datasets(data, grp_REs):
    dsets = OrderedDict()
    # structure of dsets: dict of dict of dict ...
    # dset = {
    #     'dset0': {
    #         'groupkey0': ('mean0', 'std0'),
    #         'groupkey1': ('mean1', 'std1'),
    #         ...
    #         },
    #     'dset1': {
    #         'groupkey0': ('mean0', 'std0'),
    #         'groupkey1': ('mean1', 'std1'),
    #         ...
    #         },
    #     ...
    #     }
        
    for c, RE in enumerate(grp_REs):
        dsetk = 'dset{0}'.format(c)                   # k means key
        _ = dsets[dsetk] = OrderedDict()
        for key in data.keys():
            if re.search(RE, key):
                _.update({key:data[key]})
    return dsets

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
    if 'grid' in pt_dd:   ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])
    if 'legend' in pt_dd: ax.legend(**pt_dd['legend'])

    if 'xticklabels' in pt_dd:
        ax.set_xticklabels(**pt_dd['xticklabels'])
