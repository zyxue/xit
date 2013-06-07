#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
logger = logging.getLogger(__name__)
import pprint

import yaml
import yaml_utils
yaml.add_constructor('!include', yaml_utils.include)
# from scipy import stats

import utils
import xutils

def main():
    logger.info('INIT: parsing arguments...')
    A = xutils.get_args()
    logger.info('INIT: got loglevel: {0}'.format(A.loglevel.upper()))

    logging.basicConfig(format='%(levelname)s|%(asctime)s|%(name)s:%(message)s',
                        level=getattr(logging, A.loglevel.upper()))

    config = A.config
    if not os.path.exists(config):
        raise IOError("{0} cannot found".format(config))

    logger.info('reading configuration file: {0}'.format(config))

    C = yaml.load(open(config))                                  # config_params
    vars_ = utils.get_vars(A, C)
    logger.debug(vars_)
    dir_tmpls = utils.get_dir_tmpls(A, C)
    id_tmpl = C['systems']['id']
    core_vars = utils.gen_core_vars_r(vars_, dir_tmpls, id_tmpl)
    logger.debug(pprint.pformat(core_vars))

    # sys.exit(1)
    subcmd = sys.argv[1]                                    # subcommand
    if subcmd == 'prep':
        import prep
        prep.prepare(A, C, core_vars)
    elif subcmd == 'anal':
        import anal
        anal.analyze(A, C, core_vars)
    elif subcmd == 'transform':
        import transform
        transform.transform(A, C, core_vars)
    elif subcmd == 'plot':
        import plot
        plot.plot(A, C, core_vars)
    elif subcmd == 'plotmp':
        import plotmp
        plotmp.plotmp(A, C, core_vars)

if __name__ == '__main__':
    main()
