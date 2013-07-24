import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

import utils as U

"""
rama is different from simple 2D histogram since the x & y (i.e. phi, psi) are
always closely together. Therefore, we need a separate function rama here
independent of histo2D
"""

@U.is_plot_type
def rama(data, A, C, **kw):
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type, A.v)
    ncol, nrow = U.gen_rc(len(data.keys()), pt_dd)

    # ncol * 8 instead of 6 is because color bar will squeeze the subplot
    # otherwise.
    fig = plt.figure(figsize=(ncol*8, nrow*6))
    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])

    bins = pt_dd.get('bins', 36)
    normed = pt_dd.get('normed', False)
    contours = []
    max_ = 0
    for c, gk in enumerate(data.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        da = data[gk]

        phis, psis = da
        h, phip, psip = np.histogram2d(psis, phis, range=[[-180,180], [-180,180]], 
                                       bins=bins, normed=normed)
        phip = (phip[1:] + phip[:-1]) / 2.
        psip = (psip[1:] + psip[:-1]) / 2.

        cmap = getattr(cm, pt_dd.get('cmap', 'gray_r'))
        contour = ax.contourf(phip, psip, h, cmap=cmap)
        fig.colorbar(contour, shrink=0.6, extend='both')

        contours.append(contour)
    
        decorate_ax(ax, pt_dd, ncol, nrow, c, gk, A)

        _ = max(phip.max(), psip.max())
        if _ > max_:
            max_ = _

    for _ in contours:
        _.set_clim(0, max_)

    plt.savefig(U.gen_output_filename(A, C), **pt_dd.get('savefig', {}))

@U.is_plot_type
def rama_pmf(data, A, C, **kw):
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type, A.v)
    if not pt_dd:
        # if there is no rama_pmf, search for rama instead, this is trying to
        # reduce duplication in .xitconfig.yaml
        pt_dd = U.get_pt_dd(C, A.property, 'rama', A.v)
    print pt_dd

    ncol, nrow = U.gen_rc(len(data.keys()), pt_dd)
    fig = plt.figure(figsize=(ncol*7, nrow*6))

    if 'subplots_adjust' in pt_dd:
        fig.subplots_adjust(**pt_dd['subplots_adjust'])

    bins = pt_dd.get('bins', 180)
    normed = pt_dd.get('normed', False)
    contours = []

    cutoff = pt_dd.get('cutoff', np.inf)
    if cutoff == np.inf:
        max_ = None
    else:
        max_ = cutoff
    for c, gk in enumerate(data.keys()):
        ax = fig.add_subplot(nrow, ncol, c+1)
        da = data[gk]

        phis, psis = da

        # the order switch of psis and phis is due to implementation of
        # histogram2d(), only after switch will the finally plot match what is
        # expected
        h, phi_edges, psi_edges = np.histogram2d(
            psis, phis, range=[[-180,180], [-180,180]], 
            bins=bins, normed=normed)
        phi_edges = (phi_edges[1:] + phi_edges[:-1]) / 2.
        psi_edges = (psi_edges[1:] + psi_edges[:-1]) / 2.

        h_pmf = U.prob2pmf(h, h.max())

        # lenx, leny = h_pmf.shape # len: length
        # for _i in range(lenx):
        #     for _j in range(leny):
        #         if h_pmf[_i][_j] == np.inf:
        #             h_pmf[_i][_j] = -np.inf
        # faster then the above looping
        np.place(h_pmf, h_pmf>=cutoff, -np.inf)

        cmap = getattr(cm, pt_dd.get('cmap', 'jet'))
        # this step can a while
        F = U.timeit(ax.contourf)
        contour = F(phi_edges, psi_edges, h_pmf, cmap=cmap)
        fig.colorbar(contour, shrink=0.6, extend='both')

        contours.append(contour)
    
        decorate_ax(ax, pt_dd, ncol, nrow, c, gk, A)

        if cutoff == np.inf:
            ma = h_pmf.max()
            if max_ is None or ma > max_:
                max_ = ma

    for _ in contours:
        _.set_clim(0, max_)

    plt.savefig(U.gen_output_filename(A, C), **pt_dd.get('savefig', {}))

@U.timeit
def decorate_ax(ax, pt_dd, ncol, nrow, c, gk, A):
    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
    else:
        ax.grid(which='both')

    if c < (ncol * nrow - ncol):
        ax.set_xticklabels([])
        # ax.get_xaxis().set_visible(False)                   # this hide the whole axis
    else:
        if 'xlabel' in pt_dd: 
            ax.set_xlabel(**pt_dd['xlabel'])
        else:
            ax.set_xlabel('$\phi$')

    if c % ncol == 0:
        if 'ylabel' in pt_dd:
            ax.set_ylabel(**pt_dd['ylabel'])
        else:
            ax.set_ylabel('$\psi$')
    else:
        ax.set_yticklabels([])

    if 'xlim' in pt_dd:
        ax.set_xlim(**pt_dd['xlim'])
    else:
        ax.set_xlim([-180, 180])
    if 'ylim' in pt_dd:
        ax.set_ylim(**pt_dd['ylim'])
    else:
        ax.set_ylim([-180, 180])

    if 'titles' in pt_dd:
        ax.set_title(U.get_param(pt_dd['titles'], gk))
    else:
        ax.set_title(gk + '_' + A.property)
