#!/scinet/gpc/tools/Python/Python262/bin/python

# ###############################################################################
# # Above, For checking primary, secondary, tertiary carbons, individually
# ###############################################################################
def rdf_c1vp(**kw):
    return 'printf "C1\nVP\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c1vp.xvg'.format(**kw)

def rdf_c2vp(**kw):
    return 'printf "C2\nVP\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c2vp.xvg'.format(**kw)

def rdf_c3vp(**kw):
    return 'printf "C3\nVP\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c3vp.xvg'.format(**kw)

def rdf_c1vn(**kw):
    return 'printf "C1\nVN\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c1vn.xvg'.format(**kw)

def rdf_c2vn(**kw):
    return 'printf "C2\nVN\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c2vn.xvg'.format(**kw)

def rdf_c3vn(**kw):
    return 'printf "C3\nVN\n" | g_rdf \
-f {xtcf} \
-s {tprf} \
-b {b} \
-n {ndxf} \
-bin 0.02 \
-o {anal_dir}/{id_}_rdf_c3vn.xvg'.format(**kw)
