import os
import re
import subprocess
import logging
logger = logging.getLogger(__name__)

from pprint import pprint as pp

EQ_DIR_NAME = 'beforenpt'

import utils as U

def prepare(A, C, core_vars):
    if A.prepare == 'mkdir':
        mkdir(core_vars)
    elif A.prepare == 'link_gro':
        link_gro(core_vars, A, C)
    elif A.prepare == 'sed_top':
        sed_top(core_vars, A, C)
    elif A.prepare == 'sed_0_jobsub_sh':
        sed_0_jobsub_sh(core_vars, A, C)
    elif A.prepare == 'qsub_0_jobsub_sh':
        qsub_0_jobsub_sh(core_vars, A, C)
    elif A.prepare == 'sed_0_mdrun_sh':
        sed_0_mdrun_sh(core_vars, A, C)
    elif A.prepare == 'qsub_0_mdrun_sh':
        qsub_0_mdrun_sh(core_vars, A, C)
    elif A.prepare == 'targzip':
        targzip(core_vars, A, C)
    else:
        raise ValueError("Unknown prep option: {0}".format(A.prepare))

def mkdir(core_vars):
    """This is similar to init_hdf5 in transform.py"""
    paths = U.gen_paths_dict(core_vars)

    depths = sorted(paths.keys())
    max_depth = max(depths)
    for dp in depths:
        ps = paths[dp]
        for p in ps:
            mk_new_dir(p)
            if dp == max_depth:
                eq_p = os.path.join(p, EQ_DIR_NAME) # eq_p: equilibration path
                mk_new_dir(eq_p)
                
def mk_new_dir(p):
    if not os.path.exists(p):
        os.mkdir(p)
        logger.info('mkdir {0}'.format(p))
    else:
        logger.info('{0} ALREADY EXISTED'.format(p))

def path_exists(eq_p):
    if os.path.exists(eq_p):
        return True
    else:
        logger.info("{0} doesn't exist, have you done -p mkdir, yet?".format(eq_p))
        
def tar_ex_ow(target_file, f_overwrite):
    """tar_ex_ow: target_exists_or_overwrite"""
    if not os.path.exists(target_file):
        return True
    elif f_overwrite:
        if os.path.islink(target_file): # since it cannot be overwritten, has to delete it first
            os.remove(target_file)
        return True
    else:
        logger.info('{0} ALREADY EXISTS. user --overwrite to overwrite previous one'.format(target_file))        

def link_gro(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        eq_p = os.path.join(dpp, EQ_DIR_NAME)        
        if path_exists(eq_p):
            src_gro = C['prep']['link_gro']['src_gro'].format(**cv)
            if not os.path.exists(src_gro):
                raise IOError("fatal: {0} doesn't exist!".format(src_gro))
            if 'target_gro' in C['prep']['link_gro']:
                target_gro = os.path.join(
                    eq_p, os.path.basename(C['prep']['link_gro']['target_gro'].format(**cv)))
            else:
                target_gro = os.path.join(eq_p, os.path.basename(src_gro))

            if tar_ex_ow(target_gro, A.overwrite):
                rel_src_gro = os.path.relpath(src_gro, os.path.dirname(target_gro))
                os.symlink(rel_src_gro, target_gro)
                logger.info('symlink: {0} -> {1}'.format(rel_src_gro, target_gro))

def sed_top(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)     # dpp: deepest path
        eq_p = os.path.join(dpp, EQ_DIR_NAME)
        if path_exists(eq_p):
            top_tmpl = C['prep']['sed_top']['top_tmpl'].format(**cv)
            output_top = os.path.join(eq_p, '{0}.top'.format(cv['id_']))
            if tar_ex_ow(output_top, A.overwrite):
                U.template_file(top_tmpl, output_top, **cv)

def sed_0_jobsub_sh(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        eq_p = os.path.join(dpp, EQ_DIR_NAME)
        if path_exists(eq_p):
            jobsub_tmpl = C['prep']['sed_0_jobsub_sh']['jobsub_tmpl'].format(**cv)
            output_jobsub = os.path.join(eq_p, '0_jobsub.sh')
            if tar_ex_ow(output_jobsub, A.overwrite):
                U.template_file(jobsub_tmpl, output_jobsub, **cv)


def qsub_0_jobsub_sh(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        p = os.path.join(dpp, EQ_DIR_NAME)
        if path_exists(dpp):
            subprocess.call('cd {0}; qsub 0_jobsub.sh; cd -'.format(p), shell=True)

def sed_0_mdrun_sh(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        if path_exists(dpp):
            mdrun_tmpl = C['prep']['sed_0_mdrun_sh']['mdrun_tmpl'].format(**cv)
            output_mdrun = os.path.join(dpp, '0_mdrun.sh')
            if tar_ex_ow(output_mdrun, A.overwrite):
                U.template_file(mdrun_tmpl, output_mdrun, **cv)

def qsub_0_mdrun_sh(core_vars, A, C):
    for cv in core_vars:
        dpp = U.get_dpp(cv)
        if path_exists(dpp):
            subprocess.call('cd {0}; qsub 0_mdrun.sh; cd -'.format(dpp), shell=True)

def targzip(core_vars, A, C):
    subprocess.call('tar cfv - {0} | gzip -cv > tprs.tar.gz', shell=True)
