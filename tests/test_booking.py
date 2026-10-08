from datetime import date

import pytest

from booking import BookingError, overlaps, validate

ROOMS = {1: {"name": "Katta zal", "capacity": 20}, 3: {"name": "Kabinet", "capacity": 4}}
TODAY = date(2026, 10, 8)


def form(**kw):
    base = {"name": "Ali", "room_id": "1", "people": "3",
            "date": "2026-10-09", "start_time": "10:00", "end_time": "11:00"}
    base.update(kw)
    return base


@pytest.mark.parametrize("a, b, expected", [
    (("10:00", "11:00"), ("10:30", "11:30"), True),   # qisman ustma-ust
    (("10:00", "11:00"), ("11:00", "12:00"), False),  # chegarasi tegib turibdi
    (("10:00", "11:00"), ("09:00", "10:00"), False),
    (("10:00", "12:00"), ("10:30", "11:00"), True),   # ichida
    (("10:30", "11:00"), ("10:00", "12:00"), True),   # o'rab olgan
    (("10:00", "11:00"), ("10:00", "11:00"), True),   # aynan bir xil
])
def test_overlaps(a, b, expected):
    assert overlaps(*a, *b) is expected


def test_valid_form():
    data = validate(form(), ROOMS, today=TODAY)
    assert data["start_time"] == "10:00" and data["room_id"] == 1


@pytest.mark.parametrize("start, end", [
    ("08:30", "09:30"),
    ("17:30", "18:30"),
    ("08:00", "19:00"),
])
def test_outside_working_hours(start, end):
    with pytest.raises(BookingError, match="ish vaqtida"):
        validate(form(start_time=start, end_time=end), ROOMS, today=TODAY)


def test_full_working_day_allowed():
    validate(form(start_time="09:00", end_time="18:00"), ROOMS, today=TODAY)


@pytest.mark.parametrize("start, end", [("11:00", "10:00"), ("10:00", "10:00")])
def test_end_must_be_after_start(start, end):
    with pytest.raises(BookingError, match="Tugash"):
        validate(form(start_time=start, end_time=end), ROOMS, today=TODAY)


def test_capacity_exceeded():
    with pytest.raises(BookingError, match="sig'imi 4"):
        validate(form(room_id="3", people="5"), ROOMS, today=TODAY)


def test_past_date():
    with pytest.raises(BookingError, match="O'tgan"):
        validate(form(date="2026-10-07"), ROOMS, today=TODAY)


@pytest.mark.parametrize("field, value", [
    ("name", "   "), ("room_id", "99"), ("room_id", "abc"),
    ("people", "0"), ("date", "2026-13-01"), ("start_time", "25:00"),
])
def test_bad_input(field, value):
    with pytest.raises(BookingError):
        validate(form(**{field: value}), ROOMS, today=TODAY)
