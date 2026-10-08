"""Majlislar xonasini band qilish ilovasi."""
import os
from datetime import date, timedelta

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

import db
from booking import WORK_END, WORK_START, BookingError, create_booking, parse_date, validate

DAY_MINUTES = (WORK_END.hour - WORK_START.hour) * 60


def minutes_from_start(hhmm):
    h, m = map(int, hhmm.split(":"))
    return (h - WORK_START.hour) * 60 + m


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-secret"),
        DATABASE=os.environ.get("DATABASE", os.path.join(app.root_path, "bookings.db")),
        # Qaysi bandlar "o'zimniki" ekanini cookie'da uzoq saqlaymiz
        PERMANENT_SESSION_LIFETIME=timedelta(days=365),
    )
    if test_config:
        app.config.update(test_config)

    db.init_db(app.config["DATABASE"])
    app.teardown_appcontext(db.close_db)

    def load_rooms():
        rows = db.get_db().execute("SELECT * FROM rooms ORDER BY capacity DESC").fetchall()
        return {r["id"]: r for r in rows}

    def my_bookings():
        return set(session.get("my_bookings", []))

    @app.get("/")
    def index():
        try:
            day = parse_date(request.args.get("date") or date.today().isoformat())
        except BookingError:
            day = date.today()

        rooms = load_rooms()
        rows = db.get_db().execute(
            "SELECT * FROM bookings WHERE date = ? ORDER BY start_time",
            (day.isoformat(),),
        ).fetchall()

        schedule = {room_id: [] for room_id in rooms}
        for b in rows:
            start = minutes_from_start(b["start_time"])
            end = minutes_from_start(b["end_time"])
            schedule[b["room_id"]].append({
                **dict(b),
                "left": start / DAY_MINUTES * 100,
                "width": (end - start) / DAY_MINUTES * 100,
            })

        return render_template(
            "index.html",
            day=day,
            prev_day=day - timedelta(days=1),
            next_day=day + timedelta(days=1),
            today=date.today(),
            rooms=rooms,
            schedule=schedule,
            mine=my_bookings(),
            hours=range(WORK_START.hour, WORK_END.hour + 1),
            form=session.pop("form", {}),
        )

    @app.post("/book")
    def book():
        try:
            data = validate(request.form, load_rooms())
            booking_id = create_booking(db.get_db(), data)
        except BookingError as e:
            flash(str(e), "error")
            # Foydalanuvchi kiritganini qayta yozib o'tirmasligi uchun formani saqlab qo'yamiz
            session["form"] = request.form.to_dict()
            return redirect(url_for("index", date=request.form.get("date") or None))

        session.permanent = True
        session["my_bookings"] = sorted(my_bookings() | {booking_id})
        flash("Xona band qilindi.", "success")
        return redirect(url_for("index", date=data["date"]))

    @app.post("/cancel/<int:booking_id>")
    def cancel(booking_id):
        if booking_id not in my_bookings():
            abort(403)
        conn = db.get_db()
        row = conn.execute("SELECT date FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        if row is None:
            abort(404)
        conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        session["my_bookings"] = sorted(my_bookings() - {booking_id})
        flash("Band bekor qilindi.", "success")
        return redirect(url_for("index", date=row["date"]))

    return app


app = create_app()
