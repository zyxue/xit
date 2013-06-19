import inspect

from utils import timeit

modules = []
for mod_name in ['xy', 'mp_alx', 'mp_grped_along_var', 'grped_along_var_2prop']:
    # 'grped_bars', 'grped_distr', 'grped_distr_ave']:
    # http://docs.python.org/2/library/functions.html#__import__
    modules.append(__import__(mod_name, globals(), locals(), [], -1))

PLOTMP_TYPES = {}
for mod in modules:
    for fname in dir(mod):
        f = getattr(mod, fname)
        if inspect.isfunction(f) and hasattr(f, 'IS_PLOTMP_TYPE') and f.IS_PLOTMP_TYPE:
            PLOTMP_TYPES.update({f.func_name: timeit(f)})
