"""
Module of kimbal package for loading Kimai data
===============================================

The module contains classes and methods to reading csv files exported from
Kimai time logs.
"""

# Import python packages
from os import path, strerror
from sys import exit
import errno
import pandas as pd
import datetime as dt
from collections import namedtuple
from kimbal.colourlog import logger

# Define Period named tuple
Period = namedtuple("Period", ["start", "end"],
                    defaults=[dt.date(1900, 1, 1), dt.date(2100, 1, 1)])


class TimeFrame:
    """ Defines the period of the Kimai data."""

    def __init__(self,
                 year=dt.datetime.now().year,
                 period=Period()):
        self.__year = year
        self.__period = period

    def __repr__(self):
        return "TimeFrame(\"" + self.__file + "\", " + str(self.__year) + ")"

    def __str__(self):
        return "TimeLog(\"" + self.__file + "\", " + str(self.__period.start) + \
            ":" + str(self.__period.end) + ")"

    def __setter(self, value):
        logger.warning("Kimai values cannot be changed.")

    def __deleter(self):
        logger.warning("Kimai attributes cannot be deleted.")

    def __get_year(self): return self.__year
    year = property(__get_year, __setter, __deleter)

    def __get_period(self): return self.__period
    period = property(__get_period, __setter, __deleter)


class TimeLog(TimeFrame):
    """Loads and formats Kimai input data and saves it for further analysis."""

    def __init__(self,
                 file="export.csv",
                 dir=".",
                 year=dt.datetime.now().year
                 ):
        # Read data file with exported Kimai times and convert time strins to datetimes
        self.__year = year
        rawdata = self._read_kimai(file, dir)
        self._convert_times(rawdata)
        super().__init__(self.__year, self.__period)

    def __repr__(self):
        return "TimeLog(\"" + self.__file + "\", " + str(self.__year) + ")"

    def __str__(self):
        return "TimeLog(" + str(self.__period.start) + ":" + str(self.__period.end) + ")"

    def _read_kimai(self, file, dir):
        """
        Reads data file with kimai times.

        :param file: string file name
        :param dir: string directory
        :return: pandas dataframe file data
        """

        try:
            self.__file = filepath(file, dir)
        except FileNotFoundError:
            logger.error(
                "Data file with Kimai time log ('{f}') not found.".format(f=filepath(file, dir, always_return=True)))
            exit(44)
        else:
            return pd.read_csv(
                self.__file,
                header=0,
                usecols=["Date", "In", "Out", "h:m", "Time"]
            )

    def _convert_times(self, df):
        """
        Convert times and periods to standard datetime format.

        :param df: dataframe with rawdata from kimai file
        :return: dataframe with postprocessed times and periods
        """

        # Convert time strings in raw data to datetimes
        start = pd.to_datetime(df.Date + str(self.__year) +
                               " " + df.In, dayfirst=True)
        end = pd.to_datetime(df.Date + str(self.__year) + " " + df.Out, dayfirst=True)

        # Extract time period covered in data file
        self.__period = Period(start.iloc[-1].date(), end.iloc[0].date())

        # Correct dates for work periods over midnight
        for i in range(len(end)):
            if start[i] > end[i]:
                end[i] += dt.timedelta(days=1)

        self.__kimai_data = pd.DataFrame({
            'start': start,
            'end': end,
            'duration': end - start,
            'hours': df.Time
        })

    def __setter(self, value):
        logger.warning("Kimai values cannot be changed.")

    def __deleter(self):
        logger.warning("Kimai attributes cannot be deleted.")

    def __get_file(self): return self.__file
    file = property(__get_file, __setter, __deleter)

    def __get_data(self): return self.__kimai_data
    data = property(__get_data, __setter, __deleter)


def filepath(filename, dir='.', always_return=False):
    """Adds dir to filename, if path is not already included in filename.

    Parameters
    ----------
    filename : str
        File name with or without path included.
    dir : str
        Optional directory joined to the file name. Default is cwd.
    always_return : bool, optional
        If set to true, the joined file and directory string is return even for non-existing files.

    Returns
    -------
    str
        Join directory and file name.
    """
    file = filename if ('/' in filename) else path.join(dir, filename)
    if always_return or path.exists(file):
        return file
    else:
        raise FileNotFoundError(
            errno.ENOENT, strerror(errno.ENOENT), file)


if __name__ == "__main__":
    tl = TimeLog()
    print(tl.data)
    print(tl.period)
    print(tl.kimai_file)
    tf = TimeFrame()
    print(tf.year)
    print(tf.period)
