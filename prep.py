"""
Preparation
===========

**Important Nomenclature:**

* A: arguments
* C: config
* core_vars: core variables

Functions
---------

"""

import os
import subprocess
import logging
logger = logging.getLogger(__name__)

import settings as S
import utils as U

def prepare(A, C, core_vars):
    """
    Based on the input, it determines which step of system preparation to
    invoke.
    """
    config = C['prep']
    if A.mkdir:
        mkdir(core_vars)

    elif A.sed_files_keys is not None:
        # A.sed_files_keys should be a list, different from the cases of exec
        # and qsub
        keys = A.sed_files_keys
        dd = config['files']
        if 'all' in keys:       # ignore keys[1:]
            for item in dd.items():
                sed_files(core_vars, item, A.overwrite)
        else:
            for key in keys:
                sed_files(core_vars, (key, dd[key]), A.overwrite)

    elif A.exec_files_key is not None:
        key = A.exec_files_key
        item = (key, config['files'][key])
        exec_cmds(core_vars, item)

    elif A.qsub_files_key is not None:
        key = A.qsub_files_key
        item = (key, config['files'][key])
        exec_cmds(core_vars, item, f_qsub=True)

    # elif A.prepare == 'targzip':
    #     targzip(core_vars, A, C)
    else:
        logging.info('Nothing to be done')

def mkdir(core_vars):
    """
    Make directories based on ``.xitconfig``. The looping is similar to
    :func:`transform.init_hdf5`.
    """
    paths = U.gen_paths_dict(core_vars)
    eq_dir_name = S.EQ_DIR_NAME

    depths = sorted(paths.keys())
    max_depth = max(depths)
    for dp in depths:
        for p in paths[dp]:
            mk_new_dir(p)
            if dp == max_depth:
                eq_p = os.path.join(p, eq_dir_name) #  eq_p: equilibration path
                mk_new_dir(eq_p)

def mk_new_dir(p):
    if not os.path.exists(p):
        os.mkdir(p)
        logger.info('mkdir {0}'.format(p))
    else:
        logger.info('{0} ALREADY EXISTED'.format(p))

def sed_files(core_vars, item, f_overwrite):
    """
    @param item: tuple of key and corresponding info
    """
    eq_dir_name = S.EQ_DIR_NAME
    key, val = item

    tmpl = val['src']
    output_name = val['name']
    for cv in core_vars:
        p = get_path(cv, eq_dir_name, val.get('b_pre_mdrun', True))
        template = tmpl.format(**cv)
        output = os.path.join(p, output_name.format(**cv))
        sed_file(template, output, cv, f_overwrite)

def sed_file(input_, output, cv, f_overwrite):
    if os.path.exists(output):
        if f_overwrite:
            U.template_file(input_, output, **cv)
        else:
            logger.info('{0} ALREADY EXISTS. use '
                        '--overwrite to overwrite previous one'.format(output))
    else:
        U.template_file(input_, output, **cv)

def exec_cmds(core_vars, item, f_qsub=False):
    """
    Generate the command by calling :func:`gen_cmd` and feeding it into
    :func:`utils.runit` for execution.

    @param f_qsub: if ``f_qsub`` is True, then invoke the qsub the script to
    the queueing system instead of executing it.
    """
    x = gen_cmds(core_vars, item, f_qsub)
    U.runit(x, 4, False)       # numthreads = 4 temporarily, False mean not testing

def gen_cmds(core_vars, item, f_qsub):
    """
    Called by :func:`exec_cmd`, generate the corresponding command.

    @param item: tuple of key and corresponding template

    :yield: the command
    """
    eq_dir_name = S.EQ_DIR_NAME
    key, val = item

    output_name = val['name']
    for cv in core_vars:
        p = get_path(cv, eq_dir_name, val.get('b_pre_mdrun', True))
        output = output_name.format(**cv)
        if f_qsub:
            cmd = 'cd {0}; qsub {1}; cd -'.format(p, output)
        else:
            cmd = 'cd {0}; bash {1}; cd -'.format(p, output)
        yield (cmd, None)       # none means nolog

def get_path(cv, eq_dir_name, b_pre_mdrun=False):
    dpp = U.get_dpp(cv)        
    if b_pre_mdrun:
        p = os.path.join(dpp, eq_dir_name) # inside eq_dir_name
    else:
        p = dpp                 # outside eq_dir_name
    return p


def targzip(core_vars, A, C):
    """
    Tar the file and gzip it by called tar and gzip commands from the shell
    """
    subprocess.call('tar cfv - {0} | gzip -cv > tprs.tar.gz', shell=True)

def tar_ex_ow(target_file, f_overwrite):
    """
    tar_ex_ow: target_exists_or_overwrite
    """
    if (not os.path.exists(target_file)) and not os.path.islink(target_file):
        # os.path.exists return False for symbolic link
        return True
    elif f_overwrite:
        if os.path.islink(target_file): # since it cannot be overwritten, has to delete it first
            os.remove(target_file)
        return True
    else:
        logger.info('{0} ALREADY EXISTS. use --overwrite to overwrite previous one'.format(target_file))        
