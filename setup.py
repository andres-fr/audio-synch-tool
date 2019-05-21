# -*- coding:utf-8 -*-


"""
Deploy script for the package. It has to be in the repository root directory.
Make sure that the config entries are correct!
"""

import setuptools


def setup():
    """
    The proper setup function, adapted from the tutorial in
    https://packaging.python.org/tutorials/packaging-projects/
    """
    with open("README.md", "r") as f:
        long_description = f.read()
    #
    setuptools.setup(
        name="dummypackage-dummyname",
        # the version is automatically handled by "bumpversion"
        version="1.3.0",
        author="Dummy Name",
        author_email="dd@dummysolutions.com",
        description="A dummy package",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/andres-fr/python3-template",
        packages=setuptools.find_packages(exclude=["utest*"]),
        include_package_data=True,
        classifiers=[
            # comprehensive list: https://pypi.org/classifiers/
            "Programming Language :: Python :: 3 :: Only",
            # "Programming Language :: Python",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            # "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"
        ],
    )


if __name__ == "__main__":
    setup()
