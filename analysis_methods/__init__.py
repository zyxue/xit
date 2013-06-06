import inspect

from analysis_methods import org
from analysis_methods import fancy
from analysis_methods import basic
from analysis_methods import interactions
from analysis_methods import rdf

# uses a different way to collect methods than __init__ in plot_types, just to
# see why is better in long-term. The later one must be better for frequently
# added modules

# collecting all the functions available
PROPERTIES = {}
for module in [basic, fancy, interactions, rdf]:
    for fname in dir(module):
        f = getattr(module, fname)
        if inspect.isfunction(f):
            PROPERTIES.update({f.func_name:f})

ANALYSIS_METHODS = PROPERTIES.copy()
for fname in dir(org):
    f = getattr(org, fname)
    if inspect.isfunction(f):
        ANALYSIS_METHODS.update({f.func_name:f})
    

# JUST FOR REFERENCE 
# rg_c_alpha  = B.rg_c_alpha
# rg_wl       = B.rg_wl
# e2ed        = B.e2ed

# upup            = I.upup
# unun            = I.unun
# unun_wl         = I.unun_wl
# upup_map        = I.upup_map
# unun_map        = I.unun_map

# check_inputdir = O.check_inputdir
# g_select        = O.g_select
# symlink_ndx     = O.symlink_ndx
# extend_tpr      = O.extend_tpr
# trjconv_progrof = O.trjconv_progrof
# trjorder    = O.trjorder
