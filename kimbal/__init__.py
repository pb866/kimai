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