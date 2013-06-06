import os
import utils

def seqspacing(**kw):
    dd = utils.get_anal_dd(kw['C'], 'seqspacing')
    plk = dd['plk_fmt'].format(**kw)
    pl  = dd['pl'][plk]
    thextcf = kw['proxtcf'] if kw['use_pro'] else kw['orderxtcf']
    thegrof = kw['progrof'] if kw['use_pro'] else kw['ordergrof']
    return "seqspacing.py \
-f {thextcf} \
-s {thegrof} \
-b {b} \
--pl {peptide_length} \
-o {anal_dir}/{id_}_seqspacing.xvg".format(thextcf=thextcf, thegrof=thegrof, 
                                           peptide_length=pl, **kw)

def conf_entropy(**kw):
    dd = utils.get_prop_dd(kw['C'], 'conf_entropy')
    # tmp_dir is for storing the covar_e[0-9].* directories and files in it
    # temporarily
    kw.update(tmp_dir=os.path.join(kw['anal_dir'],
                                   '{0}_{1}'.format(kw['id_'], dd['dt'])))
    kw.update(dt=dd['dt'])
    # since it will be meaningless if the beginning time equals the ending time
    kw.update(b0 = str(int(kw['b']) + int(dd['dt'])))

    # The shit returned at this stage is really shitty!!

    return """

outputxvg={anal_dir}/{id_}_conf_entropy.xvg
# remove outputxvg created by previous testing run maybe
if [ -f ${{outputxvg}} ]; then rm ${{outputxvg}}; fi

for etime in {{{b0}..{e}..{dt}}}; do 
    tmp_dir={tmp_dir}
    if [ -d ${{tmp_dir}}; then rm -rf ${{tmp_dir}}; fi
    mkdir ${{tmp_dir}}

    covar_dir={tmp_dir}/covar_e${{etime}}
    if [ -d ${{covar_dir}} ]; then rm -rfv ${{covar_dir}}; fi
    mkdir ${{covar_dir}}

    printf "Protein\\nProtein\\n" | g_covar -f {orderxtcf} -s {tprf} -b {b} -e ${{etime}} -mwa -o ${{covar_dir}}/eigenval_e${{etime}}.xvg -v ${{covar_dir}}/eigenvec_e${{etime}}.trr -av ${{covar_dir}}/average_e${{etime}}.pdb -l ${{covar_dir}}/covar_e${{etime}}.log
    echo ${{etime}} $(g_anaeig -v ${{covar_dir}}/eigenvec_e${{etime}}.trr -entropy 2>&1 | grep "Schlitter formula is" | awk '{{print $9}}') >> ${{outputxvg}}

   rm -v ${{covar_dir}}/eigenval_e${{etime}}.xvg
   rm -v ${{covar_dir}}/eigenvec_e${{etime}}.trr
   rm -v ${{covar_dir}}/average_e${{etime}}.pdb
   rm -v ${{covar_dir}}/covar_e${{etime}}.log  
   rm -vrf ${{covar_dir}}
done
# comment the following line when in production run
# echo "returncode: 0"
# remove tmp_dir to minmize # of files
# rm -rfv ${{tmp_dir}}
""".format(**kw)
