from datetime import date, timedelta

from typing import List, Tuple, Optional

from workday_lister.types import DaysOff, Period
from workday_lister.google import CalendarService
from workday_lister.calendar import get_first_day_of_month, get_last_day_of_month

class WorkdayLister:
    """
    A class for listing workdays within a given month or period.

    Args:
        month (Optional[date]): The month for which to list workdays.
        period (Optional[Period]): The period for which to list workdays.
        vacation_calendar_id (str): The ID of the vacation calendar.
        holiday_calendar_id (List[str]): The IDs of the holiday calendars.

    Raises:
        ValueError: If both month and period are None or if both month and period are provided.

    Attributes:
        period (Period): The period for which to list workdays.
        calendar_service (CalendarService): The calendar service used to retrieve holidays and vacations.

    """

    def __init__(
        self,
        vacation_calendar_id: str,
        month: Optional[date] = None,
        period: Optional[Period] = None,
        holiday_calendar_id: Optional[List[str]] = None,
    ):
        if month is None and period is None:
            raise ValueError("Either month or period must be provided")
        elif month is not None and period is not None:
            raise ValueError("Only one of month or period must be provided")
        elif month is not None:
            self.period = Period(
                get_first_day_of_month(month.year, month.month),
                get_last_day_of_month(month.year, month.month)
            )
        elif period is not None:
            self.period = period
        self.calendar_service = CalendarService(
            vacation_calendar_id,
            holiday_calendar_id,
        )
        self.days_worked, self.days_off = self.retrieve()

    def get_weekdays(self) -> List[date]:
        """
        Get a list of weekdays within the specified period.

        Returns:
            List[date]: A list of weekdays within the specified period.

        """
        weekends = []
        current_date = self.period.start
        while current_date <= self.period.end:
            if current_date.weekday() < 5:  # 5 and 6 correspond to Saturday and Sunday
                weekends.append(current_date)
            current_date += timedelta(days=1)
        return weekends


    def retrieve(
        self,
    ) -> Tuple[List[date], DaysOff]:
        """
        Retrieve the list of worked days, and dict if DaysOff within the specified period.

        Returns:
            Tuple[List[date], DaysOff]: A tuple containing the list of
            worked days and days_off within the specified period.

        """
        week_days = self.get_weekdays()
        days_off = self.calendar_service.get_vacation(self.period)
        worked_days: List[date] = []
        for day in week_days:
            if day not in days_off.keys():
                worked_days.append(day)
        return worked_days, days_off
