import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
import shutil

import unittest

import xit
import utils as U
import settings as S
import xutils
import prep

import CONSTANTS as const

class PrepTestCase(unittest.TestCase):
    def setUp(self):
        self.core_vars = const.CORE_VARS
        self.C = const.C
        
    def testMkdir(self):
        paths = const.DIR_LIST
        prep.mkdir(self.core_vars)
        for p in paths:
            self.assertTrue(os.path.exists(p))

    def testSedFiles(self):
        prep.sed_files(self.core_vars, self.C['prep'], f_overwrite=True)

    # def tearDown(self):
    #     paths = const.DIR_DICT
    #     for p in paths[1]:      # remove those of least depath
    #         shutil.rmtree(p)


        # for reference only, remove dir one by one
        # depths = sorted(paths.keys(), reverse=True)
        # max_depth = max(depths)        
        # for dp in depths:
        #     for p in paths[dp]:
        #         print p
        #         if dp == max_depth:
        #             #  eq_p: equilibration path
        #             eq_p = os.path.join(p, eq_dir_name)
        #             os.rmdir(eq_p)
        #         os.rmdir(p)
