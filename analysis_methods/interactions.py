def unvn(**kw):
    # TESTED, in the "uv" case, myg_mindist_excl1 and g_mindist produce the same result
    cmd = '''printf "UN\nVN\n" | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.55 \
-on {anal_dir}/{id_}_unvn.xvg \
-od {anal_dir}/{id_}_mindist.xvg'''.format(**kw)
    return cmd

def upvp(**kw):
    cmd = '''
printf "Protein_no_end\nOrdered_Solvent\n" | g_hbond \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{id_}_upvp.xvg'''.format(**kw)
    return cmd

def upvn(**kw):
    cmd = '''printf "UP\nVN\n" | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.45 \
-on {anal_dir}/{id_}_upvn.xvg \
-od {anal_dir}/{id_}_mindist.xvg'''.format(**kw)
    return cmd

def unvp(**kw):
    cmd = '''printf "UN\nVP\n" | myg_mindist_excl1 \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-d 0.45 \
-on {anal_dir}/{id_}_unvp.xvg \
-od {anal_dir}/{id_}_mindist.xvg'''.format(**kw)
    return cmd

def upup(**kw):
    # dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    # gromacs 4.0.7
    cmd = '''
printf "Protein_no_end\nProtein_no_end\n" | g_hbond \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{id_}_upup.xvg'''.format(**kw)
    return cmd

def unun(**kw):
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    thegrof = kw['progrof'] if kw['use_pro'] else kw['ordergrof']
    return '''
printf "UN\nUN\n" | myg_mindist_excl1 \
-f {thextcf} \
-s {thegrof} \
-n {ndxf} \
-b {b} \
-d 0.55 \
-on {anal_dir}/{id_}_unun.xvg \
-od {anal_dir}/{id_}_mindist.xvg'''.format(thextcf=thextcf, thegrof=thegrof, **kw)

def upup_map(**kw):
    """
    dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    gromacs 4.0.7

    difference from upup: including -hbn, -hbm output options
    """
    cmd = '''
printf "Protein_no_end\nProtein_no_end\n" | g_hbond \
-f {orderxtcf} \
-s {tprf} \
-n {ndxf} \
-b {b} \
-r 0.35 \
-nonitacc \
-num {anal_dir}/{id_}_upup.xvg \
-hbn {anal_dir}/{id_}_upup_map.ndx \
-hbm {anal_dir}/{id_}_upup_map.xpm'''.format(**kw)
    return cmd

def unun_wl(**kw):
    return '''
printf "UN\nUN\n" | myg_mindist_excl1 \
-f {orderxtcf} \
-s {grof} \
-n {ndxf} \
-b 0 \
-d 0.55 \
-on {anal_dir}/{id_}_unun_wl.xvg \
-od {anal_dir}/{id_}_mindist.xvg'''.format(**kw)

def unun_map(**kw):
    # dDA < 3.5nm & angle ADH<30 degree, which is the default criteria in
    # gromacs 4.0.7
    return '''
unun_map.py \
-f {orderxtcf} \
-s {ordergrof} \
-b {b} \
-c 0.55 \
--h5 {h5_filename} '''.format(**kw)
