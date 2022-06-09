"""
NAME
    kimbal

DESCRIPTION
    Package to analyse Kimai time logs
    ==================================

    The name kimbal derives from Kimai and balance.
    The package reads exported Kimai time log files as well as further meta data
    such as annual and sick leave and analyses the working times. Main purpose is
    to derive the balance of working time against the demand.

PACKAGE CONTENTS
    kimbal
    ├─ main
    ├─ colourlog
    ├─ loader
    └─ workcal

CONTENTS OF MAIN
    class Kimai(TimeLog)
        Store and analyse Kimai TimeLog data within a TimeFrame.
"""

# Import packages and modules
import pandas as pd
import datetime as dt
from textwrap import dedent
from kimbal.loader import TimeLog, Period
from kimbal.workcal import OffDays, work_days
from kimbal.colourlog import logger, ch


class Kimai(TimeLog):
    """
    Store and analyse Kimai TimeLog data within a TimeFrame.

    ...

    Attributes
    ----------
    workdays : int
        Number of work days within the period
    weekenddays : int
        Number of weekend days within the period
    holidays : int
        Number of holidays within the period
    vacation : OffDays
        with fields:
        days : int
            Number of vacation days within the period
        file : string
            Data file from which the data were retrieved
    workinghours : float
        Hours needed (debit) displayed as float
    workingtimes : datetime.timedelta
        Work time needed (debit) displayed as working days (8h) and hours, minutes, and seconds
    workedhours : float
        Work hours performed (credit) displayed as float
    workedtimes : datetime.timedelta
        Work hours performed (credit) displayed as working days (8h) and hours, minutes, and seconds
    balance : float
        Balance of work account (Hours needed (debit) - work hours performed (credit)) in hours as float
    timedifference : datetime.timedelta
        Balance of work account (Hours needed (debit) - work hours performed (credit)) in working days and time

    Attributes inherited from TimeLog
    ---------------------------------
    file : str
        Name of input file with Kimai data including the folder path.
    data : pandas.dataframe
        Kimai data with columns
            - start (datetime.datetime): Start time of work session
            - end (datetime.datetime): End time of work session
            - duration (datetime.timedelta): Duration of work session as timedelta
            - hours (float): Duration in hours of work session as float
    year : int
        Year for which Kimai data is valid
    period : NamedTuple Period
        start end end date of the Kimai data

    Methods
    -------
    stats():
        Prints the work account balance and further statistics.
    """

    def __init__(self,
                 file="export.csv",
                 dir=".",
                 year=dt.datetime.now().year,
                 vacation="vacation.csv"):
        # Read data file with exported Kimai times and convert time strins to datetimes
        super().__init__(file, dir, year)
        # Count working and off-days
        self.__vacation = OffDays(vacation, dir, self.year, self.period)
        self.__working_hours()
        self.__compile_hours()

    def __repr__(self):
        return "Kimai(\"" + self.kimai_file + "\", " + str(self.year) + ")"

    def __str__(self):
        return "Kimai(worked: {:.2f}h, balance: {:.2f}h)".format(self.workedhours, self.balance)

    def stats(self):
        """
        Print summary of working hours account and further statistics.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """

        print(dedent("""
                     Kimai Statistics for {sd} - {ed}
                     ============================================

                     Work and off-days
                     -----------------
                     - Working days: {wd}
                     - Weekend days: {we}
                     - Holidays: {hd}
                     - Annual leave: {al}

                     Balance account
                     ---------------
                     - Working hours (demand): {dt} ({dh:.2f})
                     - Hours worked: {wt} ({wh:.2f})
                     - Balance: {bt} ({bh:.2f})

                     Data files
                     ----------
                     - Kimai data: {kf}
                     - Vacation:   {vf}
                     """.format(sd=str(self.period.start), ed=self.period.end,
                     wd=self.workdays, we=self.weekenddays,
                     hd=self.holidays, al=self.vacation.days,
                     dt=self.__format_timedelta(self.workingtimes), dh=self.workinghours,
                     wt=self.__format_timedelta(self.workedtimes), wh=self.workedhours,
                     bt=self.__format_timedelta(self.timedifference),
                     bh=self.balance, kf=self.kimai_file, vf=self.vacation.file)))

    def __working_hours(self):
        """
        Counts and stores working and off-days from the period and vacation
        as well as the holidays database.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        wdays, wends, hdays = work_days(*self.period, self.year, vacation=self.__vacation.days)
        self.__workdays = wdays
        self.__weekenddays = wends
        self.__holidays = hdays
        self.__workinghours = 8*wdays
        self.__workingtimes = dt.timedelta(hours=self.__workinghours)

    def __compile_hours(self):
        """
        Counts the hours worked as time and float and calculates the respective balances.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # Define working times
        self.__workedtimes = sum(self.data.duration, dt.timedelta())
        self.__workedhours = sum(self.data.hours)
        # Calculate balance
        self.__balance = self.__workedhours - self.__workinghours
        self.__timedifference = self.__workedtimes - self.__workingtimes

    def __format_timedelta(self, td):
        """
        Counts the hours worked as time and float and calculates the respective balances.

        Parameters
        ----------
        td : datetime.timedelta
            A time difference from the datetime module.

        Returns
        -------
        Formatted timedelta string, where timedeltas are displayed as ±|timedelta|.
        1 day counts as 8 hours (1 work day).
        """
        # Define sign of timedelta and remove it from timedelta
        sign = "-" if td < dt.timedelta(0) else "+"
        if td < dt.timedelta(0): td *= -1
        # Add every 8 hours in seconds to days
        adday, seconds = divmod(td.seconds, 8*3600)
        # Transform days int work days (8h periods)
        wdays = 3*td.days + adday
        # Return formatted string
        return sign + str(dt.timedelta(wdays, seconds))

    def __setter(self, value):
        logger.warning("Kimai values cannot be changed.")

    def __deleter(self):
        logger.warning("Kimai attributes cannot be deleted.")

    def __get_workdays(self): return self.__workdays
    workdays = property(__get_workdays, __setter, __deleter,
                        "Number of work days within the period")

    def __get_weekenddays(self): return self.__weekenddays
    weekenddays = property(__get_weekenddays, __setter, __deleter,
                           "Number of weekend days within the period")

    def __get_holidays(self): return self.__holidays
    holidays = property(__get_holidays, __setter, __deleter,
                        "Number of holidays within the period")

    def __get_vacation(self): return self.__vacation
    vacation = property(__get_vacation, __setter, __deleter,
                        "Offdays object with number of vacation days within the period and the data source file")

    def __get_workinghours(self): return self.__workinghours
    workinghours = property(__get_workinghours, __setter, __deleter,
                            "Hours needed (debit) displayed as float")

    def __get_workingtimes(self): return self.__workingtimes
    workingtimes = property(__get_workingtimes, __setter, __deleter,
                            "Work time needed (debit) displayed as working days (8h) and hours, minutes, and seconds")

    def __get_workedhours(self): return self.__workedhours
    workedhours = property(__get_workedhours, __setter, __deleter,
                           "Work hours performed (credit) displayed as float")

    def __get_workedtimes(self): return self.__workedtimes
    workedtimes = property(__get_workedtimes, __setter, __deleter,
                           "Work hours performed (credit) displayed as working days (8h) and hours, minutes, and seconds")

    def __get_balance(self): return self.__balance
    balance = property(__get_balance, __setter, __deleter,
                       "Balance of work account (Hours needed (debit) - work hours performed (credit)) in hours as float")

    def __get_timedifference(self): return self.__timedifference
    timedifference = property(__get_timedifference, __setter, __deleter,
                              "Balance of work account (Hours needed (debit) - work hours performed (credit)) in working days and time")


if __name__ == '__main__':
    times = Kimai()
    times.stats()
    # times.startdate = dt.date(2022, 4, 18)

    ch.close()
    logger.removeHandler(ch)
