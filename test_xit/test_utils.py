import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

import unittest
import utils

# to avoid name overlap with settings.py in the parent directory
import CONSTANTS as const

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.core_vars = const.CORE_VARS

    def testGenPathsDict(self):
        self.assertEqual(utils.gen_paths_dict(self.core_vars),
                         const.DIR_DICT)
    # def testMkdir(self):

    
