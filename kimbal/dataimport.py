from os import path, strerror
import errno
from collections import namedtuple
import pandas as pd
import datetime as dt
from kimbal.colourlog import logger

class TimeLog:
    def __init__(self,
                 file="export.csv",
                 dir="data/",
                 year=dt.datetime.now().year,
                #  vacation="vacation.csv"
    ):
        # Read data file with exported Kimai times and convert time strins to datetimes
        rawdata = self._read_kimai(file, dir)
        self._convert_times(rawdata, year)

    def __repr__(self):
        return "TimeLog(\"" + self.__kimai_file + "\", " + str(self.__year) + ")"

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
            self.__kimai_file = filepath(file, dir)
        except FileNotFoundError:
            logger.error("Data file with Kimai time log ('{f}') not found.".format(f=filepath(file, dir, always_return=True)))
        return pd.read_csv(
            self.__kimai_file,
            header=0,
            usecols=["Date", "In", "Out", "h:m", "Time"]
        )


    def _convert_times(self, df, year):
        """
        Convert times and periods to standard datetime format.

        :param df: dataframe with rawdata from kimai file
        :return: dataframe with postprocessed times and periods
        """

        # Convert time strings in raw data to datetimes
        start = pd.to_datetime(df.Date + str(year) +
                               " " + df.In, dayfirst=True)
        end = pd.to_datetime(df.Date + str(year) + " " + df.Out, dayfirst=True)

        # Extract time period covered in data file
        Period = namedtuple("Period", ["start", "end"])
        self.__period = Period(start.iloc[-1].date(), end.iloc[0].date())
        self.__year = year

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

    @property
    def kimai_data(self):
        return self.__kimai_data

    @kimai_data.setter
    def kimai_data(self, value):
        print("Kimai data can not be manipulated after loading from input file.")

    @property
    def kimai_file(self):
        return self.__kimai_file

    @kimai_file.setter
    def kimai_file(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(
            var=inspect.stack()[0][3], val=value))

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, value):
        print("Kimai values cannot be changed. Request denied to change period to Period({}, {}).".format(
            value.start, value.end))

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(
            var=inspect.stack()[0][3], val=value))


def filepath(filename, dir, always_return=False):
    """
    Adds dir to filename, if path is not already included in filename.

    Parameters
    ----------
    filename : string
        File name with or without path included.
    dir : string
        Optional directory joined to the file name.

    Returns
    -------
    string Join directory and file name.
    """
    filepath = filename if ('/' in filename) else path.join(dir, filename)
    if always_return or path.exists(filepath):
        return filepath
    else:
        raise FileNotFoundError(
            errno.ENOENT, strerror(errno.ENOENT), filepath)
