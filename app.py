"""Music Ability Assessment site (Flask + SQLite).

Run:  python app.py            (dev)     |   gunicorn -w 1 --threads 8 app:app   (prod)
"""
import io
import csv
import json
import os
import re
import random
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from functools import wraps

from flask import (Flask, g, request, session, redirect, url_for, render_template, abort,
                   flash, jsonify, Response, send_file)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(APP_DIR, "instance"))
AUDIO_DIR = os.path.join(DATA_DIR, "audio_private")      # never served statically
DB_PATH = os.path.join(DATA_DIR, "assessment.db")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=200 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",   # set to 1 behind HTTPS
    PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
)


def _secret():
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    p = os.path.join(DATA_DIR, "secret.key")
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write(secrets.token_hex(32))
        os.chmod(p, 0o600)
    return open(p).read().strip()


app.secret_key = _secret()
signer = URLSafeTimedSerializer(app.secret_key, salt="audio-stream")
STREAM_MAX_AGE = 60 * 30
AUDIO_EXT = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".ogg": "audio/ogg", ".flac": "audio/flac"}

# ----------------------------------------------------------------------------
# DB
# ----------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  pw TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', set_no INTEGER,
  created TEXT, started TEXT, submitted TEXT);
CREATE TABLE IF NOT EXISTS blocks(block INTEGER PRIMARY KEY, perm TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS audio(
  id INTEGER PRIMARY KEY, stored TEXT NOT NULL, original TEXT, mime TEXT, size INTEGER, uploaded TEXT);
CREATE TABLE IF NOT EXISTS questions(
  id INTEGER PRIMARY KEY, set_no INTEGER NOT NULL, qid TEXT NOT NULL, ord INTEGER, section TEXT,
  qtype TEXT, prompt TEXT, note TEXT, options TEXT, cfg TEXT, key TEXT,
  points REAL DEFAULT 1, unit REAL DEFAULT 0, audio_id INTEGER REFERENCES audio(id) ON DELETE SET NULL,
  max_plays INTEGER, UNIQUE(set_no, qid));
CREATE TABLE IF NOT EXISTS responses(
  user_id INTEGER, question_id INTEGER, answer TEXT, manual_score REAL, updated TEXT,
  PRIMARY KEY(user_id, question_id));
CREATE TABLE IF NOT EXISTS plays(id INTEGER PRIMARY KEY, user_id INTEGER, question_id INTEGER, at TEXT);
CREATE TABLE IF NOT EXISTS audio_log(id INTEGER PRIMARY KEY, user_id INTEGER, question_id INTEGER, at TEXT,
  ip TEXT, ua TEXT, range TEXT, status INTEGER);
"""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(_):
    c = g.pop("db", None)
    if c:
        c.close()


def get_setting(k, default=None):
    r = db().execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    return r["v"] if r else default


def set_setting(k, v):
    db().execute("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, str(v)))


def init_db():
    c = sqlite3.connect(DB_PATH, isolation_level=None)
    c.executescript(SCHEMA)
    if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        from seed_data import build_all
        c.execute("BEGIN")
        for q in build_all():
            c.execute("INSERT INTO questions(set_no,qid,ord,section,qtype,prompt,note,options,cfg,points,unit) "
                      "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                      (q["set_no"], q["qid"], q["ord"], q["section"], q["qtype"], q["prompt"], q["note"],
                       json.dumps(q["options"], ensure_ascii=False), json.dumps(q["cfg"], ensure_ascii=False),
                       q["points"], q["unit"]))
        c.execute("COMMIT")
    for k, v in (("default_max_plays", "3"), ("assign_counter", "0"), ("show_score", "0")):
        c.execute("INSERT OR IGNORE INTO settings(k,v) VALUES(?,?)", (k, v))
    # bootstrap admin
    if c.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0] == 0:
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        pw = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(12)
        c.execute("INSERT INTO users(name,email,pw,role,created) VALUES(?,?,?,?,?)",
                  ("Administrator", email, generate_password_hash(pw), "admin", now()))
        if not os.environ.get("ADMIN_PASSWORD"):
            print("\n*** First run: admin account created ***\n    email: %s\n    password: %s\n"
                  "    (set ADMIN_EMAIL / ADMIN_PASSWORD env vars before first run to choose your own)\n" % (email, pw))
    c.close()


# ----------------------------------------------------------------------------
# Auth, CSRF, headers
# ----------------------------------------------------------------------------
def current_user():
    if "user" not in g:
        g.user = None
        uid = session.get("uid")
        if uid:
            g.user = db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            if g.user is None:
                session.clear()
    return g.user


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return f(*a, **k)
    return w


def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        u = current_user()
        if not u:
            return redirect(url_for("login", next=request.path))
        if u["role"] != "admin":
            abort(403)
        return f(*a, **k)
    return w


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token
app.jinja_env.globals["current_user"] = lambda: current_user()


@app.before_request
def csrf_protect():
    if request.method == "POST":
        t = request.form.get("csrf") or request.headers.get("X-CSRF")
        if not t or not secrets.compare_digest(t, session.get("csrf", "")):
            abort(400, "Bad CSRF token")


@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    resp.headers.setdefault("Content-Security-Policy",
                            "default-src 'self'; media-src 'self'; img-src 'self' data:; "
                            "style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'")
    if request.endpoint not in ("static",):
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


_fails = {}


def throttled(key):
    t = time.time()
    lst = [x for x in _fails.get(key, []) if t - x < 600]
    _fails[key] = lst
    return len(lst) >= 8


# ----------------------------------------------------------------------------
# Set assignment: every consecutive group of 10 sign-ups gets a random permutation of sets 1..10
# ----------------------------------------------------------------------------
def assign_set(c):
    """Call inside BEGIN IMMEDIATE. Returns the set number for the next user."""
    n = int(c.execute("SELECT v FROM settings WHERE k='assign_counter'").fetchone()[0])
    block, pos = divmod(n, 10)
    r = c.execute("SELECT perm FROM blocks WHERE block=?", (block,)).fetchone()
    if r:
        perm = json.loads(r[0])
    else:
        perm = list(range(1, 11))
        random.SystemRandom().shuffle(perm)
        c.execute("INSERT INTO blocks(block,perm) VALUES(?,?)", (block, json.dumps(perm)))
    c.execute("UPDATE settings SET v=? WHERE k='assign_counter'", (str(n + 1),))
    return perm[pos]


# ----------------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------------
def _norm(s, cs=False):
    s = re.sub(r"\s+", "", str(s if s is not None else ""))
    return s if cs else s.lower()


def _secs(x):
    try:
        if isinstance(x, (list, tuple)):
            return int(float(x[0] or 0)) * 60 + int(float(x[1] or 0))
        s = str(x).strip()
        if ":" in s:
            m, sec = s.split(":", 1)
            return int(m) * 60 + int(sec)
        return float(s)
    except Exception:
        return None


def jl(s, default=None):
    try:
        return json.loads(s) if s else default
    except Exception:
        return default


def q_max(q):
    t, key, cfg = q["qtype"], jl(q["key"]), jl(q["cfg"], {})
    if t == "multi" and cfg.get("mode") == "per_correct":
        return q["unit"] * len(key or [])
    if t == "table":
        return q["unit"] * len(key or [])
    if t == "chords":
        return q["unit"] * len(key or [])
    if t == "fields" and cfg.get("mode") == "each":
        return q["unit"] * len(cfg.get("fields", []))
    return q["points"]


def score_q(q, a):
    """Auto score, or None if no answer key set."""
    key = jl(q["key"])
    if key in (None, "", []):
        return None
    t, cfg = q["qtype"], jl(q["cfg"], {})
    if a is None:
        return 0.0
    try:
        if t == "single":
            return q["points"] if a == key else 0.0
        if t == "multi":
            sel, k = set(a), set(key)
            if cfg.get("mode") == "per_correct":
                return 0.0 if sel - k else q["unit"] * len(sel & k)
            return q["points"] if sel == k else 0.0
        if t == "fields":
            flds = cfg["fields"]
            ok = [_norm(a[i], f.get("cs")) == _norm(key[i], f.get("cs")) for i, f in enumerate(flds)]
            return q["unit"] * sum(ok) if cfg.get("mode") == "each" else (q["points"] if all(ok) else 0.0)
        if t in ("time_mmss", "time_sec"):
            x, y = _secs(a), _secs(key)
            return q["points"] if x is not None and y is not None and abs(x - y) <= cfg.get("tol", 2) else 0.0
        if t == "table":
            tol, used, s = cfg.get("tol", 2), set(), 0.0
            rows = [r for r in a if r and r[2]]
            for kr in key:
                for i, r in enumerate(rows):
                    if i in used:
                        continue
                    x = _secs([r[0], r[1]])
                    if x is not None and _norm(r[2]) == _norm(kr["n"]) and abs(x - _secs(kr["t"])) <= tol:
                        used.add(i)
                        s += q["unit"]
                        break
            return s
        if t == "chords":
            got = a.get("c", [])
            return q["unit"] * sum(1 for i, kc in enumerate(key)
                                   if i < len(got) and [_norm(x) for x in got[i]] == [_norm(x) for x in kc])
    except Exception:
        return 0.0
    return 0.0


def fmt_answer(q, a):
    if a in (None, "", []):
        return "—"
    t = q["qtype"]
    try:
        if t == "multi":
            return ", ".join(a)
        if t == "fields":
            return " | ".join(str(x) for x in a)
        if t == "time_mmss":
            return "%s:%02d" % (a[0] or 0, int(a[1] or 0))
        if t == "table":
            return "; ".join("%s:%02d %s" % (r[0] or 0, int(r[1] or 0), r[2]) for r in a if r and r[2]) or "—"
        if t == "chords":
            return " – ".join(" ".join(c) for c in a.get("c", [])) + ((" / " + a["r"]) if a.get("r") else "")
    except Exception:
        pass
    return str(a)


def fmt_key(q):
    k = jl(q["key"])
    if k in (None, "", []):
        return "—"
    t = q["qtype"]
    if t == "table":
        return "; ".join("%s %s" % (r["t"], r["n"]) for r in k)
    if t == "chords":
        return " – ".join(" ".join(c) for c in k)
    return fmt_answer(q, k) if t != "time_mmss" else str(k)


app.jinja_env.globals.update(fmt_answer=fmt_answer, fmt_key=fmt_key, jl=jl, q_max=q_max)


def user_results(uid, set_no):
    c = db()
    qs = c.execute("SELECT * FROM questions WHERE set_no=? ORDER BY ord", (set_no,)).fetchall()
    resp = {r["question_id"]: r for r in c.execute("SELECT * FROM responses WHERE user_id=?", (uid,))}
    rows, total, mx, unscored = [], 0.0, 0.0, 0
    for q in qs:
        r = resp.get(q["id"])
        a = jl(r["answer"]) if r else None
        auto = score_q(q, a)
        man = r["manual_score"] if r else None
        eff = man if man is not None else auto
        if eff is None:
            unscored += 1
        else:
            total += eff
        mx += q_max(q) if q["key"] else 0
        rows.append(dict(q=q, answer=a, auto=auto, manual=man, eff=eff, max=q_max(q)))
    return rows, total, mx, unscored


# ----------------------------------------------------------------------------
# Public pages / auth
# ----------------------------------------------------------------------------
@app.route("/")
def landing():
    u = current_user()
    if u:
        return redirect(url_for("admin_home") if u["role"] == "admin" else url_for("test"))
    return render_template("landing.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter your name and a valid email address.", "err")
        elif len(pw) < 8:
            flash("Password must be at least 8 characters.", "err")
        elif pw != request.form.get("password2"):
            flash("Passwords do not match.", "err")
        else:
            c = db()
            c.execute("BEGIN IMMEDIATE")
            try:
                if c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                    c.execute("ROLLBACK")
                    flash("An account with this email already exists. Please log in.", "err")
                    return render_template("signup.html")
                s = assign_set(c)
                cur = c.execute("INSERT INTO users(name,email,pw,role,set_no,created) VALUES(?,?,?,?,?,?)",
                                (name, email, generate_password_hash(pw), "user", s, now()))
                uid = cur.lastrowid
                c.execute("COMMIT")
            except Exception:
                c.execute("ROLLBACK")
                raise
            session.clear()
            session["uid"] = uid
            session.permanent = True
            return redirect(url_for("test"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        key = request.remote_addr + "|" + email
        if throttled(key):
            flash("Too many failed attempts. Please wait a few minutes.", "err")
            return render_template("login.html")
        u = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u and check_password_hash(u["pw"], request.form.get("password", "")):
            session.clear()
            session["uid"] = u["id"]
            session.permanent = True
            nxt = request.args.get("next", "")
            if nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("landing"))
        _fails.setdefault(key, []).append(time.time())
        flash("Incorrect email or password.", "err")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ----------------------------------------------------------------------------
# Test taking (users)
# ----------------------------------------------------------------------------
def plays_left(uid, q):
    mp = q["max_plays"] if q["max_plays"] is not None else int(get_setting("default_max_plays", "3"))
    used = db().execute("SELECT COUNT(*) FROM plays WHERE user_id=? AND question_id=?", (uid, q["id"])).fetchone()[0]
    return max(0, mp - used)


@app.route("/test")
@login_required
def test():
    u = current_user()
    if u["role"] == "admin":
        return redirect(url_for("admin_home"))
    if u["submitted"]:
        return redirect(url_for("done"))
    c = db()
    if not u["started"]:
        c.execute("UPDATE users SET started=? WHERE id=?", (now(), u["id"]))
    # ONLY the user's own assigned set is ever queried
    qs = c.execute("SELECT * FROM questions WHERE set_no=? ORDER BY ord", (u["set_no"],)).fetchall()
    saved = {r["question_id"]: jl(r["answer"]) for r in c.execute("SELECT * FROM responses WHERE user_id=?", (u["id"],))}
    items = [dict(q=q, left=plays_left(u["id"], q) if q["audio_id"] else None) for q in qs]
    return render_template("test.html", items=items, saved=saved, user=u)


@app.route("/api/answer", methods=["POST"])
@login_required
def api_answer():
    u = current_user()
    d = request.get_json(silent=True) or {}
    q = db().execute("SELECT * FROM questions WHERE id=?", (d.get("q"),)).fetchone()
    if u["role"] != "user" or u["submitted"] or not q or q["set_no"] != u["set_no"]:
        abort(403)
    ans = json.dumps(d.get("a"), ensure_ascii=False)
    if len(ans) > 20000:
        abort(400)
    db().execute("INSERT INTO responses(user_id,question_id,answer,updated) VALUES(?,?,?,?) "
                 "ON CONFLICT(user_id,question_id) DO UPDATE SET answer=excluded.answer, updated=excluded.updated",
                 (u["id"], q["id"], ans, now()))
    return jsonify(ok=True)


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    u = current_user()
    if u["role"] == "user" and not u["submitted"]:
        db().execute("UPDATE users SET submitted=? WHERE id=?", (now(), u["id"]))
    return redirect(url_for("done"))


@app.route("/done")
@login_required
def done():
    u = current_user()
    if u["role"] != "user":
        return redirect(url_for("admin_home"))
    if not u["submitted"]:
        return redirect(url_for("test"))
    res = None
    if get_setting("show_score", "0") == "1":
        _, total, mx, unscored = user_results(u["id"], u["set_no"])
        if not unscored:
            res = (total, mx)
    return render_template("done.html", user=u, res=res)


# ----------------------------------------------------------------------------
# Protected audio streaming
# ----------------------------------------------------------------------------
@app.route("/api/audio/<int:qid>/play", methods=["POST"])
@login_required
def audio_play(qid):
    u = current_user()
    q = db().execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
    if not q or not q["audio_id"]:
        abort(404)
    admin = u["role"] == "admin"
    if not admin and (q["set_no"] != u["set_no"] or u["submitted"]):
        abort(403)
    if not admin:
        if plays_left(u["id"], q) <= 0:
            return jsonify(error="No plays left for this question."), 403
        db().execute("INSERT INTO plays(user_id,question_id,at) VALUES(?,?,?)", (u["id"], qid, now()))
    if "nonce" not in session:
        session["nonce"] = secrets.token_hex(8)
    tok = signer.dumps({"u": u["id"], "a": q["audio_id"], "q": qid, "n": session["nonce"],
                        "ua": (request.user_agent.string or "")[:200]})
    return jsonify(url=url_for("stream", token=tok), left=None if admin else plays_left(u["id"], q))


@app.route("/s/<token>")
def stream(token):
    u = current_user()
    if not u:
        abort(401)
    try:
        d = signer.loads(token, max_age=STREAM_MAX_AGE)
    except (BadSignature, SignatureExpired):
        abort(403)
    if d["u"] != u["id"] or d["n"] != session.get("nonce") or d["ua"] != (request.user_agent.string or "")[:200]:
        abort(403)
    # Must be requested by an <audio> element on our own pages, not by address bar / download managers
    dest = request.headers.get("Sec-Fetch-Dest")
    if dest is not None and dest not in ("audio", "video"):
        abort(403)
    ref = request.headers.get("Referer")
    if ref and not ref.startswith(request.host_url):
        abort(403)
    a = db().execute("SELECT * FROM audio WHERE id=?", (d["a"],)).fetchone()
    if not a:
        abort(404)
    path = os.path.join(AUDIO_DIR, a["stored"])
    resp = send_file(path, mimetype=a["mime"], conditional=True, etag=False, last_modified=None, max_age=0)
    resp.headers["Content-Disposition"] = "inline"                      # no filename -> nothing to "save as"
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["X-Robots-Tag"] = "noindex"
    try:
        db().execute("INSERT INTO audio_log(user_id,question_id,at,ip,ua,range,status) VALUES(?,?,?,?,?,?,?)",
                     (u["id"], d["q"], now(), request.remote_addr, (request.user_agent.string or "")[:200],
                      request.headers.get("Range", ""), resp.status_code))
    except Exception:
        pass
    return resp


# ----------------------------------------------------------------------------
# Admin
# ----------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_home():
    c = db()
    dist = {r["set_no"]: r["n"] for r in c.execute("SELECT set_no, COUNT(*) n FROM users WHERE role='user' GROUP BY set_no")}
    cover = {r["set_no"]: (r["a"], r["t"]) for r in c.execute(
        "SELECT set_no, SUM(audio_id IS NOT NULL) a, COUNT(*) t FROM questions GROUP BY set_no")}
    stats = dict(
        users=c.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0],
        submitted=c.execute("SELECT COUNT(*) FROM users WHERE submitted IS NOT NULL").fetchone()[0],
        audio=c.execute("SELECT COUNT(*) FROM audio").fetchone()[0])
    return render_template("admin_home.html", dist=dist, cover=cover, stats=stats)


@app.route("/admin/users")
@admin_required
def admin_users():
    rows = db().execute("SELECT * FROM users ORDER BY role, id").fetchall()
    return render_template("admin_users.html", rows=rows)


@app.route("/admin/users/<int:uid>", methods=["GET", "POST"])
@admin_required
def admin_user(uid):
    c = db()
    u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not u:
        abort(404)
    if request.method == "POST":
        act = request.form.get("action")
        if act == "scores" and u["set_no"]:
            for q in c.execute("SELECT id FROM questions WHERE set_no=?", (u["set_no"],)):
                v = request.form.get("m%d" % q["id"], "").strip()
                if v == "":
                    c.execute("UPDATE responses SET manual_score=NULL WHERE user_id=? AND question_id=?", (uid, q["id"]))
                else:
                    try:
                        c.execute("INSERT INTO responses(user_id,question_id,manual_score,updated) VALUES(?,?,?,?) "
                                  "ON CONFLICT(user_id,question_id) DO UPDATE SET manual_score=excluded.manual_score",
                                  (uid, q["id"], float(v), now()))
                    except ValueError:
                        pass
            flash("Scores saved.", "ok")
        elif act == "reopen":
            c.execute("UPDATE users SET submitted=NULL WHERE id=?", (uid,))
            flash("Attempt re-opened — the user can continue and re-submit (same set).", "ok")
        elif act == "delete" and u["role"] == "user":
            c.execute("DELETE FROM responses WHERE user_id=?", (uid,))
            c.execute("DELETE FROM plays WHERE user_id=?", (uid,))
            c.execute("DELETE FROM users WHERE id=?", (uid,))
            flash("User deleted. (Their set slot is not reused, so the 10-set rotation stays balanced.)", "ok")
            return redirect(url_for("admin_users"))
        elif act == "password":
            pw = request.form.get("password", "")
            if len(pw) >= 8:
                c.execute("UPDATE users SET pw=? WHERE id=?", (generate_password_hash(pw), uid))
                flash("Password reset.", "ok")
            else:
                flash("Password must be at least 8 characters.", "err")
        return redirect(url_for("admin_user", uid=uid))
    rows = total = mx = unscored = None
    if u["set_no"]:
        rows, total, mx, unscored = user_results(uid, u["set_no"])
    return render_template("admin_user.html", u=u, rows=rows, total=total, mx=mx, unscored=unscored)


@app.route("/admin/sets")
@admin_required
def admin_sets():
    cover = db().execute("SELECT set_no, SUM(audio_id IS NOT NULL) a, SUM(key IS NOT NULL) k, COUNT(*) t "
                         "FROM questions GROUP BY set_no ORDER BY set_no").fetchall()
    return render_template("admin_sets.html", cover=cover)


@app.route("/admin/sets/<int:n>", methods=["GET", "POST"])
@admin_required
def admin_set(n):
    c = db()
    if request.method == "POST":
        for q in c.execute("SELECT id, audio_id FROM questions WHERE set_no=?", (n,)).fetchall():
            v = request.form.get("a%d" % q["id"], "")
            new = int(v) if v.isdigit() else None
            if new != q["audio_id"]:
                c.execute("UPDATE questions SET audio_id=? WHERE id=?", (new, q["id"]))
        flash("Song assignments saved for Set %d." % n, "ok")
        return redirect(url_for("admin_set", n=n))
    qs = c.execute("SELECT * FROM questions WHERE set_no=? ORDER BY ord", (n,)).fetchall()
    lib = c.execute("SELECT * FROM audio ORDER BY original").fetchall()
    return render_template("admin_set.html", n=n, qs=qs, lib=lib)


def _parse_key(q, f):
    t, cfg = q["qtype"], jl(q["cfg"], {})
    if t == "single":
        v = f.get("key", "")
        return v or None
    if t == "multi":
        v = f.getlist("key")
        return v or None
    if t == "fields":
        v = [f.get("key%d" % i, "").strip() for i in range(len(cfg["fields"]))]
        return v if any(v) else None
    if t in ("time_mmss", "time_sec"):
        v = f.get("key", "").strip()
        return v or None
    if t == "table":
        out = []
        for line in f.get("key", "").splitlines():
            m = re.match(r"^\s*(\d+:\d{1,2})\s*[,\s]\s*(.+?)\s*$", line)
            if m:
                out.append({"t": m.group(1), "n": m.group(2)})
        return out or None
    if t == "chords":
        out = []
        for line in f.get("key", "").splitlines():
            p = line.split()
            if len(p) == 3:
                out.append(p)
        return out or None
    return None


@app.route("/admin/question/<int:qid>", methods=["GET", "POST"])
@admin_required
def admin_question(qid):
    c = db()
    q = c.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
    if not q:
        abort(404)
    if request.method == "POST":
        key = _parse_key(q, request.form)
        a = request.form.get("audio", "")
        mp = request.form.get("max_plays", "").strip()
        try:
            pts = float(request.form.get("points") or q["points"])
            unit = float(request.form.get("unit") or q["unit"])
        except ValueError:
            pts, unit = q["points"], q["unit"]
        c.execute("UPDATE questions SET key=?, audio_id=?, max_plays=?, points=?, unit=? WHERE id=?",
                  (json.dumps(key, ensure_ascii=False) if key is not None else None,
                   int(a) if a.isdigit() else None, int(mp) if mp.isdigit() else None, pts, unit, qid))
        flash("Saved %s (Set %d)." % (q["qid"], q["set_no"]), "ok")
        return redirect(url_for("admin_set", n=q["set_no"]))
    lib = c.execute("SELECT * FROM audio ORDER BY original").fetchall()
    key = jl(q["key"])
    keytext = ""
    if q["qtype"] == "table" and key:
        keytext = "\n".join("%s, %s" % (r["t"], r["n"]) for r in key)
    elif q["qtype"] == "chords" and key:
        keytext = "\n".join(" ".join(r) for r in key)
    elif q["qtype"] in ("time_mmss", "time_sec") and key:
        keytext = str(key)
    return render_template("admin_question.html", q=q, lib=lib, key=key, keytext=keytext)


@app.route("/admin/audio", methods=["GET", "POST"])
@admin_required
def admin_audio():
    c = db()
    if request.method == "POST":
        if request.form.get("action") == "delete":
            aid = request.form.get("id", type=int)
            a = c.execute("SELECT * FROM audio WHERE id=?", (aid,)).fetchone()
            if a:
                c.execute("UPDATE questions SET audio_id=NULL WHERE audio_id=?", (aid,))
                c.execute("DELETE FROM audio WHERE id=?", (aid,))
                try:
                    os.remove(os.path.join(AUDIO_DIR, a["stored"]))
                except OSError:
                    pass
                flash("Song deleted.", "ok")
        else:
            n = 0
            for f in request.files.getlist("files"):
                ext = os.path.splitext(f.filename or "")[1].lower()
                if ext not in AUDIO_EXT:
                    flash("Skipped %s (allowed: %s)." % (f.filename, ", ".join(AUDIO_EXT)), "err")
                    continue
                stored = secrets.token_hex(16)               # random name, no extension
                path = os.path.join(AUDIO_DIR, stored)
                f.save(path)
                c.execute("INSERT INTO audio(stored,original,mime,size,uploaded) VALUES(?,?,?,?,?)",
                          (stored, os.path.basename(f.filename), AUDIO_EXT[ext], os.path.getsize(path), now()))
                n += 1
            if n:
                flash("Uploaded %d song(s)." % n, "ok")
        return redirect(url_for("admin_audio"))
    rows = c.execute("SELECT a.*, (SELECT COUNT(*) FROM questions q WHERE q.audio_id=a.id) used FROM audio a "
                     "ORDER BY original").fetchall()
    return render_template("admin_audio.html", rows=rows)


@app.route("/admin/audio/<int:aid>/preview", methods=["POST"])
@admin_required
def admin_audio_preview(aid):
    if "nonce" not in session:
        session["nonce"] = secrets.token_hex(8)
    tok = signer.dumps({"u": current_user()["id"], "a": aid, "q": 0, "n": session["nonce"],
                        "ua": (request.user_agent.string or "")[:200]})
    return jsonify(url=url_for("stream", token=tok))


@app.route("/admin/admins", methods=["GET", "POST"])
@admin_required
def admin_admins():
    c = db()
    if request.method == "POST":
        name, email, pw = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower(), request.form.get("password", "")
        if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or len(pw) < 8:
            flash("Name, valid email and an 8+ character password are required.", "err")
        else:
            try:
                c.execute("INSERT INTO users(name,email,pw,role,created) VALUES(?,?,?,?,?)",
                          (name, email, generate_password_hash(pw), "admin", now()))
                flash("Admin created.", "ok")
            except sqlite3.IntegrityError:
                flash("That email is already registered.", "err")
        return redirect(url_for("admin_admins"))
    return render_template("admin_admins.html", rows=c.execute("SELECT * FROM users WHERE role='admin'").fetchall())


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_required
def admin_settings():
    if request.method == "POST":
        mp = request.form.get("default_max_plays", "3")
        set_setting("default_max_plays", int(mp) if mp.isdigit() else 3)
        set_setting("show_score", "1" if request.form.get("show_score") else "0")
        flash("Settings saved.", "ok")
        return redirect(url_for("admin_settings"))
    return render_template("admin_settings.html", mp=get_setting("default_max_plays", "3"),
                           show=get_setting("show_score", "0") == "1")


@app.route("/admin/export.csv")
@admin_required
def admin_export():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["name", "email", "set", "started", "submitted", "score", "max_scored", "unscored_questions"])
    for u in db().execute("SELECT * FROM users WHERE role='user' ORDER BY id"):
        _, t, mx, un = user_results(u["id"], u["set_no"])
        w.writerow([u["name"], u["email"], u["set_no"], u["started"], u["submitted"], t, mx, un])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=results.csv"})


@app.route("/admin/audiolog")
@admin_required
def admin_audiolog():
    rows = db().execute("SELECT l.*, u.email FROM audio_log l LEFT JOIN users u ON u.id=l.user_id "
                        "ORDER BY l.id DESC LIMIT 300").fetchall()
    return render_template("admin_audiolog.html", rows=rows)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
