import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import matplotlib.pyplot as plt

import utils

@utils.is_plotmp_type
def xy(data, A, C, **kw):
    """
    data structure of data, an OrderedDict
    data = {
        'x': {
            'groupkey0': [mean0,  std0],
            'groupkey1': [mean1,  std1],
            ...
            },
        'y': {
            'groupkey0': [mean0,  std0],
            'groupkey1': [mean1,  std1],
            ...
            }
        }
    """

    pt_dd = utils.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type)
    xp, yp = A.properties                                   # e.g. upup, unun
    xdata, ydata = data[xp], data[yp]

    # x, y means and errors
    xms, xes, yms, yes = [], [], [], []
    for c, key in enumerate(xdata.keys()):
        # xdata and ydata must have the same keys()
        xms.append(xdata[key][0])
        xes.append(xdata[key][1])
        yms.append(ydata[key][0])
        yes.append(ydata[key][1])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for xm, xe, ym, ye in zip(xms, xes, yms, yes):
        ax.errorbar(xm, ym, xerr=xe, yerr=ye)

    decorate_ax(ax, pt_dd)
    plt.savefig(utils.gen_output_filename(A, C))

def grp_datasets(data, pt_dd):
    grp_REs = pt_dd['grp_REs']
    dsets = OrderedDict()
    for c, RE in enumerate(grp_REs):
        dsetk = 'dset{0}'.format(c)
        dsets[dsetk] = OrderedDict()
        for k in data.keys():
            _ = dsets[dsetk][k] = OrderedDict()
            for kk in data[k].keys():
                if re.search(RE, kk):
                    _[kk] = data[k][kk]
    # data structure
    # dsets = {
    #     'dset0': {
    #         'x': {
    #             'groupkey0': [mean0, std0],
    #             'groupkey1': [mean1, std1],
    #              ...
    #             },
    #         'y': {
    #             'groupkey0': [mean0, std0],
    #             'groupkey1': [mean1, std1],
    #              ...
    #             },
    #         },
    #     'dset1': {
    #         'x': {
    #             'groupkey0': [mean0, std0],
    #             'groupkey1': [mean1, std1],
    #              ...
    #             },
    #         'y': {
    #             'groupkey0': [mean0, std0],
    #             'groupkey1': [mean1, std1],
    #              ...
    #             },
    #         }
    #     ...
    #     }
    return dsets

@utils.is_plotmp_type
def grped_xy(data, A, C, **kw):
    pt_dd = utils.get_pt_dd(C, '_'.join(A.properties), A.plotmp_type)
    dsets = grp_datasets(data, pt_dd)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for dk in dsets.keys():
        dset = dsets[dk]
        xp, yp = A.properties

        if sorted([xp, yp]) == ['unv', 'upv']:                # this is plot specific
            ax.plot([0,1], [0,1], '--')

        xda, yda = dset[xp], dset[yp]                       # da: data

        # denormx = [float(i) for i in pt_dd.get('denormx', [1] * len(xdata.keys()))]
        # denormy = [float(i) for i in pt_dd.get('denormy', [1] * len(xdata.keys()))]

        k1, k2 = xda.keys()             # ONLY deal with two members in a group (e.g. w, m)
        x1, x2 = xda[k1], xda[k2]
        y1, y2 = yda[k1], yda[k2]

        # DEPRECATED! normalization should be done in plot.py, this is left
        # here for remembering the bad design
        # if 'denormx' in pt_dd:
        #     dx1 = float(pt_dd['denormx'][k1])               # dx: denormx
        #     dx2 = float(pt_dd['denormx'][k2])
        #     x1, x2 = x1 / dx1, x2 / dx2
        # if 'denormy' in pt_dd:
        #     dy1 = float(pt_dd['denormy'][k1])               # dy: denormy
        #     dy2 = float(pt_dd['denormy'][k2])
        #     y1, y2 = y1 / dy1, y2 / dy2

        params1, params2 = {}, {}
        if 'markers' in pt_dd:
            params1['marker'] = pt_dd['markers'][k1]
            params2['marker'] = pt_dd['markers'][k2]

        if 'colors' in pt_dd:
            params1['color'] = pt_dd['colors'][k1]
            params2['color'] = pt_dd['colors'][k2]
        
        ax.errorbar(x1[0], y1[0], xerr=x1[1], yerr=y1[1], **params1)
        ax.errorbar(x2[0], y2[0], xerr=x2[1], yerr=y2[1], **params2)
        
        ax.annotate("",
                    # STRANGE! the order need to be reversed                                   
                    xy=(x2[0], y2[0]), xycoords='data',                                        
                    xytext=(x1[0], y1[0]), textcoords='data',                                  
                    arrowprops=dict(arrowstyle="fancy", #linestyle="dashed",                   
                                    color="purple",                                            
                                    alpha=0.5,                                                 
                                    shrinkA=10,                                                
                                    shrinkB=10,                                                
                                    connectionstyle="arc3,rad=-0.3",                           
                                    ),
                    )

    decorate_ax(ax, pt_dd)


    plt.savefig(utils.gen_output_filename(A, C))

def decorate_ax(ax, pt_dd):
    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
    if 'xlim' in pt_dd: 
        ax.set_xlim(**utils.float_params(pt_dd['xlim'], 'left', 'right'))
    if 'ylim' in pt_dd:
        ax.set_ylim(**utils.float_params(pt_dd['ylim'], 'bottom', 'top'))
    if 'xlabel' in pt_dd: 
        ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: 
        ax.set_ylabel(**pt_dd['ylabel'])
