import os
import re
import logging
logger = logging.getLogger(__name__)
from pprint import pprint as pp

import utils as U

def prepare(A, C, core_vars):
    if A.prepare == 'mkdir':
        mkdir(core_vars)


def mkdir(core_vars):
    """This is similar to init_hdf5 in transform.py"""
    paths = U.gen_paths_dict(core_vars)

    depths = sorted(paths.keys())
    for dp in depths:
        ps = paths[dp]
        for p in ps:
            if not os.path.exists(p):
                os.mkdir(p)
                logger.info('mkdir {0}'.format(p))
            else:
                logger.info('{0} ALREADY EXISTED'.format(p))
