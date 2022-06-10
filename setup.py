#!/usr/bin/env python

# Import python packages
from setuptools import setup, find_packages
from os import path
import sys, re

# Define package name
PKGNAME = 'kimbal'

# Read version from file in _version.py
VERSIONFILE= path.join(PKGNAME, "_version.py")
print(VERSIONFILE)
verstrline = open(VERSIONFILE, "rt").read()
try:
    verstrline = open(VERSIONFILE, "rt").read()
except FileNotFoundError:
    print("\x1b[31;20mError: Version file not found. Version must be stored in {pkg}/_version.py.\x1b[0m".format(pkg=PKGNAME))

VSRE = r"^__version__ = ['\']([^'\']*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name=PKGNAME,
    version='0.1.0-DEV',
    author='Peter Bräuer',
    author_email='pb866.git@gmail.com',
    url='https://github.com/pb866/kimbal.git',
    packages=find_packages(),
    install_requires = ['pandas', 'holidays'],
    license='GPL3',
    description='Kimai time log analysis.',
    long_description=open('README.md').read()
)
