# Import modules
from os import path, strerror
import logging
import errno
from collections import namedtuple
import pandas as pd
import datetime as dt
import holidays
import inspect
from textwrap import dedent


class CustomFormatter(logging.Formatter):

    grey = "\x1b[35;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Kimai:
    def __init__(self,
                 file="export.csv",
                 dir="data/",
                 year=dt.datetime.now().year,
                 vacation="vacation.csv"):
        # Read data file with exported Kimai times and convert time strins to datetimes
        rawdata = self._read_kimai(file, dir)
        data = self._convert_times(rawdata, year, vacation)
        # Count working and off-days
        self.vacation_days(vacation,dir)
        self.__working_hours()
        self.__compile_hours(data)


    def __repr__(self):
        return "Kimai(\"" + self.__file + "\", " + str(self.__year) + ")"


    def __str__(self):
        return "Kimai(worked: {:.2f}h, balance: {:.2f}h)".format(self.__workedhours, self.__balance)


    def stats(self):
        """
        Print summary of working hours account.

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
                     """.format(sd=str(self.__period.start), ed=self.__period.end,
                     wd=self.__workdays, we=self.__weekenddays,
                     hd=self.__holidays, al=self.__vacdays,
                     dt=self.__format_timedelta(self.__workingtimes), dh=self.__workinghours,
                     wt=self.__format_timedelta(self.__workedtimes), wh=self.workedhours,
                     bt=self.__format_timedelta(self.__timedifference),
                     bh=self.__balance, kf=self.__file, vf=self.__vacfile)))


    def work_days(self, start, end, vacation=0, restrict_period=False):
        offdays = holidays.Germany(prov='SN', years = [self.__year])
        wdays, wends, hdays = -vacation, 0, 0
        if restrict_period:
            drange = pd.date_range(start, end).intersection(pd.date_range(self.__period.start, self.__period.end))
        else:
            drange = pd.date_range(start, end)
        for day in drange:
            if day in offdays:
                hdays += 1
            elif day.weekday() >= 5:
                wends += 1
            else:
                wdays += 1
        return wdays, wends, hdays


    def vacation_days(self, vacation, dir='.'):
        if isinstance(vacation, int):
            return self.__vacation_number(vacation)
        try:
            self.__vacfile = self.__filepath(vacation, dir)
        except FileNotFoundError:
            logger.warning("File '{f}' not found. Vacation set to 0.".format(f=vacation))
            return self.__vacation_number(0)
        self.__vacdays = 0
        vacdata = pd.read_csv(self.__vacfile, header=0)
        for index, data in vacdata.iterrows():
            dates = pd.to_datetime(data.date.split('-'), dayfirst=True)
            if len(dates) == 1:
                if dates[0] in pd.date_range(*self.__period):
                    self.__vacdays += 1
            else:
                self.__vacdays += self.work_days(dates[0], dates[1], restrict_period=True)[0]
        return self.__vacdays

    def __vacation_number(self, n):
        self.__vacdays = n
        self.__vacfile = None
        return n


    def _read_kimai(self, file, dir):
        """
        Reads data file with kimai times.

        :param file: string file name
        :param dir: string directory
        :return: pandas dataframe file data
        """

        self.__file = self.__filepath(file, dir)
        return pd.read_csv(
            self.__file,
            header=0,
            usecols=["Date", "In", "Out", "h:m", "Time"]
        )


    def _convert_times(self, df, year, vacation):
        """
        Convert times and periods to standard datetime format.

        :param df: dataframe with rawdata from kimai file
        :return: dataframe with postprocessed times and periods
        """

        # Convert time strings in raw data to datetimes
        start = pd.to_datetime(df.Date + str(year) + " " + df.In, dayfirst=True)
        end = pd.to_datetime(df.Date + str(year) + " " + df.Out, dayfirst=True)

        # Extract time period covered in data file
        Period = namedtuple("Period", ["start", "end"])
        self.__period = Period(start.iloc[-1].date(), end.iloc[0].date())
        self.__year = year

        # Correct dates for work periods over midnight
        for i in range(len(end)):
            if start[i] > end[i]: end[i] += dt.timedelta(days=1)

        return pd.DataFrame({
            'start': start,
            'end': end,
            'duration': end - start,
            'hours': df.Time
        })


    def __set_vacation(self, vacation):
        # Set vacation, if given as integer
        if isinstance(vacation, int):
            self.__vacdays = vacation
            return


    def __filepath(self, filename, dir):
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
        if path.exists(filepath):
            return filepath
        else:
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), filepath)


    def __working_hours(self):
        """
        Counts and stores working and off-days from the period and vacation
        as well as the holidays database.

        Returns
        -------
        None.

        """
        wdays, wends, hdays = self.work_days(self.__period.start, self.__period.end, vacation=self.__vacdays)
        self.__workdays = wdays
        self.__weekenddays = wends
        self.__holidays = hdays
        self.__workinghours = 8*wdays
        self.__workingtimes = dt.timedelta(hours=self.__workinghours)


    def __compile_hours(self, data):
        """
        Counts the hours worked as time and float and calculates the respective balances.

        Parameters
        ----------
        data : pandas dataframe
            Kimai data with corrected time columns.

        Returns
        -------
        None.
        """
        # Define working times
        self.__workedtimes = sum(data.duration, dt.timedelta())
        self.__workedhours = sum(data.hours)
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


    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def vacation_file(self):
        return self.__vacfile

    @vacation_file.setter
    def vacation_file(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, value):
        print("Kimai values cannot be changed. Request denied to change period to Period({}, {}).".format(value.start, value.end))

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def vacationdays(self):
        return self.__vacdays

    @vacationdays.setter
    def vacationdays(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workdays(self):
        return self.__workdays

    @workdays.setter
    def workdays(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def weekenddays(self):
        return self.__weekenddays

    @weekenddays.setter
    def weekenddays(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def holidays(self):
        return self.__holidays

    @holidays.setter
    def holidays(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workinghours(self):
        return self.__workinghours

    @workinghours.setter
    def workinghours(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workingtimes(self):
        return self.__workingtimes

    @workingtimes.setter
    def workingtimes(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workedhours(self):
        return self.__workedhours

    @workedhours.setter
    def workedhours(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workedtimes(self):
        return self.__workedtimes

    @workedtimes.setter
    def workedtimes(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def timedifference(self):
        return self.__timedifference

    @timedifference.setter
    def timedifference(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))


logger = logging.getLogger("Kimai")
# logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


if __name__ == '__main__':
    # times = Kimai(vacation=1)
    # times.stats()
    # times = Kimai(file='data/2022-04.csv', vacation=1)
    # times.stats()
    # times = Kimai(file='data/2022-04.csv', vacation='happiness.csv')
    # times.stats()
    times = Kimai()
    times.stats()
    # times.startdate = dt.date(2022, 4, 18)

    ch.close()
    logger.removeHandler(ch)