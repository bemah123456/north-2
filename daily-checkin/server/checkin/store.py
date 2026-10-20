"""Storage. SQLite for local runs and the demo; `supabase/schema.sql` has the
same tables for Postgres when you move to Supabase."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date
from pathlib import Path

DB_PATH = Path(os.environ.get("CHECKIN_DB", Path(__file__).resolve().parents[1] / "data" / "checkin.db"))
AUDIO_DIR = DB_PATH.parent / "audio"

SCHEMA = """
create table if not exists people (
  id text primary key,
  name text not null,
  birth_date text not null,
  timezone text not null,
  checkin_time text not null,
  place_keywords text not null default '[]',
  family_name text,
  family_phone text,
  senior_push_token text,
  family_push_token text,
  created_date text not null,
  evening_checkin integer not null default 0,
  evening_time text not null default '19:00'
);
create table if not exists checkins (
  id text primary key,
  person_id text not null references people(id) on delete cascade,
  local_date text not null,
  completed_at text not null,
  local_hour real not null,
  result text not null,
  features text,
  family_says_different integer,
  duration_s real,
  ease integer,
  session text not null default 'morning',
  unique (person_id, local_date, session)
);
create table if not exists days_off (
  person_id text not null references people(id) on delete cascade,
  date text not null,
  primary key (person_id, date)
);
create table if not exists alerts (
  person_id text not null references people(id) on delete cascade,
  date text not null,
  kind text not null,
  sent_at text not null,
  delivered integer not null default 0,
  message text,
  was_real integer,
  family_note text,
  primary key (person_id, date, kind)
);
-- The team's own scoring of each answer, to measure how often the app agrees.
create table if not exists hand_scores (
  checkin_id text not null references checkins(id) on delete cascade,
  exercise_id text not null,
  value text not null,
  primary key (checkin_id, exercise_id)
);
"""

PERSON_FIELDS = ["name", "birth_date", "timezone", "checkin_time", "place_keywords",
                 "family_name", "family_phone", "senior_push_token", "family_push_token",
                 "evening_checkin", "evening_time"]


@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma foreign_keys = on")
    try:
        conn.executescript(SCHEMA)
        _migrate(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


# Columns added after the first release; older databases get them here.
_ADDED = {"checkins": ["duration_s real", "ease integer"], "alerts": ["was_real integer", "family_note text"],
          "people": ["evening_checkin integer not null default 0", "evening_time text not null default '19:00'"]}


def _migrate(conn) -> None:
    # The evening check-in lets a day hold two check-ins, which needs a new
    # unique key, and SQLite can only change that by copying the table.
    have = {r[1] for r in conn.execute("pragma table_info(checkins)")}
    if "session" not in have:
        old = [c for c in ("id", "person_id", "local_date", "completed_at", "local_hour", "result", "features",
                           "family_says_different", "duration_s", "ease") if c in have]
        # Legacy mode keeps hand_scores pointing at "checkins", not the old
        # copy, and with foreign keys off dropping the copy deletes nothing.
        conn.commit()
        conn.execute("pragma foreign_keys = off")
        conn.execute("pragma legacy_alter_table = on")
        conn.execute("alter table checkins rename to checkins_old")
        conn.executescript(SCHEMA)
        cols = ", ".join(old)
        conn.execute(f"insert into checkins ({cols}) select {cols} from checkins_old")
        conn.execute("drop table checkins_old")
        conn.commit()
        conn.execute("pragma legacy_alter_table = off")
        conn.execute("pragma foreign_keys = on")
    for table, cols in _ADDED.items():
        have = {r[1] for r in conn.execute(f"pragma table_info({table})")}
        for col in cols:
            if col.split()[0] not in have:
                conn.execute(f"alter table {table} add column {col}")


def _person(row) -> dict | None:
    if row is None:
        return None
    p = dict(row)
    p["place_keywords"] = json.loads(p["place_keywords"])
    p["evening_checkin"] = bool(p.get("evening_checkin"))
    return p


def create_person(data: dict, today: date) -> dict:
    pid = uuid.uuid4().hex[:12]
    with db() as c:
        c.execute(
            "insert into people (id, name, birth_date, timezone, checkin_time, place_keywords,"
            " family_name, family_phone, senior_push_token, family_push_token, created_date,"
            " evening_checkin, evening_time) values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (pid, data["name"], data["birth_date"], data["timezone"], data["checkin_time"],
             json.dumps(data.get("place_keywords", [])), data.get("family_name"),
             data.get("family_phone"), data.get("senior_push_token"),
             data.get("family_push_token"), today.isoformat(),
             int(bool(data.get("evening_checkin"))), data.get("evening_time") or "19:00"),
        )
    return get_person(pid)


def update_person(pid: str, changes: dict) -> dict | None:
    changes = {k: v for k, v in changes.items() if k in PERSON_FIELDS}
    if "place_keywords" in changes:
        changes["place_keywords"] = json.dumps(changes["place_keywords"])
    if changes:
        sets = ", ".join(f"{k} = ?" for k in changes)
        with db() as c:
            c.execute(f"update people set {sets} where id = ?", (*changes.values(), pid))
    return get_person(pid)


def get_person(pid: str) -> dict | None:
    with db() as c:
        return _person(c.execute("select * from people where id = ?", (pid,)).fetchone())


def all_people() -> list[dict]:
    with db() as c:
        return [_person(r) for r in c.execute("select * from people")]


def add_checkin(pid: str, day: date, completed_at: str, local_hour: float,
                result: dict, features: dict | None, family_says_different: bool | None,
                duration_s: float | None = None, session: str = "morning") -> str:
    cid = uuid.uuid4().hex[:12]
    with db() as c:
        c.execute(
            "insert into checkins (id, person_id, local_date, completed_at, local_hour, result, features,"
            " family_says_different, duration_s, session) values (?,?,?,?,?,?,?,?,?,?)",
            (cid, pid, day.isoformat(), completed_at, local_hour, json.dumps(result),
             json.dumps(features) if features else None,
             None if family_says_different is None else int(family_says_different), duration_s, session),
        )
    return cid


def set_ease(cid: str, rating: int) -> None:
    with db() as c:
        c.execute("update checkins set ease = ? where id = ?", (rating, cid))


def set_alert_feedback(pid: str, day: str, kind: str, was_real: bool, note: str | None) -> bool:
    with db() as c:
        cur = c.execute("update alerts set was_real = ?, family_note = ? where person_id = ? and date = ? and kind = ?",
                        (int(was_real), note, pid, day, kind))
        return cur.rowcount > 0


def set_hand_scores(cid: str, values: dict[str, str]) -> None:
    with db() as c:
        for ex_id, v in values.items():
            c.execute("insert or replace into hand_scores values (?,?,?)", (cid, ex_id, v))


def hand_scores() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    with db() as c:
        for cid, ex_id, v in c.execute("select checkin_id, exercise_id, value from hand_scores"):
            out.setdefault(cid, {})[ex_id] = v
    return out


def all_alerts() -> list[dict]:
    with db() as c:
        return [dict(r) for r in c.execute("select * from alerts")]


def audio_path(cid: str, exercise_id: str) -> Path | None:
    folder = AUDIO_DIR / cid
    if not folder.exists():
        return None
    return next(folder.glob(f"{exercise_id}.*"), None)


def update_checkin_result(cid: str, result: dict, family_says_different: bool | None = None) -> None:
    with db() as c:
        c.execute("update checkins set result = ? where id = ?", (json.dumps(result), cid))
        if family_says_different is not None:
            c.execute("update checkins set family_says_different = ? where id = ?", (int(family_says_different), cid))


def checkins(pid: str, session: str | None = "morning") -> list[dict]:
    """Oldest first. The morning check-in is the day's check-in; the evening
    one is extra. session=None returns both."""
    with db() as c:
        if session is None:
            rows = c.execute("select * from checkins where person_id = ? order by local_date, session desc", (pid,))
        else:
            rows = c.execute("select * from checkins where person_id = ? and session = ? order by local_date",
                             (pid, session))
        out = []
        for r in rows:
            d = dict(r)
            d["result"] = json.loads(d["result"])
            d["features"] = json.loads(d["features"]) if d["features"] else None
            out.append(d)
        return out


def get_checkin(cid: str) -> dict | None:
    with db() as c:
        r = c.execute("select * from checkins where id = ?", (cid,)).fetchone()
    if r is None:
        return None
    d = dict(r)
    d["result"] = json.loads(d["result"])
    d["features"] = json.loads(d["features"]) if d["features"] else None
    return d


def set_day_off(pid: str, day: date, off: bool) -> None:
    with db() as c:
        if off:
            c.execute("insert or ignore into days_off values (?, ?)", (pid, day.isoformat()))
        else:
            c.execute("delete from days_off where person_id = ? and date = ?", (pid, day.isoformat()))


def days_off(pid: str) -> set[date]:
    with db() as c:
        return {date.fromisoformat(r[0]) for r in c.execute("select date from days_off where person_id = ?", (pid,))}


def sent_alerts(pid: str) -> set[tuple[str, str]]:
    with db() as c:
        return {(r[0], r[1]) for r in c.execute("select date, kind from alerts where person_id = ?", (pid,))}


def record_alert(pid: str, day: str, kind: str, sent_at: str, delivered: bool, message: str) -> None:
    with db() as c:
        c.execute("insert or ignore into alerts (person_id, date, kind, sent_at, delivered, message)"
                  " values (?,?,?,?,?,?)", (pid, day, kind, sent_at, int(delivered), message))


def alerts(pid: str) -> list[dict]:
    with db() as c:
        return [dict(r) for r in c.execute(
            "select * from alerts where person_id = ? order by sent_at desc", (pid,))]


def save_audio(cid: str, exercise_id: str, data: bytes, ext: str) -> None:
    folder = AUDIO_DIR / cid
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{exercise_id}.{ext}").write_bytes(data)


def delete_recordings(pid: str) -> int:
    n = 0
    for c in checkins(pid, None):
        folder = AUDIO_DIR / c["id"]
        if folder.exists():
            for f in folder.iterdir():
                f.unlink()
                n += 1
            folder.rmdir()
    return n
