CORE_VARS = [
    {'dir1': 'lele_epz1', 'dir2': 'h', 'dir3': '00',
     'path1': 'lele_epz1', 'path2': 'lele_epz1/h', 'path3': 'lele_epz1/h/00',
     'var1': 'lele_epz1', 'var2': 'h', 'var3': 8, 'var4': '00',
     'id_': 'lele_epz1h8_00'
     },
    {'dir1': 'lele_epz1', 'dir2': 'e', 'dir3': '00',
     'path1': 'lele_epz1', 'path2': 'lele_epz1/e', 'path3': 'lele_epz1/e/00',
     'var1': 'lele_epz1',  'var2': 'e', 'var3': 8, 'var4': '00',
     'id_': 'lele_epz1e8_00'
     },
    {'dir1': 'lele_epz1', 'dir2': 'h', 'dir3': '01', 
     'path1': 'lele_epz1', 'path2': 'lele_epz1/h', 'path3': 'lele_epz1/h/01',
     'var1': 'lele_epz1', 'var2': 'h', 'var3': 8, 'var4': '01', 
      'id_': 'lele_epz1h8_01'
     },
    {'dir1': 'lele_epz1', 'dir2': 'e', 'dir3': '01',
     'path1': 'lele_epz1', 'path2': 'lele_epz1/e', 'path3': 'lele_epz1/e/01',
     'var1': 'lele_epz1', 'var2': 'e', 'var3': 8, 'var4': '01',
     'id_': 'lele_epz1e8_01'
     },
    {'dir1': 'lele_epz1', 'dir2': 'h', 'dir3': '02',
     'path1': 'lele_epz1', 'path2': 'lele_epz1/h', 'path3': 'lele_epz1/h/02',
     'var1': 'lele_epz1', 'var2': 'h', 'var3': 8, 'var4': '02',
     'id_': 'lele_epz1h8_02'
     },
    {'dir1': 'lele_epz1', 'dir2': 'e', 'dir3': '02', 
     'path1': 'lele_epz1', 'path2': 'lele_epz1/e', 'path3': 'lele_epz1/e/02',
     'var1': 'lele_epz1', 'var2': 'e', 'var3': 8, 'var4': '02',
     'id_': 'lele_epz1e8_02'}
    ]

DIR_DICT = {
    1: set(['lele_epz1']),
    2: set(['lele_epz1/e', 'lele_epz1/h']),
    3: set(['lele_epz1/e/00', 'lele_epz1/e/01', 'lele_epz1/e/02',
            'lele_epz1/h/00', 'lele_epz1/h/01', 'lele_epz1/h/02',
            ])
    }

DIR_LIST =  ['lele_epz1', 
             'lele_epz1/e', 'lele_epz1/h', 
             'lele_epz1/e/00', 'lele_epz1/e/01', 'lele_epz1/e/02',
             'lele_epz1/h/00', 'lele_epz1/h/01', 'lele_epz1/h/02']

C = {
    'prep': {
        'sed_templates': {
            'top': 'repository/top.template',
            'pre_mdrun': 'repository/0_pre_mdrun.sh.template',
            'mdrun': 'repository/0_mdrun.sh.template',
            }
        }
    }

        
