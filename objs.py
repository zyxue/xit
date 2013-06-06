import os
import numpy as np

import utils

def parse_xvg(xvgf, col=None):
    """
    This function parses a xvg file, and returns a string of descripition & an
    multi dimensional matrix of data

    NOTE: Before modifing this script, please read carefully the format of you
    target xvg file, make sure it's backward compatible.  and create a new
    TABLE (i.e. class SomeProperty(tables.IsDescription) for the targeted
    property.
    """
    f1 = open(xvgf, 'r')
    desc = []
    data = []
    for line in f1:
        if line.startswith('#') or line.startswith('@'):
            desc.append(line)
        else:
            split_line = line.split()
            if len(split_line) >= 2:                        # Why do I need this line? I forgot
                if col:
                    # added col before the number of results for some property
                    # like do_dssp_E varies for different trajectories, headache!
                    # This problem has been solved by processing the xvg file first 2010-10-05
                    # but this line is left here for future potential usage
                    data.append(tuple(split_line[:col])) # tuple() necessary for table.append
                else:
                    data.append(tuple(split_line))
    f1.close()
    desc = ''.join(desc)
    return desc, data

class Xvg(object):
    def __init__(self, xvgf):
        self.filename = xvgf
        desc, data = parse_xvg(xvgf)
        self.desc = desc
        self.data = data

    def get_desc(self):
        """get the description (basically comments) of this xvgf"""
        return self.desc
    
    def get_data(self):
        """get the data contained (usually muti-dimensional array)"""
        return self.data

    def get_tablename(self, tn=None):
        """
        if tn is specified, tn will be used as the tablename, otherwise, the
        file name will be used
        """
        tablename = tn if tn else os.path.basename(self.filename)
        return tablename

class XPM(object):
    def __init__(self, xpmf):
        # Open the xpm file for reading
        xpm = open(xpmf)
        
        # Read in lines until we fidn the start of the array
        meta = [xpm.readline()]
        while not meta[-1].startswith("static char *gromacs_xpm[]"):
            meta.append(xpm.readline())

        # The next line will contain the dimensions of the array
        dim = xpm.readline()

        # nx: width, ny: height, nc: # of colors, nb: # characters per pixel
        nx, ny, nc, nb = [int(i) for i in self._unquote(dim).split()]

        # The next dim[2] lines contain the color definitions
        # Each pixel is encoded by dim[3] bytes, and a comment
        # at the end of the line contains the corresponding value
        color_map = dict([self._col(xpm.readline()) for i in range(nc)])

        color_count = []
        for i in xpm:
            if i.startswith("/*"):                          # skip comment
                continue
            j = self._unquote(i)
            color_count.append([j.count(k)/float(nx) for k in sorted(color_map.keys())])

            # maybe calculate the number of one color and then do a
            # substraction would be faster, but as long as the file doesn't get
            # too big, count multiple times are acceptable
        xpm.close()

        self.file_name = xpmf
        self.color_map = color_map
        self.nx, self.ny, self.nc, self.nb = nx, ny, nc, nb
        self.color_count = color_count

    def _unquote(self, s):
        return s[1 + s.find('"'): s.rfind('"')]

    def _uncomment(self, s):
        return s[ 2 + s.find('/*'): s.rfind('*/')]

    def _col(self, c):
        color = c.split('/*')
        # value = unquote(color[1])
        symbol, color = self._unquote(color[0]).split('c')
        if symbol.strip():
            symbol = symbol.strip()
        else:                                # meaning symbol is made of space only
            symbol = " "
            # sys.stderr.write("%-40s: %s, %s, %s\n"%(c.strip(), symbol, color, value))
        return symbol, color

class HBNdx(object):
    def __init__(self, hb_ndx_file):
        ndxf = open(hb_ndx_file)

        for line in ndxf:
            if line.lstrip().startswith("["):
                ubline = self._unbracket(line)              # ubline: unbracketed line
                keyn = self._map_ubline(ubline)
                setattr(self, keyn, [])
                ref = getattr(self, keyn)
                flag = keyn
            else:
                sl = line.strip()
                if sl:
                    if flag == "sys":
                        ref.extend(int(i) for i in sl.split())
                    elif flag == "donors":
                        ref.append(int(sl.split()[0]))
                    elif flag == "acceptors":
                        ref.extend(int(i) for i in sl.split())
                    elif flag == "hbonds":
                        sls = sl.split()
                        # order: [donor, acceptor]
                        ref.append([int(sls[0]), int(sls[-1])])

    def _map_ubline(self, ubline):
        dd = {
            'donors_hydrogens': 'donors',
            'acceptors': 'acceptors',
            'hbonds': 'hbonds'
            }
        for i in dd:
            if i in ubline:
                return dd[i]
        return "sys"                                    # meaning no useful key name found in dd

    def _unbracket(self, s):
        return s[1 + s.find('['): s.rfind(']')].strip()

    def get_resid_from_atom(self, atoms, number):
        for a in atoms:
            # +1 because number in MDAnalysis starts from 0, but resid starts from 1
            if a.number + 1 == number:
                return a.resid

    def map_id2resid(self, pro_atoms):
        # pro_atoms: all atoms in the protein
        hbonds_by_resid = []
        for hb in self.hbonds:
            hbr = []
            for i in hb:
                hbr.append(self.get_resid_from_atom(pro_atoms, i))
            hbonds_by_resid.append(hbr)
        return hbonds_by_resid

class Data(object):
    def __init__(self, vals, norm=1.):
        self.vals = vals
        self.mean = np.mean(vals)
        self.sem = utils.sem(vals)
        self.nmean = np.mean(vals) / norm
        self.nsem = utils.sem(vals) / norm

    def __repr__(self):
        return 'mean: {0:.2f}, sem: {1:.2f}'.format(self.mean, self.sem)
