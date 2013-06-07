import os
import logging
logger = logging.getLogger(__name__)

import tables
import numpy as np
from MDAnalysis import Universe

import utils as U
import objs
import prop

def transform(A, C, core_vars):
    h5 = U.get_h5(A, C)

    if A.init_hdf5:
        init_hdf5(h5, core_vars)
        return 

    anal_dir = C['data']['analysis']

    for cv in core_vars:
        id_, dpp = cv['id_'], os.path.join('/', U.get_dpp(cv))
        # ad: anal dir, out of names
        adir = os.path.join(anal_dir, 'r_{0}'.format(A.property))
        # af: anal file
        afile = os.path.join(adir, '{0}_{1}.{2}'.format(id_, A.property, A.filetype))

        tb_name = A.property
        tb_path = os.path.join(dpp, tb_name)
        if h5.__contains__(tb_path):
            tb = h5.getNode(tb_path)
            if not A.overwrite:
                logger.info("{0} ALREADY EXISTS in {1}".format(os.path.join(dpp, tb.name), h5.filename))
            else:
                # overwrite with new data
                tb.remove()
                tb = put_data(A.filetype, afile, 
                              prop.Property(A.property).schema,
                              h5, dpp, tb_name, cv, A, C)
                if tb:
                    logger.info("{0} is overwritten with new data".format(tb_path))
        else:
            # tb_or_ar: table or array, or None
            tb_or_ar = put_data(A.filetype, afile, 
                                prop.Property(A.property).schema,
                                h5, dpp, tb_name, cv, A, C)
            if tb_or_ar:
                logger.info("{0} IS TRANSFORMED to {1}".format(afile, tb_path))

def put_data(ft, f, schema, h5, dpp, tb_name, cv, A, C):
    if not os.path.exists(f) and ft != 'dependent':
        logger.info("ATTENTION: {0} doesn't exist! (You may want to consider --filetype dependent)".format(f))
        return

    if ft == 'xvg':
        fobj = objs.Xvg(f)
        tb = h5.createTable(where=dpp, name=tb_name, 
                            description=schema,
                            title=fobj.desc)
        tb.append(fobj.data)
        return tb
    elif ft == 'xpm':                                       # e.g. hbond map
        xpmf = f
        ndxf = f.replace('.xpm', '.ndx')
        dpp = U.get_dpp(cv)
        io_files = U.gen_io_files(dpp, cv['id_'])
        grof = io_files['ordergrof']
        flist = [xpmf, ndxf, grof]
        for i in flist:
            assert os.path.exists(i) == True
        hb_map = gen_hbond_map(*flist)                      # hb_map: hbond map
        ar = h5.createArray(where=dpp, name=tb_name, object=hb_map)
        return ar

    # if the code here starts to be executed, then it means filetype is
    # dependent, and it's dealt with case by case because usually the handling
    # is quite specific
    if A.property == 'upv':
        stuff = dpt_sum_alx(h5, dpp, 'time', 'upvp', 'upvn')
        tb = h5.createTable(where=dpp, name=tb_name, description=schema)
        # if without astype(), numbers would become huge, i.e. overflow
        tb.append(stuff.astype('uint32'))
        return tb
    elif A.property == 'unv':
        stuff = dpt_sum_alx(h5, dpp, 'time', 'unvp', 'unvn')
        tb = h5.createTable(where=dpp, name=tb_name, description=schema)
        tb.append(stuff.astype('uint32'))
        return tb
    else:
        raise ValueError(
            "Don't know how to transform property '{0}' of filetype 'dependent'".format(A.property))

    import sys
    sys.exit

def dpt_sum_alx(h5, dpp, xfield_name, *args):
    """put data of dependent (dpt) filetype, the way it's handled is sum y along x axis"""
    p0 = args[0]                            # args must be at least be of len 1
    node = h5.getNode(dpp, p0)
    xdata = node.read(field=xfield_name)
    sum_ = node.read(field=p0) # assume the node name is the same as the property/analysis name
    for arg in args[1:]:
        if h5.__contains__(os.path.join(dpp, arg)):
            s = h5.getNode(dpp, arg).read(field=arg)
            sum_ = sum_ + s
    res = np.array([xdata, sum_])
    return res.transpose()

def gen_hbond_map(xpm, ndx, grof):
    xpm = objs.XPM(xpm)
    hbndx = objs.HBNdx(ndx)

    univ = Universe(grof)
    pro_atoms = univ.selectAtoms('protein and not resname ACE and not resname NH2')
    hbonds_by_resid = hbndx.map_id2resid(pro_atoms)

    # pl: peptide length
    pl = pro_atoms.residues.numberOfResidues()

    hblist = []
    for i, j in zip(hbonds_by_resid, xpm.color_count):
        # j[1] is the probability of hbonds, while j[0] = 1 - j[1]
        # format: [resid of donor, resid of acceptor]
        # -1 is because resid in MDAnalysis starts from 1, minus so as to fit
        # -into hb_map initialized by hb_map
        hblist.append([i[0]-1, i[1]-1, j[1]])

    # +1: for missing resname ACE, such that it's easier to proceed in the next
    # step
    pl1 = pl + 1
    hb_map = np.zeros((pl1, pl1))
    for _ in hblist:
        hb_map[_[0]][_[1]] = _[2]

    return hb_map

def init_hdf5(h5, core_vars):
    """ init hdf5 if first time, make sure the directory hierarchy exists in hdf5 """
    filters = tables.Filters(complevel=8, complib='zlib')
    paths = U.gen_paths_dict(core_vars)
    depths = sorted(paths.keys())
    for dp in depths:
        ps = paths[dp]
        print ps
        for p in ps:
            p = os.path.join('/', p)
            dirname = os.path.dirname(p)
            basename = os.path.basename(os.path.join('/', p))
            if not h5.__contains__(p):
                logger.info('creating... {0}'.format(p))
                h5.createGroup(where=dirname, name=basename, filters=filters)
            else:
                logger.info('{0} Already existed'.format(p))
