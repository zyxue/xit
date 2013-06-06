import os.path
import yaml

root = os.path.curdir

def include(loader, node):
    """Include another YAML file."""

    global root

    old_root = root

    filename = os.path.join(root, loader.construct_scalar(node))
    root = os.path.split(filename)[0]

    data = yaml.load(open(filename, 'r'))

    root = old_root

    return data
