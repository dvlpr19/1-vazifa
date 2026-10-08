import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def tomorrow():
    return (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture
def book(client, tomorrow):
    """Band qilish uchun yordamchi: kerakli maydonlarni o'zgartirib yuborish mumkin."""
    def _book(start, end, room_id=1, people=2, name="Ali", day=None, c=None):
        return (c or client).post("/book", data={
            "name": name, "room_id": room_id, "people": people,
            "date": day or tomorrow, "start_time": start, "end_time": end,
        }, follow_redirects=True)
    return _book
