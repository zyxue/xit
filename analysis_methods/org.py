import os
import re
import glob
import subprocess
import StringIO

import utils

def check_inputdir(**kw):
    d = kw['inputdir']
    if not os.path.exists(d):
        raise ValueError('Check if {0} exists?!'.format(d))
    s = 'echo "{0!s} exists"'.format(d)
    return s

def trjorder(**kw):
    dd = utils.get_anal_dd(kw['C'], 'trjorder')
    fn = '_{0}'.format(os.path.basename(kw['orderxtcf']))
    kw['tmporderf'] = os.path.join(kw['inputdir'], fn)
    na_key = dd['nak_fmt'].format(**kw)
    na = dd['na'][na_key]
    return """
printf "Protein\nSystem\n"     | trjconv  -f {xtcf}        -s {tprf} -center   -pbc mol -ur tric -o {centerxtcf}
printf "Protein\nAll_Solvent\n"| trjorder -f {centerxtcf}  -s {tprf} -n {ndxf} -na {na} -o {tmporderf} ;        rm {centerxtcf}
printf "Ordered_Sys\n"         | trjconv  -f {tmporderf}   -s {tprf} -n {ndxf} -o {orderxtcf};                  rm {tmporderf}
printf "Ordered_Sys\n"         | trjconv  -f {orderxtcf}   -s {tprf} -n {ndxf} -dump {b} -o {ordergrof}
""".format(na=na, **kw)

def g_select(**kw):
    dd = utils.get_anal_dd(kw['C'], 'g_select')
    repo_ndx_fn = dd['repo_ndx_fn_fmt'].format(**kw)
    repo_ndx = os.path.join(kw['root'], 
                            kw['C']['data']['repository'],
                            repo_ndx_fn)
    gssk = dd['gssk_fmt'].format(**kw)
    gss  = dd['gss'].get('const') + dd['gss'][gssk]                   # gss: g_select selction
    if os.path.exists(kw['ordergrof']):
        thegrof = kw['ordergrof']
        thetprf = kw['ordergrof']
    else:
        if kw['use_pro']:
            thegrof = kw['progrof']
            thetprf = kw['progrof']
        else:
            thegrof = kw['grof']
            thetprf = kw['grof']
        
    return """g_select \
-f {thegrof} \
-s {thetprf} \
-on {repo_ndx} \
-select '{gss}'""".format(thegrof=thegrof, thetprf=thetprf, repo_ndx=repo_ndx, gss=gss, **kw)

def symlink_ndx(**kw):
    dd = utils.get_anal_dd(kw['C'], 'g_select')
    ndx_fn = dd['repo_ndx_fn_fmt'].format(**kw)
    repo_ndx = os.path.join(kw['root'], 
                            kw['C']['data']['repository'], 
                            ndx_fn)
    return "ln -s -f -v {repo_ndx} {ndxf}".format(repo_ndx=repo_ndx, **kw)

def extend_tpr(**kw):
    dd = utils.get_anal_dd(kw['C'], 'extend_tpr')
    T = kw['tprf']
    tm = get_tpr_time(T)
    nr = os.path.basename(T).rsplit('.tpr')[0]              # nr: name root
    renamed = '{0}_{1}ns.tpr'.format(nr, tm)
    oldtprf= os.path.join(os.path.dirname(T), renamed)
    return 'mv -v {tprf} {oldtprf}; tpbconv -s {oldtprf} -extend {extend} -o {tprf}'.format(
        oldtprf=oldtprf, extend=dd['extend'], **kw)

def trjcat_plus(**kw):
    # tmpl = 'sq[1-9]h[0-3][0-9]_md.part[0-9][0-9][0-9][0-9].xtc'
    RE = '{0}_md\.part[0-9][0-9][0-9][0-9].xtc$'.format(kw['id_'])
    xtcfs = sorted(
        glob.glob(
            os.path.join(kw['inputdir'], "*.xtc")
            )
        )
    xtcfs = [xtcf for xtcf in xtcfs if re.search(RE, xtcf)]
    kw.update(dict(fmt_xtcfs=' '.join(xtcfs)))
    cmd1 = 'trjcat+.py -f {fmt_xtcfs} -s {tprf} -o {xtcf}'.format(**kw)
    cmd2 = "printf 'Protein\nsystem\n' | trjconv \
-f {xtcf} \
-s {tprf} \
-pbc mol \
-center \
-b 0 \
-ur tric \
-dump 0 \
-o {grof}".format(**kw)
    return cmd1 + ';' + cmd2

def trjconv_pro(**kw):
    cmd1 = "printf 'Protein\nProtein\n' | trjconv \
-f {xtcf} \
-s {tprf} \
-pbc mol \
-center \
-b {b} \
-o {proxtcf}".format(**kw)
    cmd2 = "printf 'Protein\nProtein\n' | trjconv \
-f {xtcf} \
-s {tprf} \
-pbc mol \
-center \
-dump 0 \
-o {progrof}".format(**kw)

    return cmd1 + ';' + cmd2

def get_tpr_time(tprfile):
    proc = subprocess.Popen(['gmxdump', '-s', tprfile],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if proc.returncode == 0:
        # Different from get_cpt_time, we use stdout this time
        nsteps_found_flag = False
        dt_found_flag = False
        for line in StringIO.StringIO(stdout):
            if 'nsteps' in line:
                nsteps = float(line.split('=')[1].strip())  # number of steps
                nsteps_found_flag = True
            elif "delta_t" in line:
                dt = float(line.split('=')[1].strip())      # unit: ps
                dt_found_flag = True

            if nsteps_found_flag and dt_found_flag:
                break
        result = "{0:.0f}".format(nsteps * dt / 1000)       # unit: ns
        return result
    else:
        if not os.path.exists(tprfile):
            return "{0} not exist".format(tprfile)
        else:
            return "{0} is corrupted".format(tprfile)

def symlink_md2pro(**kw):
    """useful for simulations in vacuo"""
    proxtcf = kw['proxtcf']
    dirname = os.path.dirname(proxtcf)
    relxtcf = os.path.relpath(kw['xtcf'], dirname)
    progrof = kw['progrof']
    relprof = os.path.relpath(kw['grof'], dirname)
    return "ln -sfv {relxtcf} {proxtcf}; ln -sfv {relprof} {progrof}".format(
        relxtcf=relxtcf, proxtcf=proxtcf, relprof=relprof, progrof=progrof)
