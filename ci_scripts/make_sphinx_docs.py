# -*- coding:utf-8 -*-


"""
This script generates the package's sphinx autodocs as HTML and PDF from
scratch. Usage example:
python make_sphinx_docs.py -n dummypackage -a "Dummy Dumson"\
       -f .bumpversion.cfg -o docs -l

**WARNING**: The script DELETES any preexisting contents in the given output
directory.
"""
# torch has to be imported to prevent sphinx from crashing in projects
# involving PyTorch and matplotlib:
# https://github.com/pytorch/pytorch/issues/11326
# import torch  # noqa: F401
import os
import shutil  # to remove folder recursively
import argparse
#
import sphinx.cmd.quickstart as sphinx_quickstart
import sphinx.ext.apidoc as sphinx_apidoc
import sphinx.cmd.make_mode as sphinx_build
#
from bumpversion_utils import get_bumpversion


REMOVE_LINE = """html_theme = 'alabaster'\n"""
EXTRA_BEGIN = """
from os.path import abspath, dirname
import sys
MODULE_ROOT_DIR = dirname(dirname(abspath(__file__)))
# append module root directory to sys.path
if MODULE_ROOT_DIR not in sys.path:
    sys.path.insert(0, MODULE_ROOT_DIR)

html_theme = "sphinx_rtd_theme"
"""
EXTRA_END = "\nlatex_elements = {'extraclassoptions': 'openany,oneside'}"


if __name__ == "__main__":
    print("\n\n")
    print("==================================================================")
    print("               STARTED AUTODOC SCRIPT")
    print("==================================================================")
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--package_name",
                        type=str, required=True,
                        help="Name of the Python package to document.")
    parser.add_argument("-a", "--author_name",
                        type=str, required=True,
                        help="Can contain whitespaces if quoted.")
    parser.add_argument("-f", "--bumpversion_config_file",
                        type=str, required=True,
                        help="Filepath to the .bumpversion.cfg to examine.")
    parser.add_argument("-o", "--docs_directory",
                        type=str, required=True,
                        help="Output path. PREEXISTING WILL BE DELETED.")
    parser.add_argument("-l", "--build_latexpdf",
                        action="store_true",
                        help="If given, it will build PDF apart from HTML.")

    args = parser.parse_args()
    #
    PACKAGE_NAME = args.package_name
    AUTHOR = args.author_name
    BUMPVERSION_FILEPATH = args.bumpversion_config_file
    VERSION = get_bumpversion(BUMPVERSION_FILEPATH, as_tuple=False)
    OUT_DIR = args.docs_directory
    BUILD_PDF = args.build_latexpdf

    # Delete outdir if preexisting and create anew
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    os.mkdir(OUT_DIR)

    # call sphinx-quickstart with the given arguments
    quickstart_argv = ["-q", "-p", PACKAGE_NAME, "-a", AUTHOR,
                       # "--makefile", "--batchfile",
                       "--ext-autodoc", "--ext-imgmath", "--ext-viewcode",
                       "--ext-githubpages", "-d", "version="+VERSION,
                       "-d", "release="+VERSION, OUT_DIR]
    sphinx_quickstart.main(argv=quickstart_argv)

    # Since some parameters are sadly hardcoded, it follows some dirty editing:
    conf_py = os.path.join(OUT_DIR, "conf.py")
    with open(conf_py, "r+") as f:  # open in read/write mode:
        lines = f.readlines()
    os.remove(conf_py)
    # remove line, append text at beginning and at end:
    try:
        lines.pop(lines.index(REMOVE_LINE))
    except ValueError:
        print("WARNING: EXPECTED LINE DIDN'T EXIST:", REMOVE_LINE)
    lines.insert(1, EXTRA_BEGIN+"\n")
    lines.append(EXTRA_END+"\n")
    # rewrite edited file to its original path
    with open(conf_py, "w") as f:
        f.writelines(lines)

    # Another dirty hack: the cleanest way to create a fresh apidoc is removing
    # the existing index.rst and running apidoc:
    os.remove(os.path.join(OUT_DIR, "index.rst"))
    apidoc_argv = ["-F", PACKAGE_NAME, "-o", OUT_DIR]
    sphinx_apidoc.main(argv=apidoc_argv)

    # Finally call sphinx build (in its make-mode variant):
    build_output = os.path.join(OUT_DIR, "_build")
    build_html_args = ["html", OUT_DIR, build_output]
    sphinx_build.run_make_mode(args=build_html_args)
    if BUILD_PDF:
        build_pdf_args = ["latexpdf", OUT_DIR, build_output]
        sphinx_build.run_make_mode(args=build_pdf_args)
