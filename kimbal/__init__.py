"""
Package to analyse Kimai time logs
==================================

The name kimbal derives from Kimai and balance.
The package reads exported Kimai time log files as well as further meta data
such as annual and sick leave and analyses the working times. Main purpose is
to derive the balance of working time against the demand.


Structure of kimbal
===================
    kimbal
    ├─ main
    ├─ colourlog
    ├─ loader
    └─ workcal
"""

# Make version available in python console
from ._version import __version__

# Import kimbal modules
from kimbal import loader
from kimbal import colourlog
from kimbal import workcal

# Import classes and logging variables
from .main import Kimai
from .colourlog import CustomFormatter, logger, ch
from .loader import Period
