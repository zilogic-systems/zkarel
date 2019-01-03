from distutils.dir_util import copy_tree
import pkg_resources
import os
import sys

def err(msg):
    print("{}: {}".format(sys.argv[0], msg), file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) == 1:
        lang = "python"
    else:
        lang = sys.argv[1]

    supported_lang = ("python",)

    if lang not in supported_lang:
        err("Unsupported language '{}'".format(lang))
    
    wdir = pkg_resources.resource_filename(__name__, os.path.join("workspace", lang))
    copy_tree(wdir, os.getcwd())
    
