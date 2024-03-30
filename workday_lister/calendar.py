from datetime import date
import calendar


def get_first_day_of_month(year: int, month: int) -> date:
    return date(year, month, 1)

def get_last_day_of_month(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])
