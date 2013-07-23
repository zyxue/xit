import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.pyplot as plt

import utils as U

@U.is_plot_type
def pmf(data, A, C, **kw):
    logger.info('start plotting pmf...')

    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)

    fs = pt_dd.get('figsize', (12,9))
    fig = plt.figure(figsize=fs)

    if A.merge:
        ax = fig.add_subplot(111)
        for k, gk in enumerate(data.keys()):
            # DIM of da: (x, 3, y), where x: # of replicas; y: # of bins
            da = data[gk]
            pre_pmfm = da.mean(axis=0)                  # means over x, DIM: (3, y)
            pre_pmfe = U.sem3(da)                   # sems  over x, DIM: (3, y)

            if 'pmf_cutoff' in pt_dd:
                cf = float(pt_dd['pmf_cutoff'])
                bs, es = filter_pmf_data(pre_pmfm, cf)       # get slicing indices
            else:
                bs, es = filter_pmf_data(pre_pmfm)

            bn, pmfm, _ = sliceit(pre_pmfm, bs, es)             # bn: bin; pmfm: pmf mean
            bne, pmfe, _ = sliceit(pre_pmfe, bs, es)            # bne: bin err; pmfe: pmf err

            # pmf sem, equivalent to stats.sem(da, axis=0)
            pmfe = sliceit(pre_pmfe, bs, es)[1] # tricky: 1 corresponds err of pmf mean

            # now, prepare the errobars for the fit
            _pfits, _ks, _l0s = [], [], []
            for subda in da:
                sliced = sliceit(subda, bs, es)
                bn, pm, pe = sliced
                a, b, c = np.polyfit(bn, pm, deg=2)
                _pfv = parabola(bn, a, b, c)                    # pfv: pmf fit values
                _pfits.append(_pfv)
                _ks.append(convert_k(a))
                _l0s.append(-b/(2*a))

            _pfit = np.mean(_pfits, axis=0)
            _k    = np.mean(_ks)                   # prefix it with _ to avoid confusion
            _ke   = U.sem(_ks)
            _l0   = np.mean(_l0s)
            _l0e  = U.sem(_l0s)
            _r2   = calc_r2(pmfm, _pfit)
            _lb   = C['legends'][gk]
            _ky, _kye  = ky(_k, _l0, _ke, _l0e)

        # _txtx, _txty = [float(i) for i in pt_dd['text_coord']]
        # ax.text(_txtx, _txty, '\n'.join(['k   = {0:.1f} +/- {1:.1f} pN/nm'.format(_k, _ke),
        #                                  'l0  = {0:.1f} +/- {1:.2f} nm'.format(_l0, _l0e),
        #                                  'r^2 = {0:.2f}'.format(_r2),
        #                                  'ky  = {0:.1f} +/- {1:.1f} MPa'.format(_ky, _kye)]))

            ax.plot(bn, pmfm, color=C['colors'][gk], label=_lb)
            ax.fill_between(bn, pmfm-pmfe, pmfm+pmfe, 
                            where=None, facecolor=C['colors'][gk], alpha=.3)
            ax.plot(bn, _pfit, '--')
        decorate_ax(ax, pt_dd)

    else:
        col, row = U.gen_rc(len(data.keys()))
        logger.info('col: {0}, row; {1}'.format(col, row))
        for k, gk in enumerate(data.keys()):
            ax = fig.add_subplot(row, col, k+1)
            # da.shape: (x, 3, y), where x: # of replicas; 3: the shape of [bn, pmf, pmf_e],
            # y: # of bn, pmf, or pmf_e of each subgroup
            da = data[gk]
            pre_pmfm = da.mean(axis=0)                  # means over x, DIM: (3, y)
            pre_pmfe = U.sem3(da)                   # sems  over x, DIM: (3, y)

            if 'pmf_cutoff' in pt_dd:
                cf = float(pt_dd['pmf_cutoff'])
                bs, es = filter_pmf_data(pre_pmfm, cf)       # get slicing indices
            else:
                bs, es = filter_pmf_data(pre_pmfm)

            bn, pmfm, _ = sliceit(pre_pmfm, bs, es)             # bn: bin; pmfm: pmf mean
            bne, pmfe, _ = sliceit(pre_pmfe, bs, es)            # bne: bin err; pmfe: pmf err

            # pmf sem, equivalent to stats.sem(da, axis=0)
            pmfe = sliceit(pre_pmfe, bs, es)[1] # tricky: 1 corresponds err of pmf mean

            # now, prepare the errobars for the fit
            _pfits, _ks, _l0s = [], [], []
            for subda in da:
                sliced = sliceit(subda, bs, es)
                bn, pm, pe = sliced
                a, b, c = np.polyfit(bn, pm, deg=2)
                _pfv = parabola(bn, a, b, c)                    # pfv: pmf fit values
                _pfits.append(_pfv)
                _ks.append(convert_k(a))
                _l0s.append(-b/(2*a))

            _pfit = np.mean(_pfits, axis=0)
            _k    = np.mean(_ks)                   # prefix it with _ to avoid confusion
            _ke   = U.sem(_ks)
            _l0   = np.mean(_l0s)
            _l0e  = U.sem(_l0s)
            _r2   = calc_r2(pmfm, _pfit)
            _ky, _kye  = ky(_k, _l0, _ke, _l0e)

            text_params = {}
            text_params.update(**pt_dd['text'])
            ax.text(s = '\n'.join(['k   = {0:.1f} $\pm$ {1:.1f} pN/nm'.format(_k, _ke),
                                   'd$_0$  = {0:.1f} $\pm$ {1:.1f} nm'.format(_l0, _l0e),
                                   'r$^2$ = {0:.2f}'.format(_r2)]),
                                   # 'ky  = {0:.1f} +/- {1:.1f} MPa'.format(_ky, _kye)]),
                    **text_params)

            params = get_params(gk, pt_dd)
            ax.plot(bn, pmfm, **params)
            ax.fill_between(bn, pmfm-pmfe, pmfm+pmfe, 
                            where=None, facecolor=params.get('color'), alpha=.3)

            ax.plot(bn, _pfit, '--', color=params.get('color'))
            decorate_ax(ax, pt_dd)

    plt.savefig(U.gen_output_filename(A, C))

def get_params(gk, pt_dd):
    params = {}
    if 'colors' in pt_dd:
        params['color'] = U.get_param(pt_dd['colors'], gk)
    if 'labels' in pt_dd:
        params['label'] = U.get_param(pt_dd['labels'], gk)
    else:
        params['label'] = gk
    return params


def sliceit(l, b, e):
    l_t = l.transpose()          # (n,3) multi-dimensional data
    s_l = l_t[b:e].transpose()   # (3,n) multi-dimensional data
    return s_l

def filter_pmf(pmf_data, cutoff=2.49):
    """
    try to determine the range of bin when prob_ave < cuttoff, which can be RT (~2.49 KJ/mol)
    return the beginning and ending slices;
    for vacuo, sometimes 2kt needed
    """
    # pdt: pmf_data_transposed, pmf_data should be a (3,n) multi-dimensional
    # array
    pdt = pmf_data.transpose()
    filtered = [d for d in pdt if d[1] < cutoff]
    return np.transpose(filtered)                           # tranpose back

def parabola(x, a, b, c):
    """return the array containing values: a * x^2 + b * x + c"""
    return  (a * x ** 2) + (b * x) + c

def calc_r2(values, fit_values):
    """calculate the correlation coefficients (R^2)"""
    ave = np.average(values)
    sst = sum((i - ave)**2 for i in values)
    ssreg = sum((i - ave)**2 for i in fit_values)
    r_square = float(ssreg) / sst
    return r_square

def convert_k(raw_k):
    # raw_k in KJ/(mol*nm^2)
    Nav= 6.023e23                                              # Avogadro constant
    k = float(raw_k) * 1e3 * 1e9 * 1e12  / Nav                       # unit: pN/nm
    return k

def ky(k, l0, ke=None, l0e=None, cuboid=True):
    """ky calculates the Young Modulus based on my model"""
    # e: means error, used for error propagation
    if cuboid:
        const = (2/3.) ** (1/3.)
    else:
        const = 4

    ky = const * k / l0

    if ke is not None and l0e is not None:
        kye = np.sqrt((l0e/l0) ** 2 + (ke/k) ** 2) * ky
        kye = const * kye
        return ky, kye
    else:
        return ky

def filter_pmf_data(pmf_data, cutoff=2.49):
    """
    try to determine the range of bin when prob_ave < RT, which is
    return the beginning and ending slices
    about 2.49 KJ/mol
    """
    pdt = pmf_data.transpose()

    flag = 1                                                # used as a flag
    slices = []
    # label the data as 1 (wanted) or 0 (unwanted)
    for k, d in enumerate(pdt):
        if flag:
            if d[1] < cutoff:                          # pmf is the second item
                slices.append(k)
                flag = 0
        else:
            if d[1] >= cutoff:
                slices.append(k)
                flag = 1
    print slices
    if len(slices) == 0:
        res = [0, -1]
    elif len(slices) == 1:
        n = slices[0]
        if abs(n - len(pdt)) > len(pdt) / 2.:
            res = [n, -1]
        else:
            res = [0, n]
    elif len(slices) == 2:
        res = slices
    elif len(slices) > 2:
        ds = []
        for k, s in enumerate(slices):
            if k == 0:
                pass
            else:
                ds.append(slices[k] - slices[k-1])
        b = ds.index(max(ds))
        e = b + 1
        res = [slices[b], slices[e]]
    logger.info("beg slice: {0}, end slice: {1}".format(*res))
    return res

def decorate_ax(ax, pt_dd):
    if 'grid' in pt_dd:
        ax.grid(**pt_dd['grid'])
    else:
        ax.grid(which='both')
    if 'xlim' in pt_dd:   ax.set_xlim(**pt_dd['xlim'])
    if 'ylim' in pt_dd:   ax.set_ylim(**pt_dd['ylim'])
    if 'xlabel' in pt_dd: ax.set_xlabel(**pt_dd['xlabel'])
    if 'ylabel' in pt_dd: ax.set_ylabel(**pt_dd['ylabel'])

    if 'legend' in pt_dd: 
        ax.legend(**pt_dd['legend'])

