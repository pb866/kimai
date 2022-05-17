# Import modules
from os import path
from collections import namedtuple
import pandas as pd
import datetime as dt
import holidays
import inspect
from textwrap import dedent

class Kimai:
    def __init__(self,
                 file="export.csv",
                 dir="../data/",
                 year=dt.datetime.now().year,
                 vacation=0):
        # Read data file with exported Kimai times and convert time strins to datetimes
        rawdata = self._read(file, dir)
        data = self._convert_times(rawdata, year, vacation)
        # Count working and off-days
        self.__working_hours()
        self.__compile_hours(data)

    def __repr__(self):
        return "Kimai(\"" + self.__file + "\", " + str(self.__year) + ")"

    def __str__(self):
        return "Kimai(worked: {:.2f}h, balance: {:.2f}h)".format(self.__workedhours, self.__balance)

    def _read(self, file, dir):
        """
        Reads data file with kimai times.

        :param file: string file name
        :param dir: string directory
        :return: pandas dataframe file data
        """

        self.__file = path.join(dir, file)
        return pd.read_csv(
            self.__file,
            header=0,
            usecols=["Date", "In", "Out", "h:m", "Time"]
        )

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
                      
                     Extracted from Kimai file
                     -------------------------
                     - {kf}
                     """.format(sd=str(self.__period.start), ed=self.__period.end,
                     wd=self.__workingdays, we=self.__weekenddays, 
                     hd=self.__holidays, al=self.__vacation, 
                     dt=str(self.__workingtimes), dh=self.__workinghours,
                     wt=self.__workedtimes, wh=self.workedhours, 
                     bt=self.__format_timedelta(self.__timedifference),
                     bh=self.__balance, kf=self.__file)))

    def _convert_times(self, df, year, vacation):
        """
        Convert times and periods to standard datetime format.

        :param df: dataframe with rawdata from kimai file
        :return: dataframe with postprocessed times and periods
        """

        # Convert time strings in raw data to datetimes
        start = pd.to_datetime(df.Date + str(year) + " " + df.In)
        end = pd.to_datetime(df.Date + str(year) + " " + df.Out)

        # Extract time period covered in data file
        Period = namedtuple("Period", ["start", "end"])
        self.__period = Period(start.iloc[-1].date(), end.iloc[0].date())
        self.__year = year
        # Set vacation
        self.__vacation = vacation

        # Correct dates for work periods over midnight
        for i in range(len(end)):
            if start[i] > end[i]: end[i] += dt.timedelta(days=1)

        return pd.DataFrame({
            'start': start,
            'end': end,
            'duration': end - start,
            'hours': df.Time
        })

    def __working_hours(self):
        """
        Counts and stores working and off-days from the period and vacation
        as well as the holidays database.

        Returns
        -------
        None.

        """
        offdays = holidays.Germany(prov='SN', years = [self.__year])
        wdays, wends, hdays = -self.__vacation, 0, 0
        for day in pd.date_range(start=self.period.start, end=self.period.end):
            if day in offdays:
                hdays += 1
            elif day.weekday() >= 5:
                wends += 1
            else:
                wdays += 1
        self.__workingdays = wdays
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
        if td < dt.timedelta(0):
            return '-' + str(-td)
        else:
            # Change this to format positive timedeltas the way you want
            return '+'+str(td)


    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, value):
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
    def vacation(self):
        return self.__vacation

    @vacation.setter
    def vacation(self, value):
        print("Kimai values cannot be changed. Request denied to change {var} to {val}.".format(var=inspect.stack()[0][3], val=value))

    @property
    def workingdays(self):
        return self.__workingdays

    @workingdays.setter
    def workingdays(self, value):
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
    times = Kimai(vacation=1)
    times.stats()
    # times.startdate = dt.date(2022, 4, 18)
