import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import prop
import utils
import plot
import plotmp_types

def plotmp(A, C, core_vars):
    h5 = utils.get_h5(A, C)
    prop_objs = [prop.Property(i) for i in A.properties]
    data = OrderedDict()
    for prop_obj in prop_objs:
        data[prop_obj.name] = OrderedDict()
        grps = plot.groupit(core_vars, prop_obj, A, C, h5)
        if A.v: logger.info("Groups: {0}".format(grps.keys()))

        plot.calc_fetch_or_overwrite(grps, prop_obj, data[prop_obj.name], A, C, h5)

    func = plotmp_types.PLOTMP_TYPES[A.plotmp_type]
    func(data, A, C)
