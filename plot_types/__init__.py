import inspect

from utils import timeit

modules = []
for mod_name in ['alx', 'bars', 'distr', 'pmf', 'imap', 
                 'grped_bars', 'grped_distr', 'grped_along_var']:
    # 'grped_bars', 'grped_distr', 'grped_distr_ave']:
    # http://docs.python.org/2/library/functions.html#__import__
    modules.append(__import__(mod_name, globals(), locals(), [], -1))

PLOT_TYPES = {}
for mod in modules:
    for fname in dir(mod):
        f = getattr(mod, fname)
        if inspect.isfunction(f) and hasattr(f, 'IS_PLOT_TYPE') and f.IS_PLOT_TYPE:
        # if inspect.isfunction(f):
            PLOT_TYPES.update({f.func_name: timeit(f)})

# JUST FOR REFERENCE 
# alx = A.alx
# simple_bar = B.simple_bar
# distr = D.distr
# pmf   = D.pmf
# map   = timeit(M.imap)
