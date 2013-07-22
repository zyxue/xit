import sys
import os
import re
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import numpy as np
from tables.exceptions import NoSuchNodeError

# from scipy import stats

import prop
import utils as U
import plot_types

"""Normalization should happen here rather than during plotting!!!"""

def plot(A, C, core_vars):
    h5 = U.get_h5(A, C)
    prop_obj = prop.Property(A.property)
    data = OrderedDict()
    grps = groupit(core_vars, prop_obj, A, C, h5)
    logger.info("Groups: {0}".format(grps.keys()))

    calc_fetch_or_overwrite(grps, prop_obj, data, A, C, h5)

    func = plot_types.PLOT_TYPES[A.plot_type]
    func(data, A, C)

def calc_fetch_or_overwrite(grps, prop_obj, data, A, C, h5):
    """data should be a empty OrderedDict"""
    CALC_TYPE_MAPPING = U.reverse_mapping(
        {(calc_means, 'means'): ['bars', 'grped_bars', 'xy', 'grped_xy', 
                                 'grped_along_var', 'mp_grped_along_var', 'grped_along_var_2prop'],
         (calc_alx, 'alx'): ['alx', 'grped_alx', 'mp_alx'],
         (calc_distr, 'distr'): ['distr', 'grped_distr'],
         (calc_distr_ave, 'distr_ave'): ['grped_distr_ave'],
         (calc_imap, 'imap'): ['imap'],
         (calc_pmf, 'pmf'): ['pmf'],
         (calc_omega_distr, 'omega_distr'): ['grped_omega_distr'],



         # this is a quite specific type of analysis
         (calc_pot_ener_map, 'pot_ener_map'): ['pot_ener_map'],

         # rama cannot be calculated and stored because the result dtype would
         # be object, and their shape would be of different dimensions,
         # .e.g. np.array([h, phip, psip]).shape: (10, 10) (10,) (10,)
         (get_rama, 'rama'): ['rama'],
         })

    for c, gk in enumerate(grps):
        if A.v: logger.info('processing Group {0}: {1}'.format(c, gk))
        # ar: array
        for _ in ['plot_type', 'plotmp_type']:
            if hasattr(A, _):
                pt = getattr(A, _) # pt: plot_type or plotmp_type
                if A.v: logger.info('{0} detected'.format(pt))

        try:
            calc_type_func, calc_type = CALC_TYPE_MAPPING[pt]
        except KeyError:
            print 'Do not know how to calculate "{0}"'.format(pt)
            sys.exit(255)

        ar_name = '{0}_{1}'.format(calc_type, prop_obj.name)
        ar_where = os.path.join('/', gk)
        ar_whname = os.path.join(ar_where, ar_name)
        prop_dd = U.get_prop_dd(C, prop_obj.name)
        if h5.__contains__(ar_whname):
            if not A.overwrite:
                if A.v: logger.info('fetching subdata from precalculated result')
                sda = h5.getNode(ar_whname).read()     # sda: subdata
            else:
                if A.v: logger.info('overwriting old subdata with new ones')
                _ = h5.getNode(ar_whname)
                _.remove()
                ar = calc_type_func(h5, gk, grps[gk], prop_obj, prop_dd, A, C)
                h5.createArray(where=ar_where, name=ar_name, object=ar)
                sda = ar
        else:
            if A.v: logger.info('Calculating subdata...')
            ar = calc_type_func(h5, gk, grps[gk], prop_obj, prop_dd, A, C)
            if ar.dtype.name != 'object':
                # cannot be handled by tables yet, but it's fine not to store
                # it because usually object is a combination of other
                # calculated properties, which are store, so fetching them is
                # still fast
                print ar_where
                h5.createArray(where=ar_where, name=ar_name, object=ar)
            else:
                logger.info('"{0}" dtype number array CANNNOT be stored in h5'.format(ar.dtype.name))
            sda = ar
        data[gk] = sda

@U.timeit
def calc_pot_ener_map(h5, gk, grp, prop_obj, prop_dd, A, C):
    phis, psis = [], []
    dd = {}
    for where in grp:
        search = re.search('([pn]\d+)/([pn]\d+)', where)
        phi = U.signed_int(search.group(1))
        psi = U.signed_int(search.group(2))
        if phi not in phis: phis.append(phi)
        if psi not in psis: psis.append(psi)
        tb = fetch_tb(h5, where, prop_obj.name)
        if phi not in dd:
            dd[phi] = {}

        # [-1] only want the last item which correspons to the lowest potential
        # energy value after energy minimization
        dd[phi][psi] = tb.read(field=prop_obj.ifield)[-1]

    opf = open('lele', 'w')
    res = np.zeros((len(phis), len(psis)))
    print res.shape
    for i, phi in enumerate(phis):
        for j, psi in enumerate(psis):
            res[j][i] = dd[phi][psi]
            opf.write("{0:<15.2f}{1:<15.2f}{2:<15.5f}\n".format(phi, psi, dd[phi][psi]))

    # same problem with get_rama, dtype cannot be stored, need to think of way
    # to redesign the data structure!! --2013-07-17
    return np.array([np.array([phis, psis]), res])

def calc_means(h5, gk, grp, prop_obj, prop_dd, A, C):
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)
    _l = []
    for tb in grp_tb:
        _ = tb.read(field=prop_obj.ifield).mean()
        _l.append(_)

    if 'denorminators' in prop_dd:
        denorm = float(U.get_param(prop_dd['denorminators'], gk))
        logger.info('denormator: {0}'.format(denorm))
        return np.array([np.mean(_l) / denorm, U.sem(_l) / denorm])

    return np.array([np.mean(_l), U.sem(_l)])

def calc_omega_distr(h5, gk, grp, prop_obj, prop_dd, A, C):
    """This type of calcuation is still very limited, only to cis x_pro, x_y omega -2012-06-12"""
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)
    data = []
    for tb in grp_tb:
        # field 2 is cis
        data.append(tb.read(field=tb._f_getAttr('FIELD_2_NAME'))[0])
    return np.array(data)

def calc_distr(h5, gk, grp, prop_obj, prop_dd, A, C):
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)
    min_len = min(tb.read(field='time').shape[0] for tb in grp_tb)
    _l = []
    for tb in grp_tb:
        _l.append(tb.read(field=prop_obj.ifield)[:min_len])
    _la = np.array(_l)

    # grped_distr_ave is a variant of grped_distr
    special_cases = {'grped_distr_ave': 'grped_distr'}
    pt_dd = U.get_pt_dd(
        C, A.property, 
        special_cases.get(A.plot_type, A.plot_type))

    if 'bins' in pt_dd:
        i, j, s = [float(_) for _ in pt_dd['bins']]
        bins = np.arange(i, j, s)
    else:
        # assume usually 36 bins would be enough
        bins = np.linspace(_la.min(), _la.max(), 36)

    ps = []                             # probability distributions for each tb
    for _ in _la:
        fnormed = pt_dd.get('normed', False)
        p, __ = np.histogram(_, bins, normed=fnormed) 
        if not fnormed:
            p = p / float(sum(p)) # unnormed probability
        ps.append(p)
    ps = np.array(ps)

    bn = (bins[:-1] + bins[1:]) / 2.             # to gain the same length as psm, pse
    psm = ps.mean(axis=0)
    pse = [U.sem(ps[:,i]) for i in xrange(len(ps[0]))]
    pse = np.array(pse)
    return np.array([bn, psm, pse])

def calc_distr_ave(*args):
    distrs = calc_distr(*args)
    aves = calc_means(*args)
    return np.array([distrs, aves])

def calc_alx(h5, gk, grp, prop_obj, prop_dd, A, C):
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)
    # x assumed to be FIELD_0_NAME
    tb0 = grp_tb[0]
    xf = tb0._f_getAttr('FIELD_0_NAME') # xf: xfield, and it's assumed to be
                                        # the same in all tabls in the grp_tb
    min_len = min(tb.read(field=xf).shape[0] for tb in grp_tb)
    _l = []
    ref_col = grp_tb[0].read(field=xf)[:min_len]

    for tb in grp_tb:
        col1 = tb.read(field=xf)[:min_len]
        assert (col1 == ref_col).all() == True
        col2 = tb.read(field=prop_obj.ifield)[:min_len]
        _l.append(col2)
    _a = np.array(_l)
    y = _a.mean(axis=0)
    ye = np.array([U.sem(_a[:,i]) for i in xrange(len(_a[0]))])
    # ye = stats.sem(_a, axis=0)

    if 'xdenorm' in prop_dd:
        ref_col = ref_col / float(prop_dd['xdenorm'])
    if 'denorminators' in prop_dd:
        denorm = float(U.get_param(prop_dd['denorminators'], gk))
        y, ye = y / denorm, ye / denorm

    _aa = np.array([ref_col, y, ye])
    prop_dd = U.get_prop_dd(C, prop_obj.name)

    # nb_blave: number of blocks for block averaging
    n = int(prop_dd.get('nb_blave', 100))
    res = block_average(_aa, n)
    return res

def calc_imap(h5, gk, grp, prop_obj, prop_dd, A, C):
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)
    _l = []
    for tb in grp_tb:                              # it could be array
        _l.append(tb)
    # no need to normalize when plotting a map!
    res = np.array(_l).mean(axis=0)
    return res

def get_rama(h5, gk, grp, prop_obj, prop_dd, A, C):
    grp_tb = fetch_grp_tb(h5, grp, prop_obj.name)

    phis, psis, = [], []
    for tb in grp_tb:
        fn1 = tb._f_getAttr('FIELD_0_NAME')
        fn2 = tb._f_getAttr('FIELD_1_NAME')
        assert fn1 == 'phi'
        assert fn2 == 'psi'
        phi = tb.read(field=fn1)
        psi = tb.read(field=fn2)
        phis.extend(phi)
        psis.extend(psi)

    res = np.array([phis, psis])
    logger.info('shape: {0}; dtype: {1}'.format(res.shape, res.dtype))
    return res

def calc_pmf(h5, gk, grp, prop_obj, prop_dd, A, C):
    pt_dd = U.get_pt_dd(C, A.property, A.plot_type)
    if 'bins' not in pt_dd:
        raise ValueError('bins not found in {0}, but be specified when plotting pmf'.format(C.name))
    subgrps = U.split(grp, 10)                       # 10 is the group_size
    da = []
    for sp in subgrps:
        bn, psm, pse = calc_distr(h5, '', sp, prop_obj, prop_dd, A, C)
        pmf, pmf_e = prob2pmf(psm, max(psm), pse)
        for b, i in zip(bn, pmf):
            print b, i
        sub_da = np.array([bn, pmf, pmf_e])
        da.append(sub_da)
    return np.array(da)

def prob2pmf(p, max_p, e=None):
    """
    p: p_x
    max_p: p_x0
    e: variance of p_x, used to calc error propagation

    convert the probability of e2ed to potential of mean force
    """

    T = 300                                                 # Kelvin
    # R = 8.3144621                                           # J/(K*mol)
    R = 8.3144621e-3                                        # KJ/(K*mol)
    # R = 1.9858775                                           # cal/(K*mol)
    # pmf = - R * T * np.log(p / float(max_p))

    # k = 1.3806488e-23                         # Boltzman constant J*K-1
    pmf = - R * T * np.log(p / float(max_p))  # prefer to use k and Joule
                                              # instead so I could estimate the
    if e is not None:
        e = e
        # Now, calc error propagation
        # since = pmf = -R * T * ln(p_x / p_x0)
        # First, we calc the error of (p_x / p_x0)
        # error_of_p_x_divided_by_p_x0 = e**2 / p_x0**2
        pmf_e = -R * T * e / p
        return pmf, pmf_e
    else:
        return pmf

def fetch_grp_tb(h5, grp, prop_name):
    """fetch tbs bashed on where values in grp"""
    grp_tb = []
    for where in grp:
        tb = fetch_tb(h5, where, prop_name)
        if tb:
            grp_tb.append(tb)
    return grp_tb

def fetch_tb(h5, where, prop_name):
    try:
        # this is slow, so DON'T call it unless really necessary
        # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        # 961/481    0.003    0.000    4.711    0.010 file.py:1061(getNode)
        # 10085/485    0.022    0.000    4.707    0.010 file.py:1036(_getNode)
        tb = h5.getNode(where, prop_name)
        return tb
    except NoSuchNodeError:
        logger.info('Dude, NODE "{0}" DOES NOT EXIST in the table!'.format(
                os.path.join(where, prop_name)))

def block_average(ar, n=100):
    """a is a mutliple dimension array, n is the max number of data points desired"""
    logger.info('intended # of blocks: {0}'.format(n))
    logger.info('array shape {0}'.format(ar.shape))

    if ar.shape[1] < n:
        logger.info(('array length ({0}) less than the intended # of blocks ({1}), '
                     'no block averaging executed').format(ar.shape[1], n))
        return ar

    bs = ar.shape[1] / n                    # floor division; bs: block size
    if bs * n < ar.shape[1] - 1:            # -1 is math detail
        bs = bs + 1
    new_n = ar.shape[1] / bs
    if new_n * bs < ar.shape[1]:
        new_n = new_n + 1
    logger.info('DETERMINED: block size: {0}; real # of blocks: {1}'.format(bs, new_n))

    res = []
    for i in xrange(new_n):
        bcol = bs * i                           # bcol: beginning column number
        ecol = bs * (i + 1)                     # ecol: ending column number 
        res.append(ar[:, bcol:ecol].mean(axis=1))
    return np.array(res).transpose()

@U.timeit
def groupit(core_vars, prop_obj, A, C, h5):
    """
    grouping all the tables by grptoken (group token) specified in the commnand
    line
    """
    logger.info('grouping... by token: {0}'.format(A.grptoken))
    grptoken = A.grptoken
    grps = OrderedDict()                                    # grped data

    for cv in core_vars:
        grpid = cv[grptoken]
        if grpid not in grps:
            grps[grpid] = []
        where = os.path.join('/', U.get_dpp(cv))
        grps[grpid].append(where)
        # try:
        #     # this is slow:
        #     # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        #     # 961/481    0.003    0.000    4.711    0.010 file.py:1061(getNode)
        #     # 10085/485    0.022    0.000    4.707    0.010 file.py:1036(_getNode)
        #     tb = h5.getNode(where, prop_obj.name)
        #     grps[grpid].append(tb)
        # except NoSuchNodeError:
        #     logger.info('Dude, NODE "{0}" DOES NOT EXIST in the table!'.format(
        #             os.path.join(where, prop_obj.name)))
    return grps
