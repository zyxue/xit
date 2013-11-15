import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
import unittest

import xutils

class XutilsTestCase(unittest.TestCase):
    def testPrepMkdir(self):
        args = xutils.get_cmd_args(['prep', '--mkdir'])
        self.assertTrue(args.mkdir)

    def testPrepSedDefault(self):
        args = xutils.get_cmd_args(['prep', '--sed'])
        self.assertIsNone(args.sed_files_key)

    def testPrepSedPreMdrun(self):
        args = xutils.get_cmd_args(['prep', '--sed', 'pre_mdrun'])
        self.assertEqual(args.sed_files_key, 'pre_mdrun')

    def testPrepExec(self):
        args = xutils.get_cmd_args(['prep', '--exec', 'pre_mdrun'])
        self.assertEqual(args.exec_files_key, 'pre_mdrun')

    def testPrepQsub(self):
        args = xutils.get_cmd_args(['prep', '--qsub', 'mdrun'])
        self.assertEqual(args.qsub_files_key, 'mdrun')
        
