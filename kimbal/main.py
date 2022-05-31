# Import packages and modules
import pandas as pd
import datetime as dt
import holidays
import inspect
from textwrap import dedent
from kimbal.dataimport import TimeLog, filepath
from kimbal.colourlog import logger, ch


class Kimai(TimeLog):
    def __init__(self,
                 file="export.csv",
                 dir="data/",
                 year=dt.datetime.now().year,
                 vacation="vacation.csv"):
        # Read data file with exported Kimai times and convert time strins to datetimes
        TimeLog.__init__(self, file, dir, year)
        # Count working and off-days
        self.vacation_days(vacation,dir)
        self.__working_hours()
        self.__compile_hours()


    def __repr__(self):
        return "Kimai(\"" + self.kimai_file + "\", " + str(self.year) + ")"


    def __str__(self):
        return "Kimai(worked: {:.2f}h, balance: {:.2f}h)".format(self.workedhours, self.balance)


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
                     """.format(sd=str(self.period.start), ed=self.period.end,
                     wd=self.workdays, we=self.weekenddays,
                     hd=self.holidays, al=self.vacationdays,
                     dt=self.__format_timedelta(self.workingtimes), dh=self.workinghours,
                     wt=self.__format_timedelta(self.workedtimes), wh=self.workedhours,
                     bt=self.__format_timedelta(self.timedifference),
                     bh=self.balance, kf=self.kimai_file, vf=self.vacfile)))


    def work_days(self, start, end, vacation=0, restrict_period=False):
        offdays = holidays.Germany(prov='SN', years = [self.year])
        wdays, wends, hdays = -vacation, 0, 0
        if restrict_period:
            drange = pd.date_range(start, end).intersection(pd.date_range(self.period.start, self.period.end))
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
            self.vacfile = filepath(vacation, dir)
        except FileNotFoundError:
            logger.warning("File '{f}' not found. Vacation set to 0.".format(
                f=filepath(vacation, dir, always_return=True)))
            return self.__vacation_number(0)
        self.__vacdays = 0
        vacdata = pd.read_csv(self.vacfile, header=0)
        for index, data in vacdata.iterrows():
            dates = pd.to_datetime(data.date.split('-'), dayfirst=True)
            if len(dates) == 1:
                if dates[0] in pd.date_range(*self.period):
                    self.__vacdays += 1
            else:
                self.__vacdays += self.work_days(dates[0], dates[1], restrict_period=True)[0]
        return self.vacation_days


    def __vacation_number(self, n):
        self.vacation_days = n
        self.__vacfile = None
        return n


    def __working_hours(self):
        """
        Counts and stores working and off-days from the period and vacation
        as well as the holidays database.

        Returns
        -------
        None.

        """
        wdays, wends, hdays = self.work_days(self.period.start, self.period.end, vacation=self.__vacdays)
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
        data : pandas dataframe
            Kimai data with corrected time columns.

        Returns
        -------
        None.
        """
        # Define working times
        self.__workedtimes = sum(self.kimai_data.duration, dt.timedelta())
        self.__workedhours = sum(self.kimai_data.hours)
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
    def vacation_file(self):
        return self.__vacfile

    @vacation_file.setter
    def vacation_file(self, value):
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
