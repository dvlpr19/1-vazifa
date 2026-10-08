"""Band qilish qoidalari: tekshiruvlar va ustma-ust tushishni aniqlash."""
from datetime import date, datetime, time

WORK_START = time(9, 0)
WORK_END = time(18, 0)


class BookingError(Exception):
    """Foydalanuvchiga ko'rsatiladigan xato."""


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise BookingError("Sana noto'g'ri kiritilgan.")


def parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (TypeError, ValueError):
        raise BookingError("Vaqt noto'g'ri kiritilgan (HH:MM).")


def overlaps(start_a, end_a, start_b, end_b):
    """Ikki oraliq kesishadimi? Chegaralar tegib tursa (11:00 va 11:00) — kesishmaydi."""
    return start_a < end_b and start_b < end_a


def validate(form, rooms, today=None):
    """Formadagi ma'lumotni tekshiradi va tozalangan dict qaytaradi.

    rooms: {room_id: room_row} — sig'imni tekshirish uchun.
    """
    today = today or date.today()

    name = (form.get("name") or "").strip()
    if not name:
        raise BookingError("Ismingizni kiriting.")
    if len(name) > 100:
        raise BookingError("Ism juda uzun.")

    try:
        room_id = int(form.get("room_id", ""))
    except ValueError:
        raise BookingError("Xonani tanlang.")
    room = rooms.get(room_id)
    if room is None:
        raise BookingError("Bunday xona yo'q.")

    try:
        people = int(form.get("people", ""))
    except ValueError:
        raise BookingError("Odamlar sonini kiriting.")
    if people < 1:
        raise BookingError("Odamlar soni kamida 1 bo'lishi kerak.")
    if people > room["capacity"]:
        raise BookingError(
            f"\"{room['name']}\" sig'imi {room['capacity']} kishi, "
            f"siz {people} kishi kiritdingiz."
        )

    day = parse_date(form.get("date"))
    if day < today:
        raise BookingError("O'tgan kunga band qilib bo'lmaydi.")

    start = parse_time(form.get("start_time"))
    end = parse_time(form.get("end_time"))
    if start >= end:
        raise BookingError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak.")
    if start < WORK_START or end > WORK_END:
        raise BookingError("Faqat ish vaqtida (09:00–18:00) band qilish mumkin.")

    return {
        "name": name,
        "room_id": room_id,
        "people": people,
        "date": day.isoformat(),
        # Har doim "HH:MM" ko'rinishida saqlaymiz — shunda satrlarni solishtirish
        # vaqtlarni solishtirish bilan bir xil ishlaydi.
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
    }


def create_booking(db, data):
    """Kesishish yo'qligini tekshirib, bandni saqlaydi. Yangi id qaytaradi.

    BEGIN IMMEDIATE — tekshirish va yozish orasida boshqa so'rov shu xonani
    band qilib qo'ymasligi uchun bazani yozishga qulflaydi.
    """
    db.execute("BEGIN IMMEDIATE")
    try:
        conflict = db.execute(
            """SELECT name, start_time, end_time FROM bookings
               WHERE room_id = ? AND date = ?
                 AND start_time < ? AND ? < end_time""",
            (data["room_id"], data["date"], data["end_time"], data["start_time"]),
        ).fetchone()
        if conflict:
            raise BookingError(
                f"Bu vaqt band: {conflict['start_time']}–{conflict['end_time']} "
                f"({conflict['name']})."
            )
        cur = db.execute(
            """INSERT INTO bookings (room_id, name, people, date, start_time, end_time)
               VALUES (:room_id, :name, :people, :date, :start_time, :end_time)""",
            data,
        )
        db.execute("COMMIT")
        return cur.lastrowid
    except Exception:
        db.execute("ROLLBACK")
        raise
