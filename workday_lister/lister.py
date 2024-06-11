from datetime import date, timedelta
from typing import List, Optional, Tuple

from workday_lister.calendar import (
    get_first_day_of_month,
    get_last_day_of_month,
)
from workday_lister.google import CalendarService
from workday_lister.types import Period, MarkedDays


class WorkdayLister:
    """
    A class for listing workdays within a given month or period.

    Args:
        month (Optional[date]): The month for which to list workdays. period
        (Optional[Period]): The period for which to list workdays.
        calendar_id (str): The ID of the calendar listing the worked days.

    Raises:
        ValueError: If both month and period are None or if both month and
        period are provided.

    Attributes:
        period (Period): The period for which to list workdays.
        calendar_service (CalendarService): The calendar service used to
        retrieve holidays and vacations.

    """

    def __init__(
        self,
        calendar_id: str,
        month: Optional[date] = None,
        period: Optional[Period] = None,
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
        self.calendar_service = CalendarService(calendar_id)
        self.days_worked = self.retrieve()

    def get_weekdays(self, period: Optional[Period] = None) -> List[date]:
        """
        Get a list of weekdays within the specified period.

        Returns:
            List[date]: A list of weekdays within the specified period.

        """
        weekends = []
        if period is None:
            period = self.period
        current_date = period.start
        while current_date <= period.end:
            if current_date.weekday() < 5:  # 5 and 6 correspond to Saturday and Sunday
                weekends.append(current_date)
            current_date += timedelta(days=1)
        return weekends

    def retrieve(
        self,
    ) -> MarkedDays:
        """
        Retrieve the list of worked days, and dict if MarkedDay within the
        specified period.

        Returns:
            List[date]: the list of worked days striped from the desc str.

        """
        return self.calendar_service.get_days(self.period)

    def update(self):
        """
        Update the list of worked days and days off.

        """
        self.days_worked = self.retrieve()
