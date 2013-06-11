import logging
logger = logging.getLogger(__name__)

"""
everytime when adding a table, remember to add relevant info in
    __tables__
    class table_name(tables.IsDescription):
    d (in the Property class)

than modify the h5.conf in the directory you are working on
"""

import tables

class e2ed(tables.IsDescription):
    """
    end-to-end distance data along the time trjectory
    VERY STRANGE: docstring doesn't work for subclass of tables.IsDescription 2012-12-13
    """
    time = tables.Float32Col(pos=0)
    e2ed = tables.Float32Col(pos=1)
    e2edx = tables.Float32Col(pos=2)
    e2edy = tables.Float32Col(pos=3)
    e2edz = tables.Float32Col(pos=4)

class rama(tables.IsDescription):
    """
    phi, psi: dihedral angles
    aa: amino acid
    """
    phi = tables.Float32Col(pos=0)
    psi = tables.Float32Col(pos=1)
    # For types with a non-fixed size, this sets the size in bytes of individual items in the column.
    aa  = tables.StringCol(itemsize=10, pos=2)

class rg(tables.IsDescription):
    """
    Radius of gyration of C alpha along the time trjectory
    """
    time = tables.Float32Col(pos=0)
    rg = tables.Float32Col(pos=1)
    rg_x = tables.Float32Col(pos=2)
    rg_y = tables.Float32Col(pos=3)
    rg_z = tables.Float32Col(pos=4)

class omega_percent(tables.IsDescription):
    """
    percentage of: cis trans peptide bonds
    """
    replica_id  = tables.StringCol(itemsize=10, pos=0)
    trans_x_pro = tables.Float32Col(pos=1)
    cis_x_pro = tables.Float32Col(pos=2)
    trans_y_x = tables.Float32Col(pos=3)
    cis_y_x = tables.Float32Col(pos=4)

class dssp(tables.IsDescription):
    """
    # This table must be redesigned and do_dssp program modified if you want to
    # do all secondary structure(ss) analysis, doing do_dssp for each ss is
    # unacceptable.

    dssp analysis, 
    E: extended conformation
    H: alpha helix
    T: turn
    B: isolated bridge
    G: 3-10 helix
    I: pi helix
    C: coil
    S: Bend (ono-hydrogen-bond based assignment)
    """
    time = tables.Float32Col(pos=0)
    structure = tables.UInt32Col(pos=1)
    # number of structure types vary, which is a headache!
    # Coil = tables.UInt32Col(pos=2)
    # b-sheet = tables.Float32Col(pos=3)
    # rg_z = tables.Float32Col(pos=4)

class seqspacing(tables.IsDescription):
    """
    sequence_spacing
    """
    dij = tables.UInt32Col(pos=0)
    ave_d = tables.Float32Col(pos=1)
    std_d = tables.Float32Col(pos=2)
    num_data_points = tables.UInt32Col(pos=3)

class pmf(tables.IsDescription):
    """potential of mean force"""
    x = tables.Float32Col(pos=0)
    pmf = tables.Float32Col(pos=1)

class entropy(tables.IsDescription):
    time = tables.Float32Col(pos=0)
    entropy = tables.Float32Col(pos=1)
    # number of structure types vary, which is a headache!
    # Coil = tables.UInt32Col(pos=2)
    # b-sheet = tables.Float32Col(pos=3)
    # rg_z = tables.Float32Col(pos=4)

# itemsize : int
# For types with a non-fixed size, this sets the size in bytes of individual items in the column.
# shape : tuple
# Sets the shape of the column. An integer shape of N is equivalent to the tuple (N,).
# dflt :
# Sets the default value for the column.
# pos : int
# Sets the position of column in table. If unspecified, the position will be randomly selected.

class upup(tables.IsDescription):
    """upup along the time trajectory"""
    time = tables.Float32Col(pos=0)
    upup = tables.UInt32Col(pos=1)
    within_0_35nm = tables.UInt32Col(pos=2)

class upun(tables.IsDescription):
    """upun along the time trajectory"""
    time = tables.Float32Col(pos=0)
    upun = tables.UInt32Col(pos=1)

class unun(tables.IsDescription):
    """unun along the time trajectory"""
    time = tables.Float32Col(pos=0)
    unun = tables.UInt32Col(pos=1)

class upvp(tables.IsDescription):
    """upvp along the time trajectory"""
    time = tables.Float32Col(pos=0)
    upvp = tables.UInt32Col(pos=1)
    upvp_within_0_35nm = tables.UInt32Col(pos=2)

class upvn(tables.IsDescription):
    """upvn along the time trajectory"""
    time = tables.Float32Col(pos=0)
    upvn = tables.UInt32Col(pos=1)

class unvn(tables.IsDescription):
    """unvn along the time trajectory"""
    time = tables.Float32Col(pos=0)
    unvn = tables.UInt32Col(pos=1)

class unvp(tables.IsDescription):
    """unvp along the time trajectory"""
    time = tables.Float32Col(pos=0)
    unvp = tables.UInt32Col(pos=1)

#################### upv unv ####################

class upv(tables.IsDescription):
    """upv along the time trajectory"""
    time = tables.Float32Col(pos=0)
    upv = tables.UInt32Col(pos=1)

class unv(tables.IsDescription):
    """unv along the time trajectory"""
    time = tables.Float32Col(pos=0)
    unv = tables.UInt32Col(pos=1)

#################### rdf ####################

class rdf(tables.IsDescription):
    """rdf along the time trajectory"""
    radius = tables.Float32Col(pos=0)
    rdf = tables.Float32Col(pos=1)


SCHEMA_DICT = {
    'e2ed'          : e2ed,
    'e2ed_wl'       : e2ed,
    'rg_c_alpha'    : rg,
    'rg_c_alpha_wl' : rg,

    # 'e2ed'           : (e2ed, "e2ed"),   # end-to-end distance data along the time trjectory
    # 'rg_c_alpha'     : (rg, "rg"),       # Radius of gyration of C alpha along the time trjectory
    # 'rg_backbone'    : (rg, "rg"),       # Radius of gyration of backbone along the time trjectory

    'seqspacing'     : seqspacing,                          # sequence spacing
    'pmf_e2ed'       : pmf,                        # potential_of_mean_force along e2ed
    # 'omega_percent': (omega_percent, 'percentage of cis trans peptide bonds'),
    
    'dssp_E': dssp,                  # dssp_E (b-sheet)
    'dssp_H': dssp,                  # dssp_H (alpha-helix)
    'dssp_T': dssp,                  # dssp_T (hydrogen bonded turn)
    'dssp_G': dssp,                  # dssp_G (3-helix)
    'dssp_I': dssp,                  # dssp_I (5-helix)
    'dssp_B': dssp,                  # dssp_B (residue in isolated beta-bridge)
    'dssp_C': dssp,                  # dssp_C (coil)
    'dssp_S': dssp,                  # dssp_S (Bend)
    'dssp_X': dssp,                  # dssp_X (Bend)

    'rama': rama,
    'rama_GLY': rama,
    'rama_VAL': rama,
    'rama_PRO': rama,
    'rama_ALA': rama,


    'upup': upup,
    # 'upun': upun,
    'unun': unun,
    'unun_wl': unun,
    'upvp': upvp,             # intermolecular hbond) along the time trajectory
    'upvn': upvn,             # upvn along the time trajectory
    'unvn': unvn,             # unvn along the time trajectory
    'unvp': unvp,             # unvp along the time trajectory
    
    'upv':  upv,                              # upv along the time trajectory',
    'unv':  unv,                              # unv along the time trajectory'
    
    # 'rdf_upup': (rdf, 'rdf along the time trajectory'),
    # 'rdf_upun': (rdf, 'rdf along the time trajectory'),
    # 'rdf_unun': (rdf, 'rdf along the time trajectory'),
    # 'rdf_upvp': (rdf, 'rdf along the time trajectory'),
    # 'rdf_upvn': (rdf, 'rdf along the time trajectory'),
    # 'rdf_unvp': (rdf, 'rdf along the time trajectory'),
    # 'rdf_unvn': (rdf, 'rdf along the time trajectory'),
    
    # 'rdf_un1vn': (rdf, 'rdf along the time trajectory'),
    # 'rdf_un2vn': (rdf, 'rdf along the time trajectory'),
    # 'rdf_un3vn': (rdf, 'rdf along the time trajectory'),
    # 'rdf_un1vp': (rdf, 'rdf along the time trajectory'),
    # 'rdf_un2vp': (rdf, 'rdf along the time trajectory'),
    # 'rdf_un3vp': (rdf, 'rdf along the time trajectory'),
    
    'rdf_c1vn': rdf,
    'rdf_c2vn': rdf,
    'rdf_c3vn': rdf,
    'rdf_c1vp': rdf,
    'rdf_c2vp': rdf,
    'rdf_c3vp': rdf,
    
    # 'conf_entropy': (entropy, 'entropy with increasing sampling'),
    
    }

INTERESTED_FIELDS = {
    'e2ed'             : 'e2ed',
    'e2ed_wl'          : 'e2ed',
    'rg_c_alpha'       : 'rg',
    'rg_c_alpha_wl'    : 'rg',
    'upup'             : 'upup',
    'unun'             : 'unun',
    'unun_wl'          : 'unun',

    'upvp': 'upvp',
    'upvn': 'upvn',
    'unvn': 'unvn',
    'unvp': 'unvp',

    'upv': 'upv',
    'unv': 'unv',

    'dssp_E': 'structure',
    'dssp_E': 'structure',
    'dssp_H': 'structure',
    'dssp_T': 'structure',
    'dssp_G': 'structure',
    'dssp_I': 'structure',
    'dssp_B': 'structure',
    'dssp_C': 'structure',
    'dssp_S': 'structure',
    'dssp_X': 'structure',

    'seqspacing'       : 'ave_d',

    'rdf_c1vn': 'rdf',
    'rdf_c2vn': 'rdf',
    'rdf_c3vn': 'rdf',
    'rdf_c1vp': 'rdf',
    'rdf_c2vp': 'rdf',
    'rdf_c3vp': 'rdf',


    }

from mysys import read_mysys
mysys = read_mysys.read()

NO_SCHEMA = ['upup_map']

class Property(object):
    def __init__(self, pn):                                 # p: property name
        """values of d contain two parts: the table class & its description"""
        self.name = pn
        self.schema = None if pn in NO_SCHEMA else SCHEMA_DICT[pn]
        if pn in INTERESTED_FIELDS.keys():
            self.ifield = INTERESTED_FIELDS[pn]

    # def norm(self, x):
    #     # x could be sq1, sq2; w, m, etc. depending on mysys
    #     # THIS design is ugly and not very useful
    #     if self.name in ['rg_c_alpha', 'rg_wl']:
    #         return 1
    #     elif self.name in ['upup', 'upup_map']:
    #         return mysys[x].hbg
    #     elif self.name == 'unun':
    #         return mysys[x].scnpg
    #     else:
    #         raise ValueError("unknown norm for analysis: {0}".format(x))

if __name__ == "__main__":
    a = e2ed
