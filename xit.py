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

import xutils as xU

def get_vars_from_cmd(variables):
    return {'var{0}'.format(k+1):v for k, v in enumerate(variables)}

def get_vars_from_config(config):
    return {k:config[k] for k in config.keys() if re.match('var[0-9]+', k)}

def get_vars(cmd_vars, config_vars):
    """
    generate an OrderedDict instance of variables from cmd arguments or the
    configuration file.

    e.g.

    ``
    {var1: ['epz1'],
     var2: ['h'],
     var3: [8],
     var4: ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
     }
     ``
    """

    if cmd_vars:                  # cmd has higher priority over configuration
        vars_ = get_vars_from_cmd(cmd_vars)
    else:
        vars_ = get_vars_from_config(config_vars)

    ret = OrderedDict(sorted(vars_.items(), key=lambda i: i[0]))
    return ret

def get_dir_templates(config_dirs):
    dir_tmpls = {k:config_dirs[k] 
                 for k in config_dirs.keys() if re.match('dir[0-9]+', k)}

    # sorted dir_tmpls by keys, the digit in the end in particular
    dir_tmpls = OrderedDict(sorted(dir_tmpls.items(), key=lambda t:t[0]))
    return dir_tmpls

def gen_core_vars_r(vars_, dir_tmpls, id_tmpl='', result=[], **kw):
    """
    generate a dict core variables for each individual replica, keys include
    var[0-9]*, path[0-9]*, id_. As a whole, a list is returned

    _r means recursion
    """
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

def format_dict(ordered_dict):
    ret = ['']
    for k, v in ordered_dict.items():
        ret.append('          {0}: {1}'.format(k, v))
    return '\n'.join(ret)

def init(cmd_args):
    A = xU.get_cmd_args(cmd_args)

    logging.basicConfig(
        format='%(levelname)s|%(asctime)s|%(name)s:%(message)s',
        level=getattr(logging, A.loglevel.upper()))
    logger.info('Obtained loglevel: {0}'.format(A.loglevel.upper()))

    config_file = A.config
    if not os.path.exists(config_file):
        raise IOError("{0} cannot found".format(config_file))

    logger.info('Parsing configuration file: {0}'.format(config_file))
    C = yaml.load(open(config_file))


    vars_ = get_vars(A.vars, C['systems'])
    logger.info('Extracted variables: {0}'.format(format_dict(vars_)))
    

    dir_templates = get_dir_templates(C['systems'])
    logger.info('Extracted dir templates: {0}'.format(format_dict(dir_templates)))


    id_template = C['systems']['id']
    logger.info('Extracted id template: {0}'.format(id_template))

    core_vars = gen_core_vars_r(vars_, dir_templates, id_template)
    logger.debug(pprint.pformat((core_vars)))
    return A, C, core_vars
    
def main(cmd_args):
    A, C, core_vars = init(cmd_args)

    subcmd = cmd_args[0]        # subcommand
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
