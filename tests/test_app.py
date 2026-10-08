from app import create_app


def test_index_shows_rooms(client):
    html = client.get("/").get_data(as_text=True)
    for name in ("Katta zal", "Kichik xona", "Kabinet"):
        assert name in html


def test_booking_appears_in_schedule(client, book, tomorrow):
    r = book("10:00", "11:00", name="Vali")
    assert "Xona band qilindi" in r.get_data(as_text=True)
    html = client.get(f"/?date={tomorrow}").get_data(as_text=True)
    assert "10:00–11:00" in html and "Vali" in html


def test_overlap_rejected(book):
    book("10:00", "11:00")
    r = book("10:30", "11:30", name="Boshqa")
    assert "Bu vaqt band" in r.get_data(as_text=True)


def test_adjacent_allowed(book):
    book("10:00", "11:00")
    r = book("11:00", "12:00")
    assert "Xona band qilindi" in r.get_data(as_text=True)


def test_same_time_other_room_allowed(book):
    book("10:00", "11:00", room_id=1)
    r = book("10:00", "11:00", room_id=2)
    assert "Xona band qilindi" in r.get_data(as_text=True)


def test_form_values_kept_after_error(book):
    r = book("17:00", "19:00", name="Saqlansin")
    html = r.get_data(as_text=True)
    assert "ish vaqtida" in html and 'value="Saqlansin"' in html


def test_cancel_own_booking(client, book, tomorrow):
    book("10:00", "11:00")
    r = client.post("/cancel/1", follow_redirects=True)
    assert "Band bekor qilindi" in r.get_data(as_text=True)
    # Endi shu vaqtni boshqa band qila oladi
    assert "Xona band qilindi" in book("10:00", "11:00").get_data(as_text=True)


def test_cannot_cancel_others_booking(app, book):
    book("10:00", "11:00")
    stranger = app.test_client()  # boshqa brauzer — cookie yo'q
    assert stranger.post("/cancel/1").status_code == 403
    assert "Bekor qilish</button>" not in stranger.get("/").get_data(as_text=True)


def test_data_survives_restart(tmp_path, tomorrow):
    path = str(tmp_path / "persist.db")
    c1 = create_app({"TESTING": True, "DATABASE": path}).test_client()
    c1.post("/book", data={"name": "Doimiy", "room_id": 1, "people": 2, "date": tomorrow,
                           "start_time": "14:00", "end_time": "15:00"})
    # "Server qayta ishga tushdi" — yangi ilova, o'sha baza fayli
    c2 = create_app({"TESTING": True, "DATABASE": path}).test_client()
    assert "Doimiy" in c2.get(f"/?date={tomorrow}").get_data(as_text=True)


def test_bad_date_in_url_falls_back(client):
    assert client.get("/?date=xyz").status_code == 200
