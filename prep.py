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

    if A.sed_files_keys is not None:
        keys = A.sed_files_keys
        dd = config['sed_files']
        if 'all' in keys:       # ignore keys[1:]
            for item in dd.items():
                sed_files(core_vars, config, item, A.overwrite)
        else:
            for key in keys:
                sed_files(core_vars, config, (key, dd[key]), A.overwrite)

    if A.exec_files_key is not None:
        pass

    if A.qsub_files_key is not None:
        pass

    # A.prepare == 'sed':
    #     sed_files(core_vars, config, A.overwrite)
    # elif A.prepare == 'qsub':
    #     pass
    # elif A.prepare == 'exec':
    #     pass
    # elif A.prepare in ['qsub_0_jobsub_sh', 'exec_0_jobsub_sh', 'qsub_0_mdrun_sh']:
    #     exec_cmd(A.prepare, core_vars, A, C)
    # elif A.prepare == 'targzip':
    #     targzip(core_vars, A, C)
    # else:
    #     raise ValueError("Unknown prep option: {0}".format(A.prepare))

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

def sed_files(core_vars, config, item, f_overwrite):
    """
    @param item: tuple of key and corresponding template
    """
    eq_dir_name = S.EQ_DIR_NAME
    key, val = item

    tmpl = val['src']
    output_name = val['name']
    for cv in core_vars:
        dpp = U.get_dpp(cv)     # dpp: deepest path
        if val.get('b_pre_mdrun', True):
            p = os.path.join(dpp, eq_dir_name) # inside eq_dir_name
        else:
            p = dpp             # outside eq_dir_name

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

def exec_cmd(key, core_vars, A, C):
    """
    Generate the command by calling :func:`gen_cmd` and feeding it into
    :func:`utils.runit` for execution.

    :param key: the type of prep as specified after ``xit prep -p``
    :type key: str
    """
    x = gen_cmd(key, core_vars, A, C)
    U.runit(x, 4, False)       # numthreads = 4 temporarily, False mean not testing

def gen_cmd(key, core_vars, A, C):
    """
    Called by :func:`exec_cmd`, generate the corresponding command.

    :yield: the command
    """
    for cv in core_vars:
        eq_p = dpp = U.get_dpp(cv)
        if key in ['qsub_0_jobsub_sh', 'exec_0_jobsub_sh']:
            eq_p = os.path.join(dpp, S.EQ_DIR_NAME)
        must_exist(eq_p)
        cmd = construct_cmd(key, eq_p)
        yield (cmd, None)       # none means nolog

def construct_cmd(key, path):
    """
    Called by :func:`gen_cmd`, construct the command based on the ``key`` and path.

    :return: the command.
    """
    if key == 'qsub_0_jobsub_sh':
        return 'cd {0}; qsub 0_jobsub.sh; cd -'.format(path)
    elif key == 'exec_0_jobsub_sh':
        return 'cd {0}; bash 0_jobsub.sh; cd -'.format(path)
    elif key == 'qsub_0_mdrun_sh':
        return 'cd {0}; qsub 0_mdrun.sh; cd -'.format(path)

def sed_0_mdrun_sh(core_vars, A, C):
    """
    Sed ``0_mdrun.sh``, different from other sed_files in terms of the file locations
    """
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        if path_exists(dpp):
            mdrun_tmpl = C['prep']['sed_0_mdrun_sh']['mdrun_tmpl'].format(**cv)
            output_mdrun = os.path.join(dpp, '0_mdrun.sh')
            if tar_ex_ow(output_mdrun, A.overwrite):
                U.template_file(mdrun_tmpl, output_mdrun, **cv)

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

def path_exists(eq_p):
    """
    check if the path eq_p exists, if it does, return :keyword:`True`, else log info.
    """
    if os.path.exists(eq_p):
        return True
    else:
        logger.info("{0} doesn't exist, have you done -p mkdir, yet?".format(eq_p))

def must_exist(path_or_file):
    """
    The path or file must exist, otherwise raise :keyword:`IOERROR`.
    """
    if not os.path.exists(path_or_file):
        raise IOError("fatal: {0} doesn't exist!".format(path_or_file))
