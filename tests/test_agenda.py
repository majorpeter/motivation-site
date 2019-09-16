from datetime import datetime

from agenda import classify_datetime, DateClass


def test_datetime_classify():
    today = datetime(year=2012, month=12, day=3)
    tomorrow = datetime(year=2012, month=12, day=4)
    sunday = datetime(year=2012, month=12, day=9)
    next_monday = datetime(year=2012, month=12, day=10)
    next_sunday = datetime(year=2012, month=12, day=16)
    last_day_of_month = datetime(year=2012, month=12, day=31)
    first_day_of_next_month = datetime(year=2013, month=1, day=1)
    last_day_of_next_month = datetime(year=2013, month=1, day=31)
    later_date = datetime(year=2013, month=2, day=10)

    assert classify_datetime(today, today) == DateClass.TODAY
    assert classify_datetime(tomorrow, today) == DateClass.TOMORROW
    assert classify_datetime(sunday, today) == DateClass.THIS_WEEK
    assert classify_datetime(next_monday, today) == DateClass.NEXT_WEEK
    assert classify_datetime(next_sunday, today) == DateClass.NEXT_WEEK
    assert classify_datetime(last_day_of_month, today) == DateClass.THIS_MONTH
    assert classify_datetime(first_day_of_next_month, today) == DateClass.NEXT_MONTH
    assert classify_datetime(last_day_of_next_month, today) == DateClass.NEXT_MONTH
    assert classify_datetime(later_date, today) == DateClass.LATER

    assert classify_datetime(datetime(2013, 2, 1), datetime(2013, 1, 10)) == DateClass.NEXT_MONTH
    assert classify_datetime(datetime(2013, 12, 1), datetime(2013, 11, 10)) == DateClass.NEXT_MONTH
