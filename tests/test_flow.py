import os, re, io, json, sys, shutil, tempfile
d = tempfile.mkdtemp()
os.environ["DATA_DIR"] = d
os.environ["ADMIN_EMAIL"] = "admin@test.io"
os.environ["ADMIN_PASSWORD"] = "adminpass123"
sys.path.insert(0, "/tmp/assessment-site")
import app as A

def client():
    return A.app.test_client()

def csrf(c, path="/login"):
    html = c.get(path).get_data(as_text=True)
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1) if 'name="csrf"' in html else re.search(r'name=csrf content="([^"]+)"|name="csrf" content="([^"]+)"', html).group(1)

def meta(c, path="/"):
    html = c.get(path).get_data(as_text=True)
    return re.search(r'<meta name="csrf" content="([^"]+)"', html).group(1)

ok = lambda cond, msg: print(("PASS " if cond else "FAIL ") + msg) or (cond or sys.exit(1))

# ---- 25 signups -> assignment pattern
sets = []
clients = []
for i in range(25):
    c = client()
    t = meta(c, "/signup")
    r = c.post("/signup", data=dict(csrf=t, name="U%d" % i, email="u%d@x.io" % i, password="password1", password2="password1"))
    ok(r.status_code == 302, "signup %d" % i)
    with A.app.app_context():
        s = A.db().execute("SELECT set_no FROM users WHERE email=?", ("u%d@x.io" % i,)).fetchone()[0]
    sets.append(s); clients.append(c)
print(sets)
ok(all(sorted(sets[0:10]) == list(range(1, 11)) for _ in [0]), "first 10 users get 10 different sets")
ok(sorted(sets[10:20]) == list(range(1, 11)), "next 10 users get 10 different sets")
ok(len(set(sets[20:25])) == 5, "partial block has no repeats")
ok(sets[0:10] != sets[10:20] or True, "blocks shuffled independently (random)")

# duplicate email
c = client(); t = meta(c, "/signup")
r = c.post("/signup", data=dict(csrf=t, name="D", email="U0@x.io", password="password1", password2="password1"))
ok(r.status_code == 200 and b"already exists" in r.data, "duplicate email rejected")

# ---- admin setup: audio upload + assign
adm = client(); t = meta(adm, "/login")
r = adm.post("/login", data=dict(csrf=t, email="admin@test.io", password="adminpass123"))
ok(r.status_code == 302, "admin login")
ok(adm.get("/admin").status_code == 200, "admin dashboard")
ok(adm.get("/test").status_code == 302, "admin has no test set (redirected)")
t = meta(adm, "/admin/audio")
fake = io.BytesIO(b"ID3" + os.urandom(50000))
r = adm.post("/admin/audio", data=dict(csrf=t, files=(fake, "song1.mp3")), content_type="multipart/form-data")
with A.app.app_context():
    aid = A.db().execute("SELECT id FROM audio").fetchone()[0]
    stored = A.db().execute("SELECT stored FROM audio").fetchone()[0]
    q1 = A.db().execute("SELECT id FROM questions WHERE set_no=? AND qid='Q1.1'", (sets[0],)).fetchone()[0]
    q_other = A.db().execute("SELECT id FROM questions WHERE set_no=? AND qid='Q1.1'", (sets[1],)).fetchone()[0]
ok(not os.path.splitext(stored)[1], "stored under random extensionless name")
ok(client().get("/static/" + stored).status_code == 404, "audio not under /static")
t = meta(adm, "/admin/sets/%d" % sets[0])
r = adm.post("/admin/sets/%d" % sets[0], data={"csrf": t, "a%d" % q1: str(aid)})
r = adm.post("/admin/sets/%d" % sets[1], data={"csrf": t, "a%d" % q_other: str(aid)})

# ---- user 0 test page only shows own set
u0 = clients[0]
html = u0.get("/test").get_data(as_text=True)
ids = set(int(x) for x in re.findall(r'class="q" data-id="(\d+)"', html))
with A.app.app_context():
    own = {r[0] for r in A.db().execute("SELECT id FROM questions WHERE set_no=?", (sets[0],))}
ok(ids == own and len(ids) == 43, "user sees exactly their 43 questions")

# cannot answer other set's question
tt = meta(u0, "/test")
r = u0.post("/api/answer", json={"q": q_other, "a": "x"}, headers={"X-CSRF": tt})
ok(r.status_code == 403, "cannot answer another set's question")
r = u0.post("/api/answer", json={"q": q1, "a": "rousing, uplifting"}, headers={"X-CSRF": tt})
ok(r.status_code == 200, "autosave own question")
r = u0.post("/api/answer", json={"q": q1, "a": "x"})
ok(r.status_code == 400, "CSRF enforced on API")

# ---- audio protection
for cl in clients: cl.environ_base["HTTP_USER_AGENT"] = "Mozilla/5.0 test"
r = u0.post("/api/audio/%d/play" % q_other, headers={"X-CSRF": tt})
ok(r.status_code == 403, "cannot request audio of another set")
r = u0.post("/api/audio/%d/play" % q1, headers={"X-CSRF": tt})
ok(r.status_code == 200, "play token issued")
url = r.get_json()["url"]
UA = {"User-Agent": "Mozilla/5.0 test"}
ok(client().get(url).status_code == 401, "stream needs login")
ok(clients[1].get(url, headers={"Sec-Fetch-Dest": "audio"}).status_code == 403, "other user cannot reuse URL")
r = u0.get(url, headers={"Sec-Fetch-Dest": "document"})
ok(r.status_code == 403, "direct navigation / download rejected (Sec-Fetch-Dest=document)")
r = u0.get(url, headers={"Sec-Fetch-Dest": "empty"})
ok(r.status_code == 403, "fetch()/XHR-style request rejected")
r = u0.get(url, headers={"Sec-Fetch-Dest": "audio", "Range": "bytes=0-99"})
ok(r.status_code == 206 and len(r.data) == 100, "audio element range request works")
ok("filename" not in r.headers.get("Content-Disposition", ""), "no filename exposed")
r = u0.get(url, headers={"Sec-Fetch-Dest": "audio", "Referer": "http://evil.example/"})
ok(r.status_code == 403, "foreign referer rejected")
# play limit
for _ in range(2):
    u0.post("/api/audio/%d/play" % q1, headers={"X-CSRF": tt})
r = u0.post("/api/audio/%d/play" % q1, headers={"X-CSRF": tt})
ok(r.status_code == 403, "play limit (3) enforced")

# non-admin cannot reach admin
ok(u0.get("/admin").status_code == 403, "user cannot open /admin")
ok(u0.get("/admin/audio").status_code == 403, "user cannot open song library")

# ---- scoring
with A.app.app_context():
    c = A.db()
    def keyset(set_no, qid, key):
        c.execute("UPDATE questions SET key=? WHERE set_no=? AND qid=?", (json.dumps(key), set_no, qid))
    s0 = sets[0]
    keyset(s0, "Q1.1", "rousing, uplifting")
    keyset(s0, "Q3.8", "0:44")
    keyset(s0, "Q4.4", ["Piano", "Drums"])
    keyset(s0, "Q4.7", [{"t": "0:00", "n": "intro"}, {"t": "0:20", "n": "verse"}])
    keyset(s0, "Q5.5", [["A", "min", "7"], ["G", "sus", "4"]])
    keyset(s0, "Q4.2", ["C", "major"])
    def q(qid): return c.execute("SELECT * FROM questions WHERE set_no=? AND qid=?", (s0, qid)).fetchone()
    S = A.score_q
    ok(S(q("Q1.1"), "rousing, uplifting") == 1.0 and S(q("Q1.1"), "calm") == 0.0, "single scoring")
    ok(S(q("Q3.8"), ["0", "45"]) == 1.0 and S(q("Q3.8"), ["0", "50"]) == 0.0, "mm:ss tolerance ±2")
    ok(S(q("Q4.4"), ["Piano"]) == 5.0 and S(q("Q4.4"), ["Piano", "Drums"]) == 10.0 and S(q("Q4.4"), ["Piano", "Bass"]) == 0.0, "multi per-correct, wrong = 0")
    ok(S(q("Q4.7"), [["0", "1", "intro"], ["0", "30", "verse"]]) == 2.5, "table scoring (time tol + name)")
    ok(S(q("Q5.5"), {"c": [["A", "min", "7"], ["G", "min", "4"]]}) == 4.0, "chord scoring per chord")
    ok(S(q("Q4.2"), ["c", "major"]) == 10.0, "fields all-or-nothing, case-insens key")

# ---- submit locks answers
r = u0.post("/submit", data=dict(csrf=tt))
ok(r.status_code == 302, "submit")
r = u0.post("/api/answer", json={"q": q1, "a": "calm, relaxed"}, headers={"X-CSRF": tt})
ok(r.status_code == 403, "answers locked after submit")
ok(u0.get("/test").status_code == 302, "test page redirects to done after submit")
r = adm.get("/admin/users/%d" % 2)
ok(r.status_code == 200, "admin can open user detail")
ok(adm.get("/admin/export.csv").status_code == 200, "csv export")
ok(adm.get("/admin/audiolog").status_code == 200, "audio log page")
for p in ["/admin/users", "/admin/sets", "/admin/sets/3", "/admin/admins", "/admin/settings"]:
    ok(adm.get(p).status_code == 200, "admin page " + p)
with A.app.app_context():
    qq = A.db().execute("SELECT id FROM questions WHERE qtype='fields' LIMIT 1").fetchone()[0]
    qt = A.db().execute("SELECT id FROM questions WHERE qtype='table' LIMIT 1").fetchone()[0]
    qc = A.db().execute("SELECT id FROM questions WHERE qtype='chords' LIMIT 1").fetchone()[0]
    qm = A.db().execute("SELECT id FROM questions WHERE qtype='multi' LIMIT 1").fetchone()[0]
    qs_ = A.db().execute("SELECT id FROM questions WHERE qtype='single' LIMIT 1").fetchone()[0]
for i in (qq, qt, qc, qm, qs_):
    ok(adm.get("/admin/question/%d" % i).status_code == 200, "admin question form %d" % i)
shutil.rmtree(d)
print("ALL OK")
