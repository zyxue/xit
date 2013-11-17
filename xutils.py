import re
import argparse
import logging
logger = logging.getLogger(__name__)

# from analysis_methods import PROPERTIES, ANALYSIS_METHODS
# from plot_types import PLOT_TYPES
# from plotmp_types import PLOTMP_TYPES

"""Here contains not as basic util functions that need to import import any
other local xit-specific modules"""

class convert_vars(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        final = []
        for value in values:
            subfinal = []
            svalue = value.split()
            for val in svalue:
                # not trivial a regex that works!
                # this does not work with names like sr1_CT3, g3ub
                mat = re.match('([a-zA-Z_0-9]*)((?:\[\d+-\d+\])?)$', val)
                if mat:                                     # mat: match
                    prefix, num = mat.groups()
                    if num == '':
                        subfinal.append(prefix)
                    else:
                        mmat = re.search('\[(\d+)-(\d+)\]', num)
                        if mmat:                              # mmat: another match
                            min_, max_ = mmat.groups()
                            l = max([len(min_), len(max_)])
                            fmt = '{{0}}{{1:0{l}d}}'.format(l=l)
                            min_, max_ = (int(i) for i in mmat.groups())
                            res = [fmt.format(prefix, i) for i in xrange(min_, max_ + 1)]
                            subfinal.extend(res)
                        else:
                            fmt = '{{0}}{{1:0{l}d}}'.format(l=len(num))
                            subfinal.append(fmt.format(prefix, int(num)))
                else:
                    raise ValueError('unkown input: {0}'.format(val))
            final.append(subfinal)
        setattr(namespace, self.dest, final)

def get_cmd_args(args_to_parse=None):
    """
    :param args_to_parse list of arguments
    :type args_to_parse list
    """
    parser = argparse.ArgumentParser(description="xit helps you prepare, manage and analyze your simulations")
    subparsers = parser.add_subparsers(title='subcommands')

    prep_parser = subparsers.add_parser('prep', help='used during simulation preparation')

    mgrp = prep_parser.add_mutually_exclusive_group()
    mgrp.add_argument('--mkdir', action='store_true', help='make directories based on .xitconfig.yaml')
    mgrp.add_argument('--sed', dest='sed_files_key', default=None, nargs='?',
                      help=('the key corresponding to the files to be sed, e.g. top, premdrun, mdrun, '
                            'or you could specify "ALL" to let xit '
                            'sed every files found in sed_templates in the .xitconfig.yaml'))
    mgrp.add_argument('--exec', dest='exec_files_key', default=None,
                      help=('the key corresponding to the files to be executed'
                            'e.g. premdrun, mdrun (especially when they will finish shortly, '
                            "and you don't want to submit them to the job queueing system"))
    mgrp.add_argument('--qsub', dest='qsub_files_key', 
                      help='the key corresponding to the files to be qsub-ed to the queueing system')

    prep_parser.add_argument('--overwrite', action='store_true', help='overwrite previous files when do --sed')

    anal_parser = subparsers.add_parser(
        'anal', help='do different sorts of analysis')
    anal_parser.add_argument('--numthreads', type=int, default=16, help='number of threads')
    anal_parser.add_argument('--test', action='store_true', help='if test, print the cmd without executing it')
    anal_parser.add_argument('--nolog', action='store_true', help='disable logging, output to stdout')
    anal_parser.add_argument('-b', default=0, help='gromacs -b')
    anal_parser.add_argument('-e', default=-1, help='gromacs -e')
    anal_parser.add_argument('--use_pro', action='store_true', 
                             help=("use proxtcf instead of orderxtcf for quick analysis, "
                                   "especially when the later hasn't been generated"))
    anal_parser.add_argument('--opt_arg', help=('this is used for tool specific arguments specified'
                                                'in the .xitconfig.yaml file (e.g. var1, var2, or var3)'))

    transform_parser = subparsers.add_parser(
        'transform', help=('transform the file formats from analysis step (e.g. xvg) to hdf5 format, '
                           'if the previous one is in hdf5 already, then this step is unecessary.'))
    transform_parser.add_argument('-t' , '--filetype', default='xvg', 
                                  help=('e.g. xvg, xpm, or dependent, which is property-specific, '
                                        'e.g. upv depends on upvp and upvn'))
    transform_parser.add_argument('--overwrite', action='store_true', 
                                  help='overwrite previous data, used when doing transform or plotting')
    transform_parser.add_argument('--init_hdf5', action='store_true', help='initialize hdf5, creating dirs, etc.')

    plot_parser = subparsers.add_parser(
        'plot', help='postprocess the results from analysis and illustrate it via plotting')

    plot_parser.add_argument('--plot_type', choices='LELE', help='NEED A NEW STRATEGY TO LIST THIS')
    # plot_parser.add_argument('--plot_type', choices=PLOT_TYPES.keys(), help='e.g {0}'.format(PLOT_TYPES.keys()))

    # plot_parser.add_argument('--scale', action='store_true', help='scale to 1, when map plotting is not obvious')

    # shouldn't be used, instead put it in the .xitconfig.yaml --2013-05-09
    # plot_parser.add_argument('--normid', help='var1, etc')

    plotmp_parser = subparsers.add_parser(
        'plotmp', help='similar to plot, but handles two properties at the same time')
    plotmp_parser.add_argument('--plotmp_type', choices='LELE', help='NEED A NEW STRATEGY TO LIST THIS')
    # plotmp_parser.add_argument('--plotmp_type', choices=PLOTMP_TYPES.keys(), help='{0}'.format(PLOTMP_TYPES.keys()))
    plotmp_parser.add_argument('-p' , '--properties', nargs='+',
                               help=('added MULTIPLE properties, which is different '
                                     'than a single property in plot. e.g. "upup unun"'))

    for p in [plot_parser, plotmp_parser]:
        p.add_argument('--grptoken', required=True, help='how to group the original  directories? e.g. path2')
        p.add_argument('--merge', action='store_true', help='merge all plots in one ax')
        p.add_argument('--overwrite', action='store_true', help='overwrite previous postprocess data')
        p.add_argument('-o', '--output', help='output file')
        p.add_argument('--output_format', choices=['png', 'pdf'], help='png (default), pdf')

    for p in [prep_parser, anal_parser, transform_parser, plot_parser, plotmp_parser]:
        # forget what the following two lines mean ---2013-05-09
        # f is used to add global_args, it does not work with argparse to put
        # --vars in right after argparse.ArgumentParser, which is strange
        p.add_argument('--vars', nargs='+', action=convert_vars,
                       help='list of vars, as defined in the .xit file, command line options override .xit')
        p.add_argument('-g', '--config', default='.xitconfig.yaml', help='specify the config option if not default')
        p.add_argument('--nobackup', action='store_true', help="don't back the file to speed up analysis")
        p.add_argument('--loglevel', default='info', help="don't back the file to speed up analysis")
        p.add_argument('-v', action='store_true', help="enable verbose output")
        p.add_argument('--vv', action='store_true', help="enable very verbose output")
        p.add_argument('--vvv', action='store_true', help="enable very very verbose output")

    for p in [anal_parser]:
        p.add_argument('-a' , '--analysis', required=True, help='NEED A NEW STRATEGY TO LIST THIS')
        # p.add_argument('-a' , '--analysis', required=True, help='{0}'.format(ANALYSIS_METHODS.keys()))

    for p in [transform_parser, plot_parser]:
        p.add_argument('-p' , '--property', help='NEED A NEW STRATEGY TO LIST THIS')
        # p.add_argument('-p' , '--property', help='{0}'.format(PROPERTIES.keys()))

    for p in [anal_parser, transform_parser, plot_parser, plotmp_parser]:
        p.add_argument('--hdf5', help='specify the .h5 file to use if not configured in .xitconfig.yaml')

    args = parser.parse_args(args_to_parse)
    return args
