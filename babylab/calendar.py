"""
Time utils.
"""

from datetime import datetime
from dateutil import relativedelta


def get_age(birth_date: str | datetime, timestamp: str | datetime = None):
    """Estimate age in months and days at some timestamp based on date of birth.

    Args:
        birth_date (str | datetime): Birthdate as ``datetime`` object or str in "Y-m-d" format. Defaults to current date (``datetime.today()``).
        timestamp (str | datetime, optional): Time for which the age is calculated. Defaults to None.

    Returns:
        list[int]: Age in months and days.
    """  # pylint: disable=line-too-long
    if timestamp is None:
        timestamp = datetime.today()
    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    delta = relativedelta.relativedelta(timestamp, birth_date)
    return [delta.months + (delta.years * 12), delta.days]


def get_birth_date(age: str, timestamp: str | datetime = None):
    """Calculate date of birth based on age at some timestamp.

    Args:
        age (str): Age in months and days (``m:d`` format) at the timestamp.
        timestamp (str | datetime, optional): Time at which age was calculated. Defaults to ``datetime.today()``.

    Returns:
        _type_: _description_
    """  # pylint: disable=line-too-long
    if timestamp is None:
        timestamp = datetime.today()
    if not isinstance(timestamp, datetime):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    age_parsed = age.split(":")
    days_diff = int(float(age_parsed[0]) * 30.437 + float(age_parsed[1]))
    return timestamp - relativedelta.relativedelta(days=days_diff)


def get_age_lambda(row, **kwargs):
    """Lambda function to calculate ages.

    Args:
        row (any): Row in a ``pd.DataFrame`` project.
        **kwargs: Additional arguments passed to ``get_age()``.

    Returns:
        row: Calculated value.
    """
    age = f"{row['age_now_months']}:{row['age_now_days']}"
    birth_date = get_birth_date(age, **kwargs)
    age = get_age(birth_date)
    return int(age[1]), int(age[2])
