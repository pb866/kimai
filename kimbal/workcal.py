"""
Module of kimbal package for work and off days in Kimai logs
============================================================

The module contains classes and methods for counting work, weekend days, and
holidays as well as annual and sick leave.
"""

# Import python packages
import pandas as pd
import datetime as dt
import holidays
from kimbal.loader import TimeFrame, Period, filepath
from kimbal.colourlog import logger


class OffDays(TimeFrame):
    """ Retrieve the number of non-work or off-days within a TimeFrame period."""

    def __init__(self,
                 off="vacation.csv",
                 dir=".",
                 year=dt.datetime.now().year,
                 period=Period()
                 ):
        # Count working and off-days
        super().__init__(year, period)
        self.__vacdays, self.__vacfile = off_days(
            self.year, off, dir, self.period)

    def __repr__(self):
        return "OffDays(\"" + self.__vacfile + "\", " + str(self.year) + ")"

    def __str__(self):
        return "OffDays(" + str(self.period.start) + ":" + str(self.period.end) + ")"

    def __setter(self, value):
        logger.warning("Kimai values cannot be changed.")

    def __deleter(self):
        logger.warning("Kimai attributes cannot be deleted.")

    def __get_days(self): return self.__vacdays
    days = property(__get_days, __setter, __deleter, "Number of off-days within the period")

    def __get_file(self): return self.__vacfile
    file = property(__get_file, __setter, __deleter, "Data source file (including the directory)")


def off_days(year, off, dir='.', restrict=Period()):
    """
    Counts the number of off-days in a period.

    Off-days are either given as integer or read from a data file in csv format.
    The first column of the data file is the date of the off-date or a period in the format
    dd.mm.yyyy - dd.mm.yyyy (with or without spaces around the hyphen).
    The second column is a description or reason for the off-days.

    Parameters
    ----------
    year : int
        The year holding the period. The period must not extend over several years.
    off : int or str
        Either number of off-days or file name of data source file (in- or excluding the directory)
    dir : str, optional (otherwise current directory)
        Optional folder path to source file (absolute or relative)
    restrict : Period, optional
        Named tuple with start and end date of period within the off days are counted;
        dates outside the restrict period from the off source file are ignored.

    Returns
    -------
    offdays : int
        Number of off-days in the period
    file : str or None
        data source file with optional directory or None, if an integer was passed by off.
    """
    # Return integers
    if isinstance(off, int):
        return off, None
    # Or read data from file
    try:
        off_file = filepath(off, dir)
    except FileNotFoundError:
        logger.warning("File '{f}' not found. Off-days set to 0.".format(
            f=filepath(off, dir, always_return=True)))
        return 0, None
    # Count off days in data file
    offdays = 0
    offdata = pd.read_csv(off_file, header=0)
    for index, data in offdata.iterrows():
        dates = pd.to_datetime(data.date.split('-'), dayfirst=True)
        if len(dates) == 1:
            if dates[0] in pd.date_range(*restrict):
                offdays += 1
        else:
            offdays += work_days(*dates, year, restrict=restrict)[0]
    return offdays, off_file


def work_days(start, end, year, vacation=0, restrict=Period()):
    """
    Counts the number of work days, weekend days, and holidays in a period.

    Give statistics on the number of work days and weekends or holidays between the start and end date in a given year.
    The number of vacation days is substracted from the work days and a second period (restrict) can be passed to
    work_days. In this case only the intersect between the period and the range between start and end is considered.

    Parameters
    ----------
    start : datetime.date
        Start of the period in which the work and off days are counted.
    end : datetime.date
        End of the period in which the work and off days are counted.
    year : int
        The year holding the period between start and end. The period must not extend over several years.
    vacation : int
        Number of vacation days substracted from the work days.
    restrict : Period, optional
        Named tuple with start and end date of an optional second period. Only the intersect between the primary and
        secondary period are considered. This is needed to count vacation days from a file that can span a large period
        and restrict it to a period of the Kimai TimeFrame.

    Returns
    -------
    wdays : int
        Number of work days in the period (or intersect of periods)
    wends : int
        Number of weekend days in the period (or intersect of periods)
    hdays : int
        Number of holidays in the period (or intersect of periods) determined by the holidays package for Saxony, Germany.
    """

    offdays = holidays.Germany(prov='SN', years=[year])
    wdays, wends, hdays = -vacation, 0, 0
    drange = pd.date_range(start, end).intersection(
        pd.date_range(restrict.start, restrict.end))
    for day in drange:
        if day in offdays:
            hdays += 1
        elif day.weekday() >= 5:
            wends += 1
        else:
            wdays += 1
    return wdays, wends, hdays


if __name__ == "__main__":
    datadir = "../data"

    vacation = OffDays(dir = datadir)
