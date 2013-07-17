import os
import subprocess
import logging
logger = logging.getLogger(__name__)

import setting as S

import utils as U

def prepare(A, C, core_vars):
    if A.prepare == 'mkdir':
        mkdir(core_vars, A, C)
    elif A.prepare == 'link_gro':
        link_gro(core_vars, A, C)
    elif A.prepare in ['sed_top', 'sed_itp', 'sed_0_jobsub_sh']:
        sed_file(A.prepare, core_vars, A, C)
    elif A.prepare in ['qsub_0_jobsub_sh', 'exec_0_jobsub_sh', 'qsub_0_mdrun_sh']:
        exec_cmd(A.prepare, core_vars, A, C)
    elif A.prepare == 'sed_0_mdrun_sh':
        sed_0_mdrun_sh(core_vars, A, C)
    elif A.prepare == 'targzip':
        targzip(core_vars, A, C)
    else:
        raise ValueError("Unknown prep option: {0}".format(A.prepare))

def mkdir(core_vars, A, C):
    """This is similar to init_hdf5 in transform.py"""
    paths = U.gen_paths_dict(core_vars)

    depths = sorted(paths.keys())
    max_depth = max(depths)
    for dp in depths:
        ps = paths[dp]
        for p in ps:
            mk_new_dir(p)
            if dp == max_depth:
                eq_p = os.path.join(p, S. EQ_DIR_NAME) # eq_p: equilibration path
                mk_new_dir(eq_p)

def mk_new_dir(p):
    if not os.path.exists(p):
        os.mkdir(p)
        logger.info('mkdir {0}'.format(p))
    else:
        logger.info('{0} ALREADY EXISTED'.format(p))

def link_gro(core_vars, A, C):
    for cv in core_vars:
        src_gro = C['prep']['link_gro']['src_gro'].format(**cv)
        must_exist(src_gro)

        dpp = U.get_dpp(cv)
        eq_p = os.path.join(dpp, S. EQ_DIR_NAME)        

        must_exist(eq_p)

        if 'target_gro' in C['prep']['link_gro']:
            target_gro = os.path.join(
                eq_p, os.path.basename(C['prep']['link_gro']['target_gro'].format(**cv)))
        else:
            target_gro = os.path.join(eq_p, os.path.basename(src_gro))

        if tar_ex_ow(target_gro, A.overwrite):
            print target_gro
            rel_src_gro = os.path.relpath(src_gro, os.path.dirname(target_gro))
            os.symlink(rel_src_gro, target_gro)
            logger.info('symlink: {0} -> {1}'.format(rel_src_gro, target_gro))

def sed_file(key, core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)     # dpp: deepest path
        eq_p = os.path.join(dpp, S. EQ_DIR_NAME)
        must_exist(eq_p)

        template, output = gen_template_output(key, cv, eq_p, C)
        if tar_ex_ow(output, A.overwrite):
            U.template_file(template, output, **cv)

def gen_template_output(key, cv, path, C):
    if key == 'sed_top':
        dd = C['prep']['sed_top']
        template = dd['top_tmpl'].format(**cv)
        output = os.path.join(path, dd.get('output',  '{id_}.top').format(**cv))
    elif key == 'sed_itp':
        dd = C['prep']['sed_itp']
        template = dd['itp_tmpl'].format(**cv)
        output = os.path.join(path, dd.get('output',  '{id_}.itp').format(**cv))
    elif key == 'sed_0_jobsub_sh':
        dd = C['prep']['sed_0_jobsub_sh']
        template = dd['jobsub_tmpl'].format(**cv)
        output = os.path.join(path, '0_jobsub.sh')
    return template, output

def exec_cmd(key, core_vars, A, C):
    x = gen_cmd(key, core_vars, A, C)
    U.runit(x, 4, False)       # numthreads = 4 temporarily, False mean not testing

def gen_cmd(key, core_vars, A, C):
    for cv in core_vars:
        eq_p = dpp = U.get_dpp(cv)
        if (key == 'qsub_0_mdrun_sh'):
            eq_p = os.path.join(dpp, S. EQ_DIR_NAME)
        must_exist(eq_p)
        cmd = construct_cmd(key, eq_p)
        yield (cmd, None)       # none means nolog

def construct_cmd(key, p):
    if key == 'qsub_0_jobsub_sh':
        return 'cd {0}; qsub 0_jobsub.sh; cd -'.format(p)
    elif key == 'exec_0_jobsub_sh':
        return 'cd {0}; bash 0_jobsub.sh; cd -'.format(p)
    elif key == 'qsub_0_mdrun_sh':
        return 'cd {0}; qsub 0_mdrun.sh; cd -'.format(p)

def sed_0_mdrun_sh(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        if path_exists(dpp):
            mdrun_tmpl = C['prep']['sed_0_mdrun_sh']['mdrun_tmpl'].format(**cv)
            output_mdrun = os.path.join(dpp, '0_mdrun.sh')
            if tar_ex_ow(output_mdrun, A.overwrite):
                U.template_file(mdrun_tmpl, output_mdrun, **cv)

def targzip(core_vars, A, C):
    subprocess.call('tar cfv - {0} | gzip -cv > tprs.tar.gz', shell=True)

def tar_ex_ow(target_file, f_overwrite):
    """tar_ex_ow: target_exists_or_overwrite"""
    if (not os.path.exists(target_file)) and not os.path.islink(target_file):
        # os.path.exists return False for symbolic link
        return True
    elif f_overwrite:
        if os.path.islink(target_file): # since it cannot be overwritten, has to delete it first
            os.remove(target_file)
        return True
    else:
        logger.info('{0} ALREADY EXISTS. user --overwrite to overwrite previous one'.format(target_file))        

def path_exists(eq_p):
    if os.path.exists(eq_p):
        return True
    else:
        logger.info("{0} doesn't exist, have you done -p mkdir, yet?".format(eq_p))

def must_exist(path_or_file):
    if not os.path.exists(path_or_file):
        raise IOError("fatal: {0} doesn't exist!".format(path_or_file))
