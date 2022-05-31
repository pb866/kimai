# Make version available in python console
from ._version import __version__

# Import classes and logging variables
from .main import Kimai
from .colourlog import CustomFormatter, logger, ch

# Import kimbal modules
from kimbal import dataimport
from kimbal import colourlog
