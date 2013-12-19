# Seems pickle cannot be used as cache, still very slow

import os
import inspect
import pickle

from settings import CACHE_PLOT_TYPES_FILE as cache

if os.path.exists(cache):
    PLOT_TYPES = pickle.load(open(cache))
else:
    modules = []
    for mod_name in ['alx', 'bars', 'distr', 'pmf', 'imap', 'rama',
                     'grped_bars', 'grped_distr', 'grped_pmf', 'grped_along_var', 'grped_omega_distr',
                     'pot_ener_map']:
        # 'grped_bars', 'grped_distr', 'grped_distr_ave']:
        # http://docs.python.org/2/library/functions.html#__import__
        modules.append(__import__(mod_name, globals(), locals(), [], -1))

    PLOT_TYPES = {}
    for mod in modules:
        for fname in dir(mod):
            f = getattr(mod, fname)
            if inspect.isfunction(f) and hasattr(f, 'IS_PLOT_TYPE') and f.IS_PLOT_TYPE:
                PLOT_TYPES.update({f.func_name: f})

    s = pickle.dump(PLOT_TYPES, open(cache, 'w'))

# JUST FOR REFERENCE 
# alx = A.alx
# simple_bar = B.simple_bar
# distr = D.distr
# pmf   = D.pmf
# map   = timeit(M.imap)
