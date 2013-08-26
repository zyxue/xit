def pot_ener_em(**kw):
    return 'echo "Potential" | g_energy \
-f {em_edrf} \
-o {anal_dir}/{id_}_pot_ener_em.xvg'.format(**kw)
