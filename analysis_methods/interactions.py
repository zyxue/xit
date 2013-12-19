def myg_mindist_diff_chain_LYS_LYS(**kw):
    return "printf 'LYS\nLYS\n' | myg_mindist_diff_chain \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.68 \
-on {anal_dir}/{id_}_diff_chain_LYS_LYS.xvg \
-od {anal_dir}/{id_}_mindist.xvg \
-dt 1000".format(**kw)

def g_mindist_XL_W(**kw):
    return "printf 'XL\nOrdered_Solvent' | g_mindist \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.68 \
-on {anal_dir}/{id_}_XL_W.xvg \
-od {anal_dir}/{id_}_mindist.xvg \
-dt 1000".format(**kw)

def g_mindist_HP_W(**kw):
    return "printf 'HP\nOrdered_Solvent' | g_mindist \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.68 \
-on {anal_dir}/{id_}_HP_W.xvg \
-od {anal_dir}/{id_}_mindist.xvg \
-dt 1000".format(**kw)

def g_mindist_LYS_W(**kw):
    return "printf 'LYS\nOrdered_Solvent' | g_mindist \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.68 \
-on {anal_dir}/{id_}_LYS_W.xvg \
-od {anal_dir}/{id_}_mindist.xvg \
-dt 1000".format(**kw)


def unvn(**kw):
    # TESTED, in the "uv" case, myg_mindist_excl1 and g_mindist produce the same result
    return "printf 'UN\nVN\n' | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.55 \
-on {anal_dir}/{id_}_unvn.xvg \
-od {anal_dir}/{id_}_mindist.xvg".format(**kw)

def upvp(**kw):
    return "printf 'Protein_no_end\nOrdered_Solvent\n' | g_hbond \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{id_}_upvp.xvg".format(**kw)

def upvn(**kw):
    return "printf 'UP\nVN\n' | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.45 \
-on {anal_dir}/{id_}_upvn.xvg \
-od {anal_dir}/{id_}_mindist.xvg".format(**kw)

def unvp(**kw):
    return "printf 'UN\nVP\n' | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.45 \
-on {anal_dir}/{id_}_unvp.xvg \
-od {anal_dir}/{id_}_mindist.xvg".format(**kw)

def upup(**kw):
    """dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    gromacs 4.0.7"""
    # op_fn: output filename
    opfn = '{id_}_upup.xvg' if kw['b'] > 0 else '{id_}_upup_wl.xvg'
    opfn = opfn.format(**kw)
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    return "printf 'Protein_no_end\nProtein_no_end\n' | g_hbond \
-f {thextcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{opfn}".format(thextcf=thextcf, opfn=opfn, **kw)

def unun(**kw):
    opfn = '{id_}_unun.xvg' if kw['b'] > 0 else '{id_}_unun_wl.xvg'
    opfn = opfn.format(**kw)
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    thegrof = kw['progrof'] if kw['use_pro'] else kw['ordergrof']
    return "printf 'UN\nUN\n' | myg_mindist_excl1 \
-f {thextcf} \
-s {thegrof} \
-n {ndxf} \
-b {b} \
-d 0.55 \
-on {anal_dir}/{opfn} \
-od {anal_dir}/{id_}_mindist.xvg; \
rm {anal_dir}/{id_}_mindist.xvg;".format(thextcf=thextcf, thegrof=thegrof,
                                         opfn=opfn, **kw)
def upup_map(**kw):
    """
    dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    gromacs 4.0.7

    difference from upup: including -hbn, -hbm output options
    """
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    return "printf 'Protein_no_end\nProtein_no_end\n' | g_hbond \
-f {thextcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{id_}_upup.xvg \
-hbn {anal_dir}/{id_}_upup_map.ndx \
-hbm {anal_dir}/{id_}_upup_map.xpm".format(thextcf=thextcf, **kw)

def unun_map(**kw):
    # dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    # gromacs 4.0.7
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    thegrof = kw['progrof'] if kw['use_pro'] else kw['ordergrof']
#     return "unun_map.py \
# -f {thextcf} \
# -s {thegrof} \
# -b {b} \
# -e {e} \
# -c 0.55 \
# --h5 {h5_filename} \
# -o {anal_dir}/{id_}_unun_map.log".format(thextcf=thextcf, thegrof=thegrof, **kw)

    # temporary: make -c, --nres-away --query based on .xitconfig.yaml immediately
    return "unun_map.py \
-f {thextcf} \
-s {thegrof} \
-b {b} \
-e {e} \
-c 1.2 \
--nres-away 6 \
--query 'name BB' \
--h5 {h5_filename} \
-o {anal_dir}/{id_}_unun_map.log".format(thextcf=thextcf, thegrof=thegrof, **kw)
