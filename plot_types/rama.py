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
    col, row = U.gen_rc(len(data.keys()))
    fig = plt.figure(figsize=(col*6, row*6))
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)

    for c, gk in enumerate(data.keys()):
        ax = fig.add_subplot(row, col, c+1)
        da = data[gk]

        psis, phis = da # the order of phi, psi produced by g_rama is probably wrong. --2013-06-11
        h, phip, psip = np.histogram2d(phis, psis, range=[[-180,180], [-180,180]], bins=36)
        phip = (phip[1:] + phip[:-1]) / 2.
        psip = (psip[1:] + psip[:-1]) / 2.
        contour = ax.contourf(phip, psip, h, cmap=cm.gray_r)

        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
    
    # plt.colorbar(contour, shrink=0.6, extend='both')
    plt.savefig(U.gen_output_filename(A, C))

    # if 'bins' in pt_dd:
    #     i, j, s = [float(_) for _ in pt_dd['bins']]
    #     bins = np.arange(i, j, s)
    # else:
    #     # assume usually 36 bins would be enough
    #     bins = np.linspace(_la.min(), _la.max(), 36)
