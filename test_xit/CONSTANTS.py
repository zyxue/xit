CORE_VARS = [
    {'dir1': 'test_epz1', 'dir2': 'h', 'dir3': '00',
     'path1': 'test_epz1', 'path2': 'test_epz1/h', 'path3': 'test_epz1/h/00',
     'var1': 'test_epz1', 'var2': 'h', 'var3': 8, 'var4': '00',
     'id_': 'test_epz1h8_00'
     },
    {'dir1': 'test_epz1', 'dir2': 'e', 'dir3': '00',
     'path1': 'test_epz1', 'path2': 'test_epz1/e', 'path3': 'test_epz1/e/00',
     'var1': 'test_epz1',  'var2': 'e', 'var3': 8, 'var4': '00',
     'id_': 'test_epz1e8_00'
     },
    {'dir1': 'test_epz1', 'dir2': 'h', 'dir3': '01', 
     'path1': 'test_epz1', 'path2': 'test_epz1/h', 'path3': 'test_epz1/h/01',
     'var1': 'test_epz1', 'var2': 'h', 'var3': 8, 'var4': '01', 
      'id_': 'test_epz1h8_01'
     },
    {'dir1': 'test_epz1', 'dir2': 'e', 'dir3': '01',
     'path1': 'test_epz1', 'path2': 'test_epz1/e', 'path3': 'test_epz1/e/01',
     'var1': 'test_epz1', 'var2': 'e', 'var3': 8, 'var4': '01',
     'id_': 'test_epz1e8_01'
     },
    {'dir1': 'test_epz1', 'dir2': 'h', 'dir3': '02',
     'path1': 'test_epz1', 'path2': 'test_epz1/h', 'path3': 'test_epz1/h/02',
     'var1': 'test_epz1', 'var2': 'h', 'var3': 8, 'var4': '02',
     'id_': 'test_epz1h8_02'
     },
    {'dir1': 'test_epz1', 'dir2': 'e', 'dir3': '02', 
     'path1': 'test_epz1', 'path2': 'test_epz1/e', 'path3': 'test_epz1/e/02',
     'var1': 'test_epz1', 'var2': 'e', 'var3': 8, 'var4': '02',
     'id_': 'test_epz1e8_02'}
    ]

DIR_DICT = {
    1: set(['test_epz1']),
    2: set(['test_epz1/e', 'test_epz1/h']),
    3: set(['test_epz1/e/00', 'test_epz1/e/01', 'test_epz1/e/02',
            'test_epz1/h/00', 'test_epz1/h/01', 'test_epz1/h/02',
            ])
    }

DIR_LIST =  ['test_epz1', 
             'test_epz1/e', 'test_epz1/h', 
             'test_epz1/e/00', 'test_epz1/e/01', 'test_epz1/e/02',
             'test_epz1/h/00', 'test_epz1/h/01', 'test_epz1/h/02']
