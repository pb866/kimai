# Make version available in python console
from ._version import __version__

# Import classes and logging variables
from .main import Kimai
from .main import CustomFormatter, logger, ch

# Import kimbal modules
from kimbal import dataimport
