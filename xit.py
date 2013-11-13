#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import logging
logger = logging.getLogger(__name__)
import pprint
from collections import OrderedDict

import yaml
import yaml_utils
yaml.add_constructor('!include', yaml_utils.include)
# from scipy import stats

import xutils as xU

def get_vars_from_cmd(variables):
    return {'var{0}'.format(k+1):v for k, v in enumerate(variables)}

def get_vars_from_config(config):
    return {k:config[k] for k in config.keys() if re.match('var[0-9]+', k)}

def get_vars(A, C):
    """
    generate an OrderedDict instance of variables from cmd arguments or the
    configuration file
    """
    if A.vars:                  # cmd has higher priority over configuration
        vars_ = get_vars_from_cmd(A.vars)
    else:
        vars_ = get_vars_from_config(C['system'])

    vars_ = OrderedDict(sorted(vars_.items(), key=lambda i: i[0]))
    return vars_

def gen_core_vars_r(vars_, dir_tmpls, id_tmpl='', result=[], **kw):
    """_r means recursion"""
    if not vars_:
        # cv: core vars
        cv = {}
        dirnames = {_:dir_tmpls[_].format(**kw) for _ in dir_tmpls}
        dirnames = OrderedDict(sorted(dirnames.items(), key=lambda i: i[0]))
        cv.update(dirnames)
        cv.update(id_=id_tmpl.format(**kw))
        cv.update(kw)
        pathnames = dirnames.values()
        for i in xrange(len(pathnames)):
            cv.update({'path{0}'.format(i+1):os.path.join(*pathnames[0:i+1])})
        result.append(cv)
    else:
        k, val = vars_.popitem()
        for v in val:
            kw_copy = {i:kw[i] for i in kw}
            kw_copy.update({k:v})
            vars_copy = {i:vars_[i] for i in vars_}
            gen_core_vars_r(vars_copy, dir_tmpls, id_tmpl, **kw_copy)
    return result

def get_dir_tmpls(A, C):
    CS = C['systems']
    dir_tmpls = {k:CS[k] for k in CS.keys() if re.match('dir[0-9]+', k)}
    # sorted dir_tmpls by keys, the number in particular
    dir_tmpls = OrderedDict(sorted(dir_tmpls.items(), key=lambda t:t[0]))
    return dir_tmpls

def main(cmd_args):
    logger.info('INIT: parsing arguments...')
    A = xU.get_args(cmd_args)
    logger.info('INIT: got loglevel: {0}'.format(A.loglevel.upper()))

    logging.basicConfig(format='%(levelname)s|%(asctime)s|%(name)s:%(message)s',
                        level=getattr(logging, A.loglevel.upper()))

    config = A.config
    if not os.path.exists(config):
        raise IOError("{0} cannot found".format(config))

    logger.info('reading configuration file: {0}'.format(config))

    C = yaml.load(open(config))                                  # config_params
    vars_ = get_vars(A, C)
    logger.info(vars_)
    dir_tmpls = get_dir_tmpls(A, C)
    id_tmpl = C['systems']['id']
    core_vars = gen_core_vars_r(vars_, dir_tmpls, id_tmpl)
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
    main(sys.argv[1:])
