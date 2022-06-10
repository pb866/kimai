"""
Module of kimbal package for colouring log messages
===================================================

The colourlog module formats log entries and assigns specific colours to the
debug messages, infos, warnings, errors, and critical errors.
"""


# Import python packages
import logging


class CustomFormatter(logging.Formatter):
    f"""
    Adds colours to log messages.

    Defines colours for debug, info, warning, error, and critical level and formats log messages.
    """

    dbg = "\x1b[35;20m"
    inf = "\x1b[36;20m"
    wrn = "\x1b[33;20m"
    err = "\x1b[31;20m"
    crt = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: dbg + format + reset,
        logging.INFO: inf + format + reset,
        logging.WARNING: wrn + format + reset,
        logging.ERROR: err + format + reset,
        logging.CRITICAL: crt + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("Kimai")
# logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
