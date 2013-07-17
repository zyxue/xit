def rg_c_alpha(**kw):
    """
    Radius of Gyration: backbone heavy atoms only. e.g. for (GVPGV)7, there would be 107 atoms,
    which is 35 * 3 + 2 (modified ends)
    """
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    theb = kw['b']
    if theb > 0:
        theo = '{anal_dir}/{id_}_rg_c_alpha.xvg'.format(**kw)
    else:
        theo = '{anal_dir}/{id_}_rg_c_alpha_wl.xvg'.format(**kw)
    return 'printf "C-alpha" | g_gyrate \
-f {thextcf} \
-s {tprf} \
-b {theb} \
-o {theo}'.format(thextcf=thextcf, theb=theb, theo=theo, **kw)

def dssp(**kw):
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    thegrof = kw['progrof'] if kw['use_pro'] else kw['ordergrof']
    theb = kw['b']
    if theb > 0:
        thesc = '{anal_dir}/{id_}_dssp.xvg'.format(**kw)
    else:
        thesc = '{anal_dir}/{id_}_dssp_wl.xvg'.format(**kw)
    return 'printf "Protein" | mydo_dssp \
-f {thextcf} \
-s {thegrof} \
-b {theb} \
-sc {thesc}'.format(thextcf=thextcf, thegrof=thegrof, theb=theb, thesc=thesc, **kw)

def e2ed(**kw):
    """end to end distance"""
    # 2012-09-18
    # myg_dist & g_dist, the results are different for sq4m00 in mono_su_as.

    # By comparing the results in vmd, g_dist and myg_dist, as well as that
    # from g_dist on proxtcf and orderxtcf, the results returned by g_dist is
    # found to be unreliable.

    # Since my analysis is all based on orderxtcf, using g_dist would be good,
    # there is not problem concerning PBC any more.
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    # seems g_dist only takes tprf
    return 'printf "N_ter\nC_ter\n" | g_dist \
-f {thextcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-o {anal_dir}/{id_}_e2ed.xvg'.format(thextcf=thextcf, **kw)

# def e2ed_wl(**kw):
#     return 'printf 'N_ter\nC_ter\n' | g_dist \
# -f {orderxtcf} \
# -s {tprf} \
# -b 0 \
# -n {ndxf} \
# -o {anal_dir}/{id_}_e2ed.xvg'.format(**kw)
