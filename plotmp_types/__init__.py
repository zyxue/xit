import inspect

from utils import timeit

modules = []
for mod_name in ['xy', 'mp_alx']:
    # 'grped_bars', 'grped_distr', 'grped_distr_ave']:
    # http://docs.python.org/2/library/functions.html#__import__
    modules.append(__import__(mod_name, globals(), locals(), [], -1))

PLOT2P_TYPES = {}
for mod in modules:
    for fname in dir(mod):
        f = getattr(mod, fname)
        if inspect.isfunction(f) and hasattr(f, 'IS_PLOT2P_TYPE') and f.IS_PLOT2P_TYPE:
            PLOT2P_TYPES.update({f.func_name: timeit(f)})
