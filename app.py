import secrets
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request, redirect
from urllib.parse import quote
from markupsafe import escape
import json, os, re
app = Flask(__name__)
from datetime import datetime, timedelta
def build_slots(shop):
    days=[int(x) for x in shop.get("days",[])] or [0,1,2,3,4]
    try:
        oh,om=[int(x) for x in shop.get("open","09:00").split(":")]
        ch,cm=[int(x) for x in shop.get("close","17:00").split(":")]
    except Exception:
        oh,om,ch,cm=9,0,17,0
    step=int(shop.get("slot","30") or 30)
    taken={b.get("when") for b in shop.get("bookings",[])}
    labels=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    out=[]
    today=datetime.now()
    for dd in range(14):
        day=today+timedelta(days=dd)
        if day.weekday() not in days: continue
        cur=day.replace(hour=oh,minute=om,second=0,microsecond=0)
        end=day.replace(hour=ch,minute=cm,second=0,microsecond=0)
        while cur<end:
            val=cur.strftime("%Y-%m-%d %H:%M")
            if val not in taken and cur>today:
                out.append((val, labels[day.weekday()]+" "+day.strftime("%b %d")+" at "+cur.strftime("%I:%M %p")))
            cur+=timedelta(minutes=step)
    return out

def h(s): return s
DASH_PASS = "bookie123"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
DB = "shops.json"
TEMPLATES = {
 "Hair salon": {"Haircut": 30, "Color": 60, "Blowout": 25, "Treatment": 40},
 "Barber": {"Haircut": 20, "Fade": 25, "Beard trim": 15, "Cut and beard": 35},
 "Nails": {"Manicure": 20, "Pedicure": 30, "Gel set": 40, "Fill": 25},
 "Tattoo": {"Small tattoo": 50, "Medium piece": 100, "Large piece": 200, "Consultation": 0},
 "Massage": {"30 min massage": 30, "60 min massage": 50, "90 min massage": 70},
 "Lashes and brows": {"Lash set": 50, "Lash fill": 30, "Brow shape": 15},
 "Personal trainer": {"1 session": 25, "5 sessions": 100, "Consultation": 0},
 "Cleaning": {"Standard clean": 50, "Deep clean": 100, "Move-out clean": 150},
 "Photography": {"Mini session": 50, "Full session": 100, "Event": 200},
 "Other": {"Appointment": 0}}
def load():
    return json.load(open(DB)) if os.path.exists(DB) else {}
def save(d):
    json.dump(d, open(DB, "w"), indent=2)
S = "<meta name='viewport' content='width=device-width'><style>body{font-family:sans-serif;background:#fff;color:#123;max-width:420px;margin:auto;padding:16px}input,select,button,textarea{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #cdd;font-size:16px;box-sizing:border-box}button{background:#1a6dff;color:#fff;font-weight:bold;border:none}.card{background:#eef3ff;padding:12px;border-radius:8px;margin:8px 0}a{color:#1a6dff}</style>"
@app.route("/")
def home():
    return h("""
<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;font-family:system-ui,Arial;background:#1a6dff;color:#fff;text-align:center}
.wrap{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:28px}
.logo{font-size:40px;font-weight:800;letter-spacing:-1px}
.cal{font-size:40px}
.head{font-size:30px;font-weight:800;margin:22px 0 6px}
.sub{font-size:17px;opacity:.95;margin-bottom:26px}
.btn{background:#fff;color:#1a6dff;font-size:20px;font-weight:800;border:none;border-radius:14px;padding:16px 40px;text-decoration:none}
.benes{margin-top:30px;font-size:16px;line-height:2;opacity:.97}
.trust{margin-top:18px;font-size:14px;opacity:.9}
</style></head><body>
<div class="wrap">
<div class="cal">&#128197;</div>
<div class="logo">Business Bookie</div>
<div class="head">Sign up your business for free</div>
<div class="sub">Your own booking page in minutes.</div>
<a class="btn" href="/new">Get Started</a><div style="margin-top:20px"><a href="/find" style="color:#fff;font-size:17px;text-decoration:underline">Book a business &#8594;</a></div>
<div class="benes">&#9989; Your own booking link<br>&#9989; Get paid up front<br>&#9989; No more DMs</div>
<div class="trust">No credit card needed</div><div style='margin-top:14px'><a href='/login' style='color:#fff;font-size:15px;text-decoration:underline'>Already have a business? Log in</a></div>
</div>
</body></html>
""")


@app.route("/new")
def new():
    opts = "".join(f"<option>{t}</option>" for t in TEMPLATES)
    return S + f"""<h1>Set up your business</h1>
<form method='post' action='/setup'>
<input name='shop' placeholder='Business name' required>
<p>What kind of business?</p>
<select name='btype'>{opts}</select>
<button>Next</button></form>"""
@app.route("/setup", methods=["POST"])
def setup():
    shop = request.form["shop"]
    bt = request.form.get("btype", "Other")
    tpl = TEMPLATES.get(request.form.get("btype"), TEMPLATES["Other"])
    rows = "".join(f"<div class='card'><label><input type='checkbox' name='pick' value='{i}' checked style='width:auto'> {escape(n)}</label><input type='hidden' name='n{i}' value='{escape(n)}'><input type='number' name='f{i}' value='{p}' placeholder='Booking fee $'></div>" for i, (n, p) in enumerate(tpl.items()))
    return S + f"""<h1>Your services</h1><p>Untick what you don't offer and set your booking fees.</p>
<form method='post' action='/create' onsubmit='if(this.sent)return false;this.sent=1'>
<input type='hidden' name='shop' value='{escape(shop)}'><input type='hidden' name='btype' value='{escape(bt)}'><input type='hidden' name='btype' value='{escape(bt)}'>
{rows}
<p>Add your own, one per line: name | booking fee</p>
<input name='addr' placeholder='Business address'><input name='email' placeholder='Your email (we send a confirm link)' type='email' required><input name='pw' type='password' placeholder='Create a password' required><textarea name='custom' rows='3' placeholder='Deluxe package | 40'></textarea>
<input type='hidden' name='lat' id='glat'><input type='hidden' name='lng' id='glng'><button type='button' onclick='navigator.geolocation.getCurrentPosition(p=>(glat.value=p.coords.latitude,glng.value=p.coords.longitude,this.innerText="Location saved"))'>Use my location</button><p><b>Days you're open:</b></p><label style='margin-right:10px'><input type='checkbox' name='days' value='0' checked style='width:auto'> Mon</label><label style='margin-right:10px'><input type='checkbox' name='days' value='1' checked style='width:auto'> Tue</label><label style='margin-right:10px'><input type='checkbox' name='days' value='2' checked style='width:auto'> Wed</label><label style='margin-right:10px'><input type='checkbox' name='days' value='3' checked style='width:auto'> Thu</label><label style='margin-right:10px'><input type='checkbox' name='days' value='4' checked style='width:auto'> Fri</label><label style='margin-right:10px'><input type='checkbox' name='days' value='5'  style='width:auto'> Sat</label><label style='margin-right:10px'><input type='checkbox' name='days' value='6'  style='width:auto'> Sun</label><p>Opening time</p><input type='time' name='open' value='09:00'><p>Closing time</p><input type='time' name='close' value='17:00'><p>Appointment length</p><select name='slot'><option value='30'>30 minutes</option><option value='60'>1 hour</option><option value='90'>90 minutes</option><option value='120'>2 hours</option></select><button>Create my booking page</button></form>"""
@app.route("/create", methods=["POST"])
def create():
    d = load()
    sid = re.sub(r"[^a-z0-9]+", "-", request.form["shop"].lower()).strip("-") or "shop"
    base, i = sid, 2
    while sid in d:
        sid = f"{base}-{i}"; i += 1
    svc = {}
    for k in request.form.getlist("pick"):
        n = request.form.get("n" + k, "").strip()
        p = request.form.get("f" + k, "").strip()
        if n: svc[n] = int(p) if p.isdigit() else 0
    for line in request.form.get("custom", "").splitlines():
        if "|" in line:
            n, p = line.split("|", 1); p = p.strip()
            svc[n.strip()] = int(p) if p.isdigit() else 0
    if not svc: svc["Appointment"] = 0
    tok = secrets.token_urlsafe(16)
    d[sid] = {"live": False, "token": tok, "name": request.form["shop"], "addr": request.form.get("addr",""), "email": request.form.get("email",""), "pw": request.form.get("pw",""), "lat": request.form.get("lat",""), "lng": request.form.get("lng",""), "type": request.form.get("btype","Other"), "type": request.form.get("btype","Other"), "services": svc, "days": request.form.getlist("days"), "open": request.form.get("open","09:00"), "close": request.form.get("close","17:00"), "slot": request.form.get("slot","30"), "bookings": []}
    save(d)
    notify("New business signed up", request.form["shop"])
    notify("Confirm your business on Business Bookie", "Tap to confirm and go live: " + request.host_url + "confirm/" + sid + "/" + tok, request.form["email"])
    return redirect("/d/" + sid + "?pw=" + quote(request.form.get("pw","")))
@app.route("/b/<sid>")
def book_page(sid):
    d = load()
    if sid not in d: return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    prices = "".join(f"<div class='card'><b>{escape(n)}</b> - ${p} booking fee</div>" for n, p in shop["services"].items())
    sl = build_slots(shop)
    if sl:
        slots = "<p><b>Pick a time:</b></p><select name='when' required>" + "".join(f"<option value='{v}'>{lab}</option>" for v, lab in sl) + "</select>"
    else:
        slots = "<p>No open times right now.</p><input name='when' type='datetime-local' required>"
    opts = "".join(f"<option value='{escape(n)}'>{escape(n)} - ${p}</option>" for n, p in shop["services"].items())
    return S + f"""<h1>{escape(shop['name'])}</h1><p>Location: {escape(shop.get('addr',''))}</p>{prices}<p>Book an appointment</p>
<form method='post' action='/book/{sid}'>
<input name='name' placeholder='Your name' required>
<input name='phone' placeholder='Phone number' required>
<select name='service'>{opts}</select>
{slots}
<button>Book now</button></form>"""
@app.route("/book/<sid>", methods=["POST"])
def book(sid):
    d = load()
    if sid not in d: return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    s = request.form["service"]
    fee = shop["services"].get(s, 0)
    shop["bookings"].append({"name": request.form["name"], "phone": request.form["phone"], "service": s, "when": request.form["when"], "fee": fee})
    save(d)
    notify("New booking at " + shop["name"], request.form["name"] + " - " + s + " - " + request.form["when"] + " - " + request.form["phone"], shop.get("email") or GMAIL)
    return S + f"<h1>You're booked!</h1><p>{escape(s)} at {escape(shop['name'])}</p><p>Booking fee: ${fee}. Your booking is confirmed and the business has been notified by email.</p><a href='/b/{sid}'>Back</a>"
@app.route("/d/<sid>")
def dash(sid):
    escape = lambda s: str(__import__('markupsafe').escape(s))
    from urllib.parse import quote
    d = load()
    if sid not in d: return "<h1>Not found</h1>", 404
    pw = request.values.get("pw", "")
    if pw != (d[sid].get("pw") or DASH_PASS):
        return S + "<h1>Owner login</h1><form><input name='pw' type='password' placeholder='Password'><button>View bookings</button></form>"
    shop = d[sid]
    bk = shop["bookings"]
    link = request.host_url + "b/" + sid
    names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    days = ", ".join(names[int(x)] for x in shop.get("days", [])) or "Not set"
    hrs = days + " | " + shop.get("open", "") + " - " + shop.get("close", "")
    ref = "<meta http-equiv='refresh' content='30;url=/d/" + sid + "?pw=" + quote(pw) + "'>"
    head = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;font-family:system-ui,Arial;background:#eef3ff}.top{background:#1a6dff;color:#fff;padding:22px 18px}.top h1{margin:0;font-size:26px}.top p{margin:4px 0 0;opacity:.9}.wrap{padding:16px;max-width:460px;margin:auto}.card{background:#fff;padding:16px;border-radius:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08)}.big{font-size:34px;font-weight:800;color:#1a6dff}a{color:#1a6dff}.note{background:#fff3cd}</style>"
    note = "" if shop.get("live", True) else "<div class='card note'>Almost there! Check your email and tap the confirm link to go live.</div>"
    if bk:
        rows = "".join("<div class='card'><b>" + escape(x['name']) + "</b> - " + escape(x['service']) + "<br>" + escape(x['when']) + "<br>" + escape(x['phone']) + " - fee $" + str(x.get('fee', x.get('deposit', 0))) + "</div>" for x in reversed(bk))
    else:
        rows = "<div class='card'>No bookings yet. Share your link to get your first one!</div>"
    body = ref + head + "<div class='top'><h1>" + escape(shop['name']) + "</h1><p>Your dashboard</p></div><div class='wrap'>" + note + "<div class='card'><div class='big'>" + str(len(bk)) + "</div>total bookings</div><div class='card'><b>Your booking link</b><br><a href='/b/" + sid + "'>" + escape(link) + "</a><br><button onclick=\"if(navigator.share){navigator.share({title:'Book with us',url:'" + link + "'})}else{navigator.clipboard.writeText('" + link + "');this.innerText='Copied!'}\" style='margin-top:10px'>Share link</button></div><div class='card'><b>Open:</b> " + escape(hrs) + "</div><h3>Bookings</h3>" + rows + "<div class='card'><a href='/b/" + sid + "'>View my public page</a> | <a href='/mine?em=" + quote(shop.get('email','')) + "&pw=" + quote(pw) + "'>All my businesses</a> | <a href='/'>Log out</a></div></div>"
    return body.replace("<", chr(60)).replace(">", chr(62))

import smtplib
from email.message import EmailMessage
GMAIL = "infinitymichael29@gmail.com"
GMAIL_PASS = "mlyixivouttufzyf"
def notify(subject, body, to=None):
    try:
        m = EmailMessage()
        m["Subject"] = subject
        m["From"] = GMAIL
        m["To"] = to or GMAIL
        m.set_content(body)
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        s.login(GMAIL, GMAIL_PASS)
        s.send_message(m)
        s.quit()
    except Exception as e:
        print("email failed:", e)
@app.route("/c/<cat>")
def category(cat):
    d = load()
    rows = "".join(f"<a href='/b/{sid}' style='text-decoration:none'><div class='card'><b>{escape(v['name'])}</b><br>{escape(v.get('addr',''))}</div></a>" for sid, v in d.items() if v.get("type", "Other") == cat and v.get("live", True))
    return S + f"<h1>{escape(cat)}</h1>" + (rows or "<p>None yet.</p>") + "<a href='/'>Back</a>"
@app.route("/confirm/<sid>/<tok>")
def confirm(sid, tok):
    d = load()
    if sid in d and d[sid].get("token") == tok:
        d[sid]["live"] = True
        save(d)
        return S + f"<h1>You're live!</h1><p>Customer booking link:</p><a href='/b/{sid}'>/b/{sid}</a><p>Your bookings:</p><a href='/d/{sid}'>/d/{sid}</a>"
    return S + "<h1>Link not valid</h1>", 404
@app.route("/find")
def find():
    from urllib.parse import quote
    d = load()
    counts = {}
    for v in d.values():
        if not v.get("live", True): continue
        k = v.get("type", "Other")
        counts[k] = counts.get(k, 0) + 1
    cats = "".join(f"<a href='/c/{quote(k)}' style='text-decoration:none'><div class='card'><b>{escape(k)}</b> - {n} businesses</div></a>" for k, n in [(k, counts.get(k, 0)) for k in TEMPLATES])
    return S + "<h1>Find a business</h1><form action='/search'><input name='q' placeholder='Search by name or type'><button>Search</button></form><button onclick='navigator.geolocation.getCurrentPosition(p=>location.href=`/near?lat=${p.coords.latitude}&lng=${p.coords.longitude}`)'>Businesses near me</button><p>Or browse by category:</p>" + (cats or "<p>No businesses yet.</p>") + "<a href='/'>Back</a>"
@app.route("/search")
def search():
    d = load()
    q = request.args.get("q", "").lower()
    rows = "".join(f"<a href='/b/{sid}' style='text-decoration:none'><div class='card'><b>{escape(v['name'])}</b><br>{escape(v.get('type',''))} - {escape(v.get('addr',''))}</div></a>" for sid, v in d.items() if v.get("live", True) and (q in v['name'].lower() or q in v.get('type','').lower()))
    return S + f"<h1>Results for '{escape(q)}'</h1>" + (rows or "<p>Nothing found.</p>") + "<a href='/find'>Back</a>"
@app.route("/near")
def near():
    import math
    d = load()
    try:
        la = float(request.args["lat"]); lo = float(request.args["lng"])
    except Exception:
        return S + "<h1>Location not available</h1><a href='/find'>Back</a>"
    out = []
    for sid, v in d.items():
        if not v.get("live", True): continue
        try:
            bl = float(v.get("lat")); bg = float(v.get("lng"))
        except Exception:
            continue
        h = math.sin(math.radians(bl - la) / 2) ** 2 + math.cos(math.radians(la)) * math.cos(math.radians(bl)) * math.sin(math.radians(bg - lo) / 2) ** 2
        out.append((3959 * 2 * math.asin(math.sqrt(h)), sid, v))
    out.sort(key=lambda x: x[0])
    rows = "".join(f"<a href='/b/{sid}' style='text-decoration:none'><div class='card'><b>{escape(v['name'])}</b><br>{escape(v.get('type',''))} - {escape(v.get('addr',''))}<br>{mi:.1f} miles away</div></a>" for mi, sid, v in out)
    return S + "<h1>Near you</h1>" + (rows or "<p>No businesses with a location yet.</p>") + "<a href='/find'>Back</a>"
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        d = load()
        em = request.form.get("em", "")
        pw = request.form.get("pw", "")
        for sid, v in d.items():
            if v.get("email") == em and v.get("pw") == pw:
                return redirect("/mine?em=" + quote(em) + "&pw=" + quote(pw))
        return S + "<h1>Wrong email or password</h1><a href='/login'>Try again</a>"
    return S + "<h1>Business owner log in</h1><form method='post'><input name='em' type='email' placeholder='Email' required><input name='pw' type='password' placeholder='Password' required><button>Log in</button></form><p>New here? <a href='/new'>Create an account and set up your business</a></p><a href='/'>Back</a>"
@app.route("/mine")
def mine():
    from urllib.parse import quote
    escape = lambda s: str(__import__('markupsafe').escape(s))
    d = load()
    em = request.args.get("em", "")
    pw = request.args.get("pw", "")
    owned = [(sid, v) for sid, v in d.items() if em and v.get("email") == em and v.get("pw") == pw]
    if not owned: return redirect("/login")
    if len(owned) == 1: return redirect("/d/" + owned[0][0] + "?pw=" + quote(pw))
    head = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;font-family:system-ui,Arial;background:#eef3ff}.top{background:#1a6dff;color:#fff;padding:22px 18px}.top h1{margin:0;font-size:26px}.wrap{padding:16px;max-width:460px;margin:auto}.card{display:block;background:#fff;padding:16px;border-radius:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);color:#123;text-decoration:none}a{color:#1a6dff}</style>"
    rows = "".join("<a class='card' href='/d/" + sid + "?pw=" + quote(pw) + "'><b>" + escape(v['name']) + "</b><br>" + escape(v.get('type','')) + " - " + str(len(v.get('bookings',[]))) + " bookings</a>" for sid, v in owned)
    return head + "<div class='top'><h1>My businesses</h1></div><div class='wrap'>" + rows + "<a href='/new'>+ Add another business</a> | <a href='/'>Log out</a></div>"

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
