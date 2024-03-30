# workday-lister

[![Build Status](https://github.com/codekoriko/workday-lister/workflows/test/badge.svg?branch=master&event=push)](https://github.com/codekoriko/workday-lister/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/codekoriko/workday-lister/branch/master/graph/badge.svg)](https://codecov.io/gh/codekoriko/workday-lister)
[![Python Version](https://img.shields.io/pypi/pyversions/workday-lister.svg)](https://pypi.org/project/workday-lister/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

Get list of week days, then substract the public holiday from google's public calendar, given its [calendar ID](https://gist.github.com/dhoeric/76bd1c15168ee0ee61ad3bf1730dcb65), then substracting days having an event from calendar '[vacation](https://calendar.google.com/calendar/embed?src=ee98820c6f4878ce8dac4b06b8a3de293276b6b8125200b5335092f60f7dce36%40group.calendar.google.com&ctz=Asia%2FHo_Chi_Minh)'


## Features

- Returns a lists of day_worked: List[date]
- Returns a list of days_off parsed from google calendar
- Stores auth token in user's home dir `.workday_lister` (resolved by `os.path.expanduser('~')`)
- 
- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)


## Installation

```bash
poetry add git+ssh://git@github.com:codekoriko/workday-lister.git
```

## Authentication

- create [credentials.json](https://console.cloud.google.com/apis/credentials) with scope: `calendar.readonly`
- place the file ~/.workday_lister
- Upon first execution, ask for auth, follow link printed in terminal

## Usage

### Create a Google Calendar

- create a new calendar type _'vacation'_ (can remove notification)
- copy its Calendar ID: _Settings and sharing_ > _Integrate calendar_ > _Calendar ID_


```python
from workday_lister.lister import WorkdayLister
from datetime import date

lister = WorkdayLister(
    vacation_calendar_id='ee98820c6f4878ce8dac4b06b8a3de293276b6b8125200b5335092f60f7dce36@group.calendar.google.com',
    month=date.today(),
)
days_worked, days_off, = lister.retrieve()

#  
#    days_worked => 
#    [
#        "2024-03-01",
#        "2024-03-04",
#        "2024-03-05",
#        "2024-03-06",
#        "2024-03-07",
#        "2024-03-08",
#        "2024-03-11",
#        "2024-03-12",
#        "2024-03-13",
#        "2024-03-14",
#        "2024-03-15",
#        "2024-03-18",
#        "2024-03-19",
#        "2024-03-22",
#        "2024-03-25",
#        "2024-03-26",
#        "2024-03-27",
#        "2024-03-28",
#        "2024-03-29"
#    ]
#
#    days_off => 
#    {
#        "2024-03-20": "took a day off",
#        "2024-03-21": "took a day another one"
#    }
```

the days_off description are parsed from summary (first big field)

## License

[MIT](https://github.com/codekoriko/workday-lister/blob/master/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [d8fc7db01116b338f542eea6d8ca7bf37a888f1a](https://github.com/wemake-services/wemake-python-package/tree/d8fc7db01116b338f542eea6d8ca7bf37a888f1a). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/d8fc7db01116b338f542eea6d8ca7bf37a888f1a...master) since then.
