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

def gmxcheck_cpt(**kw):
    # tr -d [:cntrl:] : remove control characters
    # sed -e : remove color characters, the re is not the same as that in
    # python,
    # http://www.gnu.org/software/sed/manual/html_node/Regular-Expressions.html
    # for details
    sed_re = 's/\[\([0-9]\{2\};[0-9]\{2\}\)\?m\[K//g'
    return "t=$(gmxcheck -f {cptf} 2>&1 | grep 'Last frame' | tr -d [:cntrl:] | sed -e '{sed_re}'); echo {cptf}: $t".format(sed_re=sed_re, **kw)

def trjconv_cluster_center(**kw):
    p1 = 'printf "Protein\nSystem\n" | trjconv -f {xtcf} -s {tprf} -pbc cluster -o {clusterxtcf}'.format(**kw)
    p2 = 'printf "Protein\nSystem\n" | trjconv -f {clusterxtcf} -s {tprf} -pbc mol -center -ur tric -o {centerxtcf}; rm {clusterxtcf}'.format(**kw)
    return '\n'.join([p1, p2])

def trjorder(**kw):
    dd = utils.get_anal_dd(kw['C'], 'trjorder')
    fn = '_{0}'.format(os.path.basename(kw['orderxtcf']))
    kw['tmporderf'] = os.path.join(kw['inputdir'], fn)
    na_key = dd['nak_fmt'].format(**kw)
    na = dd['na'][na_key]

    if os.path.exists(kw['centerxtcf']): # possibly prodcued by trjconv_cluster_center
        p1 = """
printf "Protein\nAll_Solvent\n"| trjorder -f {centerxtcf}  -s {tprf} -n {ndxf} -na {na} -o {tmporderf} -b {b}  ;     # rm {centerxtcf}
""".format(na=na, **kw)
    else:
        p1 = """
printf "Protein\nSystem\n"     | trjconv  -f {xtcf}        -s {tprf} -center   -pbc mol -ur tric -o {centerxtcf} -b {b} 
printf "Protein\nAll_Solvent\n"| trjorder -f {centerxtcf}  -s {tprf} -n {ndxf} -na {na} -o {tmporderf} ;      rm {centerxtcf}
""".format(na=na, **kw)

    p2 = """
printf "Ordered_Sys\n"         | trjconv  -f {tmporderf}   -s {tprf} -n {ndxf} -o {orderxtcf};                rm {tmporderf}
printf "Ordered_Sys\n"         | trjconv  -f {orderxtcf}   -s {tprf} -n {ndxf} -dump {b} -o {ordergrof}
""".format(**kw)

    return '\n'.join([p1, p2])

def g_select(**kw):
    dd = utils.get_anal_dd(kw['C'], 'g_select')
    repo_ndx_fn = dd['repo_ndx_fn_fmt'].format(**kw)
    repo_ndx = os.path.join(kw['root'], 
                            kw['C']['data']['repository'],
                            repo_ndx_fn)
    gssk = dd['gssk_fmt'].format(**kw)
    gss  = dd['gss'].get('const', '') + dd['gss'][gssk]                   # gss: g_select selction
    # if os.path.exists(kw['ordergrof']):
    #     thegrof = kw['ordergrof']
    #     thetprf = kw['ordergrof']
    # else:
    #     if kw['use_pro']:
    #         thegrof = kw['progrof']
    #         thetprf = kw['progrof']
    #     else:
    #         thegrof = kw['grof']
    #         thetprf = kw['grof']
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
