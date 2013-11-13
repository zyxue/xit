import re
import os
import time
import shutil
from functools import update_wrapper

def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(args)
    return _f

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        res = method(*args, **kw)
        te = time.time()
        # cannot use logging.info: guess due to namespacing problem
        print '--- spent: {0:.1e}s on {1}'.format(te - ts, method.__name__)
        # print '--- spent: {0}    on {1}\n'.format(
        #         time.strftime('%H:%M:%S', time.gmtime(delta_time)),
        #         method.__name__)
        return res
    return timed

def backup_file(f):
    if os.path.exists(f):
        dirname = os.path.dirname(f)
        basename = os.path.basename(f)
        count = 1
        rn_to = os.path.join(
            dirname, '#' + basename + '.{0}#'.format(count))
        while os.path.exists(rn_to):
            count += 1
            rn_to = os.path.join(
                dirname, '#' + basename + '.{0}#'.format(count))
        print "BACKING UP {0} to {1}".format(f, rn_to)
        shutil.copy(f, rn_to)
        return rn_to
        print "BACKUP FINISHED"


def gen_paths_dict(core_vars):
    PATH_KEY_RE = re.compile('path\d+')
    paths = {}
    # data structure of paths with depth as the key
    # paths = {
    #     1: set(d1, d2),
    #     2: set(d1/dd1, d1/dd2, d2/dd1, d2/dd2),
    #     3: set(d1/dd1/ddd1, d1/dd1/ddd2,
    #            d1/dd2/ddd1, d1/dd2/ddd2,
    #            d2/dd1/ddd1, d2/dd1/ddd2,
    #            d2/dd2/ddd1, d2/dd2/ddd2),
    #     }
    for cv in core_vars:
        for key in cv.keys():
            if re.match(PATH_KEY_RE, key):
                path = cv[key]
                depth = path.count('/') + 1
                if depth in paths:
                    paths[depth].add(path)
                else:
                    paths[depth] = set([path])
    return paths
