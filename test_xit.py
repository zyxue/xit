from xutils import get_args

def test_get_args():
    test_set = []
    # subcommands = ['prep', 'anal', 'transform', 'plot']
    subcommands = ['prep']
    for subc in subcommands:
        test_set.extend([
                (
                    [subc, '--vars', 'w m'],
                    [['w', 'm']]
                    ),
                (
                    [subc, '--vars', 'sq[1-3]'],
                    [['sq1', 'sq2', 'sq3']]
                    ),
                (
                    [subc, '--vars', 'sq1 sq[3-5]'],
                    [['sq1', 'sq3', 'sq4', 'sq5']]
                    ),
                (
                    [subc, '--vars', 'xy1 xy[3-5]'],
                    [['xy1', 'xy3', 'xy4', 'xy5']]
                    ),
                (
                    [subc, '--vars', 'xy1 xy[3-4] xy8'],
                    [['xy1', 'xy3', 'xy4', 'xy8']]
                    ),
                (
                    [subc, '--vars', 'xy1 xy[3-4] xy8', 'ab[1-3]'],
                    [['xy1', 'xy3', 'xy4', 'xy8'], ['ab1', 'ab2', 'ab3']]
                    ),
                (
                    [subc, '--vars', 'xy1 xy8', '[1-3]'],
                    [['xy1', 'xy8'], ['1', '2', '3']],
                    ),
                (
                    [subc, '--vars', 'xy01 xy12', '[11-13]'],
                    [['xy01', 'xy12'], ['11', '12', '13']],
                    ),
                (
                    [subc, '--vars', 'sq1 sq2', 'w m', '[1-3]'],
                    [['sq1', 'sq2'], ['w', 'm'], ['1', '2', '3']],
                    ),
                (
                    [subc, '--vars', 'sq1', 'ff[1-6]', '[8-11]'],
                    [['sq1'], ['ff1', 'ff2', 'ff3', 'ff4', 'ff5', 'ff6'], ['08', '09', '10', '11']],
                    ),
                (
                    [subc, '--vars', 'sr1_CT3', 'ff1', 'w'],
                    [['sr1_CT3'], ['ff1'], ['w']],
                    ),


                ])
    for input_, expected in test_set:
        try:
            assert get_args(input_).vars == expected
        except AssertionError:
            print '{0:20s}: {1}\n{2:20s}: {3}\n{4:20s}: {5}\n'.format(
                'input', input_, 'expected', expected, 'output', get_args(input_).vars)

if __name__ == "__main__":
    test_get_args()
