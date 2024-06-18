from workday_lister.lister import WorkdayLister
from datetime import date
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


if __name__ == '__main__':
    lister = WorkdayLister(
        calendar_id='ee98820c6f4878ce8dac4b06b8a3de293276b6b8125200b5335092f60f7dce36@group.calendar.google.com',
        month=date.today(),
    )
    days_worked = lister.retrieve()
    print('Workdays: ')
    print(json.dumps(days_worked, cls=DateEncoder, indent=4))
    print('Holidays: ')
    print(json.dumps({str(k): v for k, v in days_worked.items()}, indent=4))
