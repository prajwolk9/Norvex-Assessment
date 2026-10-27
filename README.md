# Music Ability Assessment website (Flask + SQLite)

## Run it
```bash
pip install -r requirements.txt
export ADMIN_EMAIL=you@example.com ADMIN_PASSWORD='choose-a-strong-one'   # before FIRST run
python app.py                      # dev: http://localhost:5000
# production (keep ONE worker process; SQLite + in-memory login throttle):
COOKIE_SECURE=1 gunicorn -w 1 --threads 8 -b 127.0.0.1:8000 app:app      # behind nginx/Caddy with HTTPS
```
If you don't set ADMIN_* the first run creates `admin@example.com` with a random password printed in the console.
Data lives in `instance/` (database, secret key, private audio). Back it up; never expose it.

## What it does
- Landing page → Sign up / Log in. Admins log in with the same form and get the admin area (no question set).
- **Set assignment:** every consecutive group of 10 sign-ups receives a random permutation of sets 1–10 (a new
  random shuffle per group), so no set repeats inside a group. Done in one DB transaction, so simultaneous
  sign-ups can't collide. A user only ever loads, answers, and hears audio for their own set (checked server-side
  on every request). Deleting a user does not free their slot, keeping the rotation balanced.
- **Test page:** all 43 questions of the set, autosave, progress counter, submit-and-lock.
- **Admin:** upload songs → assign a song to any question of any set (Sets & songs), per-question play limit,
  answer keys + points, view/override each candidate's scores, re-open attempts, reset passwords, add admins,
  CSV export, audio access log, settings.
- Scoring is automatic once you enter answer keys (Admin → Sets → Key / limits). Default points are placeholders
  (1 per simple question; the point values stated in the PDF for Q4/Q5) — adjust per question.

## Song protection (read this)
Implemented: songs are stored outside the web root under random names; there is no file URL. Each play requests a
short-lived signed stream URL bound to the user, session and browser; it is refused for other users, direct
navigation, fetch/XHR-style requests (anything whose `Sec-Fetch-Dest` isn't `audio`) and foreign referers; responses
are `no-store` with no filename; plays are limited per question; every stream request is logged (Admin → Audio
access log); no download button, context menu disabled on the player.

**Not possible:** no website can fully stop a determined user from capturing audio that the browser plays — screen/
system-audio recording, "stream capture" extensions that hook the audio element, or tools that replay the browser's
own request can still get it. These measures stop casual downloading, right-click/URL saving, sharing links, and
most download extensions, and make abuse visible in the log. If you need stronger protection, the options are
DRM-style encrypted streaming (Widevine via a provider), or shorter/lower-quality clips so a leaked copy has little
value.
