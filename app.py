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
<div class="trust">Free business signup &middot; No credit card needed</div><div style='margin-top:14px'><a href='/login' style='color:#fff;font-size:15px;text-decoration:underline'>Already have a business? Log in to check bookings</a></div>
</div>
</body></html>
""")


@app.route("/new")
def new():
    opts = "".join(f"<option>{t}</option>" for t in TEMPLATES)
    return S + f"""<h1>Set up your business</h1>
<form method='post' action='/setup'>
<input name='shop' placeholder='Business name' required><input name='owner' placeholder='Your name' required>
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
<input type='hidden' name='shop' value='{escape(shop)}'><input type='hidden' name='owner' value='{escape(request.values.get('owner',''))}'><input type='hidden' name='btype' value='{escape(bt)}'><input type='hidden' name='btype' value='{escape(bt)}'>
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
    d[sid] = {"live": False, "token": tok, "name": request.form["shop"], "owner": request.form.get("owner", ""), "addr": request.form.get("addr",""), "email": request.form.get("email",""), "pw": request.form.get("pw",""), "lat": request.form.get("lat",""), "lng": request.form.get("lng",""), "type": request.form.get("btype","Other"), "type": request.form.get("btype","Other"), "services": svc, "days": request.form.getlist("days"), "open": request.form.get("open","09:00"), "close": request.form.get("close","17:00"), "slot": request.form.get("slot","30"), "bookings": []}
    save(d)
    notify("New business signed up", request.form["shop"])
    notify("Confirm your business on Business Bookie", "Tap to confirm and go live: " + request.host_url + "confirm/" + sid + "/" + tok, request.form["email"])
    _bb_sess["own_" + sid] = True
    return redirect("/done/" + sid)
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
    rv = shop.get("reviews", [])
    if rv:
        avg = sum(r["stars"] for r in rv) / len(rv)
        full = int(round(avg))
        revs = "<div class='card'><b>" + "&#9733;" * full + "&#9734;" * (5 - full) + " " + ("%.1f" % avg) + "</b> (" + str(len(rv)) + " reviews)" + "".join("<p>" + "&#9733;" * r["stars"] + " " + str(escape(r.get("text", ""))) + " <i>- " + str(escape(r.get("name", ""))) + "</i></p>" for r in reversed(rv[-10:])) + "</div>"
    else:
        revs = ""
    ow = ("<p><b>with " + str(escape(shop.get("owner", ""))) + "</b></p>") if shop.get("owner") else ""
    return S + f"""<h1>{escape(shop['name'])}</h1>{ow}<p>Location: {escape(shop.get('addr',''))}</p>{revs}{prices}<p>Book an appointment</p>
<form method='post' action='/book/{sid}'>
<input name='name' placeholder='Your name' required>
<input name='phone' placeholder='Phone number' required>
<input name='email' type='email' placeholder='Email (we send your booking link)' required>
<select name='service'>{opts}</select>
{slots}
<div style='background:#fff6e5;border:1px solid #f0c36d;border-radius:10px;padding:12px;margin:12px 0;font-size:14px'><b>Cancellation terms</b><br>You pay in full now to hold your spot. You can <b>reschedule for free</b>. If you <b>cancel</b>, you get a refund minus a small processing fee (card fees + 3.7% service fee).</div>
<label style='display:flex;gap:8px;align-items:flex-start;margin:10px 0'><input type='checkbox' name='agree' value='1' required style='width:auto;margin-top:3px'> I have read and agree to the cancellation terms</label>
<button>Book now</button></form>"""
def _bb_g(o, k):
    try:
        return o[k]
    except Exception:
        return None

@app.route("/book/<sid>", methods=["POST"])
def book(sid):
    d = load()
    if sid not in d: return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    s = request.form["service"]
    fee = shop["services"].get(s, 0)
    if not request.form.get("email"):
        return S + "<h1>Please enter your email</h1><p>We send your booking link there.</p><a href='/b/" + sid + "'>Back</a>"
    if not request.form.get("agree"):
        return S + "<h1>Please agree to the cancellation terms</h1><p>Go back and tick the box to book.</p><a href='/b/" + sid + "'>Back</a>"
    import os
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if key and float(fee or 0) > 0:
        import stripe
        stripe.api_key = key
        base = request.host_url.rstrip("/") if "localhost" in request.host else "https://" + request.host
        try:
            cs = stripe.checkout.Session.create(
                mode="payment",
                **_bb_pi(shop, fee), line_items=[{"price_data": {"currency": "usd", "product_data": {"name": s + " booking fee - " + shop["name"]}, "unit_amount": int(round(float(fee) * 100))}, "quantity": 1}],
                metadata={"sid": sid, "name": request.form["name"], "phone": request.form["phone"], "service": s, "when": request.form["when"], "email": request.form.get("email", "")[:200]},
                success_url=base + "/paid/" + sid + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=base + "/b/" + sid)
        except Exception as ex:
            return S + "<h1>Payment error</h1><p>" + str(escape(str(ex))) + "</p><a href='/b/" + sid + "'>Back</a>"
        return redirect(cs.url, code=303)
    rt = secrets.token_urlsafe(8)
    shop["bookings"].append({"name": request.form["name"], "phone": request.form["phone"], "service": s, "when": request.form["when"], "fee": fee, "rt": rt, "email": request.form.get("email", "")})
    save(d)
    notify("New booking at " + shop["name"], request.form["name"] + " - " + s + " - " + request.form["when"] + " - " + request.form["phone"], shop.get("email") or GMAIL)
    if request.form.get("email"):
        ml = request.host_url + "m/" + sid + "/" + rt
        notify("Your booking at " + shop["name"], "You're booked!\n\n" + s + " at " + shop["name"] + "\nWhen: " + request.form["when"] + "\n\nNeed to cancel or reschedule? Use this link:\n" + ml, request.form["email"])
    return S + f"<h1>You're booked!</h1><p>{escape(s)} at {escape(shop['name'])}</p><p>Booking fee: ${fee}. Your booking is confirmed and the business has been notified by email.</p><p><b>After your appointment, leave a review here (save this link):</b><br><a href='/r/{sid}/{rt}'>{request.host_url}r/{sid}/{rt}</a></p><a href='/b/{sid}'>Back</a>"
@app.route("/d/<sid>", methods=["GET", "POST"])
def dash(sid):
    escape = lambda s: str(__import__('markupsafe').escape(s))
    from urllib.parse import quote
    d = load()
    if sid not in d: return "<h1>Not found</h1>", 404
    pw = request.values.get("pw", "")
    if not _bb_ok(sid, pw, d[sid]):
        return S + "<h1>Owner login</h1><form method='post'><input name='pw' type='password' placeholder='Password'><button>View bookings</button></form>"
    if request.args.get("pw"): return redirect("/d/" + sid)
    pw = ""
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
    acct = shop.get("acct", "")
    pq = "?pw=" + quote(pw)
    cb = "display:block;text-align:center;background:#1a6dff;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:700;margin-top:10px"
    if shop.get("payouts_on"):
        pay = "<div class='card'><b>&#9989; Payments on</b><br>Customer payments go to your bank.</div>"
    elif acct:
        pay = "<div class='card note'><b>Payment setup not finished</b><a style='" + cb + "' href='/connect/" + sid + pq + "'>Finish payment setup</a></div>"
    else:
        pay = "<div class='card'><b>Get paid online</b><br>Connect your bank so customers can pay when they book. Takes a few minutes.<a style='" + cb + "' href='/connect/" + sid + pq + "'>Connect payments</a></div>"
    body = ref + head + "<div class='top'><h1>" + escape(shop['name']) + "</h1><p>Your dashboard</p><a href='/' style='color:#fff;font-weight:700;text-decoration:none'>&#127968; Home</a></div><div class='wrap'>" + note + "<div class='card'><div class='big'>" + str(len(bk)) + "</div>total bookings</div><div class='card'><b>Your booking link</b><br><a href='/b/" + sid + "'>" + escape(link) + "</a><br><button onclick=\"if(navigator.share){navigator.share({title:'Book with us',url:'" + link + "'})}else{navigator.clipboard.writeText('" + link + "');this.innerText='Copied!'}\" style='margin-top:10px'>Share link</button></div><div class='card'><b>Open:</b> " + escape(hrs) + "</div><div class='card' style='display:flex;gap:10px;flex-wrap:wrap'><a href='/new' style='flex:1;text-align:center;background:#1a6dff;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:700'>+ Add another business</a><a href='/b/" + sid + "' style='flex:1;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700'>Book an appointment</a></div>" + pay + "<h3>Bookings</h3>" + rows + "<div class='card'><a href='/b/" + sid + "'>View my public page</a> | <a href='/mine?em=" + quote(shop.get('email','')) + "&pw=" + quote(pw) + "'>All my businesses</a> | <a href='/pw/" + sid + "'>Change password</a> | <a href='/'>Log out</a></div></div>"
    return body.replace("<", chr(60)).replace(">", chr(62))

import smtplib
from email.message import EmailMessage
GMAIL = "infinitymichael29@gmail.com"
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
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
                for _k, _v in d.items():
                    if _v.get("email") == em and _v.get("pw") == pw: _bb_sess["own_" + _k] = True
                return redirect("/mine?em=" + quote(em))
        return S + "<h1>Wrong email or password</h1><a href='/login'>Try again</a>"
    return S + "<h1>Business owner log in</h1><form method='post'><input name='em' type='email' placeholder='Email' required><input name='pw' type='password' placeholder='Password' required><button>Log in</button></form><p><a href='/forgot'>Forgot password?</a></p><p>New here? <a href='/new'>Create an account and set up your business</a></p><a href='/'>Back</a>"
@app.route("/mine")
def mine():
    from urllib.parse import quote
    escape = lambda s: str(__import__('markupsafe').escape(s))
    d = load()
    em = request.args.get("em", "")
    pw = request.args.get("pw", "")
    owned = [(sid, v) for sid, v in d.items() if em and v.get("email") == em and (pw and v.get("pw") == pw or _bb_sess.get("own_" + sid))]
    if not owned: return redirect("/login")
    if len(owned) == 1: return redirect("/d/" + owned[0][0] + "?pw=" + quote(pw))
    head = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;font-family:system-ui,Arial;background:#eef3ff}.top{background:#1a6dff;color:#fff;padding:22px 18px}.top h1{margin:0;font-size:26px}.wrap{padding:16px;max-width:460px;margin:auto}.card{display:block;background:#fff;padding:16px;border-radius:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);color:#123;text-decoration:none}a{color:#1a6dff}</style>"
    rows = "".join("<a class='card' href='/d/" + sid + "?pw=" + quote(pw) + "'><b>" + escape(v['name']) + "</b><br>" + escape(v.get('type','')) + " - " + str(len(v.get('bookings',[]))) + " bookings</a>" for sid, v in owned)
    return head + "<div class='top'><h1>My businesses</h1></div><div class='wrap'>" + rows + "<a href='/new'>+ Add another business</a> | <a href='/'>Log out</a></div>"


import os, secrets as _bb_secrets
from flask import session as _bb_sess
app.secret_key = os.environ.get("SECRET_KEY") or app.secret_key or _bb_secrets.token_hex(32)

def _bb_ok(sid, pw, shop):
    if _bb_sess.get("own_" + sid):
        return True
    if pw and pw == (shop.get("pw") or DASH_PASS):
        _bb_sess["own_" + sid] = True
        _bb_sess.permanent = True
        return True
    return False

@app.route("/logout")
def _bb_logout():
    _bb_sess.clear()
    return redirect("/")

@app.route("/pw/<sid>", methods=["GET", "POST"])
def change_pw(sid):
    from markupsafe import escape as e
    d = load()
    if sid not in d:
        return S + "<h1>Business not found</h1><a href='/'>Home</a>"
    if request.method == "POST":
        old = request.form.get("old", "")
        new = request.form.get("new", "")
        if old != d[sid].get("pw"):
            return S + "<h1>Current password is wrong</h1><a href='/pw/" + sid + "'>Try again</a>"
        if len(new) < 6 or new != request.form.get("new2", ""):
            return S + "<h1>New passwords must match and be at least 6 characters</h1><a href='/pw/" + sid + "'>Try again</a>"
        em = d[sid].get("email")
        for k, v in d.items():
            if v.get("email") == em and v.get("pw") == old:
                v["pw"] = new
        save(d)
        _bb_sess["own_" + sid] = True
        return redirect("/d/" + sid)
    return S + "<h1>Change password</h1><p>" + str(e(d[sid]["name"])) + "</p><form method='post'><input name='old' type='password' placeholder='Current password' required><input name='new' type='password' placeholder='New password' required><input name='new2' type='password' placeholder='New password again' required><button>Save new password</button></form><a href='/login'>Back</a>"

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        import secrets, time
        em = request.form.get("em", "").strip()
        d = load()
        tok = secrets.token_urlsafe(16)
        found = False
        for k, v in d.items():
            if em and v.get("email") == em:
                v["reset"] = tok
                v["reset_at"] = time.time()
                found = True
        if found:
            save(d)
            link = request.host_url.rstrip("/") + "/reset/" + tok
            try:
                notify("Business Bookie - reset your password", "Tap this link to set a new password (works for 1 hour):\n\n" + link, to=em)
            except Exception as ex:
                print("RESET EMAIL FAILED:", ex)
        return S + "<h1>Check your email</h1><p>If that email has an account, we sent a reset link. It works for 1 hour.</p><a href='/login'>Back to log in</a>"
    return S + "<h1>Forgot password</h1><form method='post'><input name='em' type='email' placeholder='Your email' required><button>Send reset link</button></form><a href='/login'>Back</a>"

@app.route("/reset/<tok>", methods=["GET", "POST"])
def reset_pw(tok):
    import time
    d = load()
    acct = [v for v in d.values() if tok and v.get("reset") == tok and time.time() - v.get("reset_at", 0) < 3600]
    if not acct:
        return S + "<h1>This link expired or is not valid</h1><a href='/forgot'>Send a new one</a>"
    if request.method == "POST":
        new = request.form.get("new", "")
        if len(new) < 6 or new != request.form.get("new2", ""):
            return S + "<h1>Passwords must match and be at least 6 characters</h1><a href='/reset/" + tok + "'>Try again</a>"
        for v in acct:
            v["pw"] = new
            v.pop("reset", None)
            v.pop("reset_at", None)
        save(d)
        return S + "<h1>Password changed</h1><a href='/login'>Log in now</a>"
    return S + "<h1>Set a new password</h1><form method='post'><input name='new' type='password' placeholder='New password' required><input name='new2' type='password' placeholder='New password again' required><button>Save</button></form>"


@app.route("/paid/<sid>")
def paid(sid):
    import os, json, stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    try:
        info = json.loads(str(stripe.checkout.Session.retrieve(request.args.get("session_id", ""))))
    except Exception:
        return S + "<h1>Could not find that payment</h1><a href='/b/" + sid + "'>Back</a>"
    m = info.get("metadata") or {}
    if info.get("payment_status") != "paid" or m.get("sid") != sid:
        return S + "<h1>Payment not completed</h1><a href='/b/" + sid + "'>Try again</a>"
    d = load()
    if sid not in d:
        return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    fee = (info.get("amount_total") or 0) / 100
    import secrets
    ex = [b for b in shop["bookings"] if b.get("paid_id") == info["id"]]
    rt = ex[0].get("rt", "") if ex else secrets.token_urlsafe(8)
    if not ex:
        shop["bookings"].append({"name": m["name"], "phone": m["phone"], "service": m["service"], "when": m["when"], "fee": fee, "paid": True, "paid_id": info["id"], "rt": rt, "email": m.get("email", ""), "pi": _bb_g(info, "payment_intent"), "keep": (_bb_pi(shop, fee).get("payment_intent_data") or {}).get("application_fee_amount")})
        save(d)
        notify("New PAID booking at " + shop["name"], m["name"] + " - " + m["service"] + " - " + m["when"] + " - " + m["phone"] + " - paid $" + ("%.2f" % fee), shop.get("email") or GMAIL)
        if m.get("email"):
            ml = request.host_url + "m/" + sid + "/" + rt
            notify("Your booking at " + shop["name"], "You're booked and paid!\n\n" + m["service"] + " at " + shop["name"] + "\nWhen: " + m["when"] + "\nPaid: $" + ("%.2f" % fee) + "\n\nNeed to cancel or reschedule? Use this link:\n" + ml + "\n\nRescheduling is free. If you cancel, you get a refund minus a small processing fee (card fees + 3.7% service fee).", m["email"])
    return S + "<h1>You're booked and paid!</h1><p>" + str(escape(m["service"])) + " at " + str(escape(shop["name"])) + "</p><p>Booking fee paid: $" + ("%.2f" % fee) + ". The business has been notified.</p><p style='background:#eef3ff;border-radius:10px;padding:12px'>&#9993; We emailed your confirmation to <b>" + str(escape(m.get("email", ""))) + "</b>. It has your link to <b>reschedule or cancel</b>. Check your spam folder if you don't see it.</p><p><b>Need to cancel or reschedule? Save this link:</b><br><a href='/m/" + sid + "/" + rt + "'>" + request.host_url + "m/" + sid + "/" + rt + "</a></p><p><b>After your appointment, leave a review here (save this link):</b><br><a href='/r/" + sid + "/" + rt + "'>" + request.host_url + "r/" + sid + "/" + rt + "</a></p><a href='/b/" + sid + "'>Back</a>"


@app.route("/m/<sid>/<rt>", methods=["GET", "POST"])
def _bb_manage(sid, rt):
    d = load()
    shop = d.get(sid)
    if not shop or not rt:
        return S + "<h1>Booking not found</h1>", 404
    b = next((x for x in shop.get("bookings", []) if x.get("rt") == rt), None)
    if b is None:
        c = next((x for x in shop.get("cancelled", []) if x.get("rt") == rt), None)
        if c:
            return S + "<h1>This booking was cancelled</h1><p>Refund: $" + ("%.2f" % (c.get("refund") or 0)) + "</p><a href='/b/" + sid + "'>Book again</a>"
        return S + "<h1>Booking not found</h1>", 404
    total = int(round(float(b.get("fee") or 0) * 100))
    keep = b.get("keep")
    if keep is None:
        keep = (int(round(total * BB_CUT)) + int(round(total * 0.029)) + 30) if total else 0
    amt = max(total - keep, 0)
    amt_s = "%.2f" % (amt / 100)
    try:
        started = datetime.strptime(b.get("when", ""), "%Y-%m-%d %H:%M") <= datetime.now()
    except Exception:
        started = False
    head = "<h1>Your booking</h1><p><b>" + str(escape(b.get("service", ""))) + "</b> at " + str(escape(shop["name"])) + "</p><p>When: " + str(escape(b.get("when", ""))) + "</p><p>Paid: $" + ("%.2f" % (total / 100)) + "</p>"
    if started:
        return S + head + "<p>This appointment has already started, so it can't be changed online. Please contact the business.</p>"
    if request.method == "POST" and request.form.get("act") == "cancel":
        if total and not b.get("pi"):
            return S + head + "<p>Online refunds aren't available for this booking. Please contact the business.</p>"
        if b.get("pi") and amt > 0:
            import stripe
            stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            kw = {"payment_intent": b["pi"], "amount": amt}
            if b.get("keep") is not None:
                kw["reverse_transfer"] = True
            try:
                stripe.Refund.create(**kw)
            except Exception as e:
                return S + head + "<p>Refund failed: " + str(escape(str(e))) + "</p>"
        b["refund"] = amt / 100
        b["cancelled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        shop["bookings"].remove(b)
        shop.setdefault("cancelled", []).append(b)
        save(d)
        try:
            notify("Booking CANCELLED at " + shop["name"], b.get("name", "") + " - " + b.get("service", "") + " - " + b.get("when", "") + " - refunded $" + amt_s, shop.get("email") or GMAIL)
        except Exception:
            pass
        return S + "<h1>Booking cancelled</h1><p>You'll be refunded $" + amt_s + ". It can take 5 to 10 business days to show on your card.</p><a href='/b/" + sid + "'>Back</a>"
    sl = [(v, lab) for v, lab in build_slots(shop) if v != b.get("when")]
    if request.method == "POST" and request.form.get("act") == "resched":
        nw = request.form.get("when", "")
        if nw not in [v for v, _ in sl]:
            return S + head + "<p>That time isn't available anymore. Please pick another.</p><a href='/m/" + sid + "/" + rt + "'>Back</a>"
        old = b.get("when", "")
        b["when"] = nw
        save(d)
        try:
            notify("Booking RESCHEDULED at " + shop["name"], b.get("name", "") + " - " + b.get("service", "") + " - moved from " + old + " to " + nw, shop.get("email") or GMAIL)
        except Exception:
            pass
        return S + "<h1>Rescheduled!</h1><p>Your new time: " + str(escape(nw)) + "</p><p>No extra charge.</p><a href='/m/" + sid + "/" + rt + "'>View booking</a>"
    if sl:
        resched = "<h3>Reschedule (free)</h3><form method='post'><input type='hidden' name='act' value='resched'><select name='when' required>" + "".join("<option value='" + str(escape(v)) + "'>" + str(escape(lab)) + "</option>" for v, lab in sl) + "</select><button>Move my appointment</button></form><h3>Cancel</h3>"
    else:
        resched = "<p>No other open times right now to reschedule into.</p>"
    cancel = "<form method='post' data-m='Cancel this booking? You will be refunded $" + amt_s + ".' onsubmit='return confirm(this.dataset.m)'><input type='hidden' name='act' value='cancel'><button style='background:#d33'>Cancel booking (refund $" + amt_s + ")</button></form>"
    return S + head + resched + "<p style='font-size:14px'>Cancelling refunds everything except the processing fee (card fees + 3.7% service fee).</p>" + cancel


@app.route("/r/<sid>/<rt>", methods=["GET", "POST"])
def leave_review(sid, rt):
    from datetime import datetime, timedelta
    d = load()
    if sid not in d:
        return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    bk = [b for b in shop["bookings"] if b.get("rt") == rt]
    if not rt or not bk:
        return S + "<h1>Review link not found</h1>", 404
    b = bk[0]
    name = str(escape(shop["name"]))
    if b.get("reviewed"):
        return S + "<h1>Thanks!</h1><p>You already reviewed " + name + ".</p><a href='/b/" + sid + "'>Back</a>"
    now = datetime.utcnow() - timedelta(hours=10)
    try:
        appt = datetime.fromisoformat(str(b.get("when", ""))[:16])
    except Exception:
        appt = None
    if appt and now < appt:
        return S + "<h1>Almost!</h1><p>You can leave a review after your appointment (" + str(escape(b["when"])) + "). Save this link and come back then.</p><a href='/b/" + sid + "'>Back</a>"
    if request.method == "POST":
        try:
            st = int(request.form.get("stars", "0"))
        except ValueError:
            st = 0
        if st < 1 or st > 5:
            return S + "<h1>Please pick 1 to 5 stars</h1><a href='/r/" + sid + "/" + rt + "'>Back</a>"
        first = (b.get("name", "") or "Customer").split()[0]
        txt = request.form.get("text", "")[:500]
        shop.setdefault("reviews", []).append({"stars": st, "text": txt, "name": first, "service": b.get("service", "")})
        b["reviewed"] = True
        save(d)
        notify("New " + str(st) + "-star review for " + shop["name"], first + ": " + txt, shop.get("email") or GMAIL)
        return S + "<h1>Thanks for your review!</h1><p>It's now on " + name + "'s page.</p><a href='/b/" + sid + "'>See it</a>"
    stars = "".join("<label style='font-size:24px;margin-right:8px'><input type='radio' name='stars' value='" + str(i) + "' required> " + str(i) + "&#9733;</label>" for i in range(1, 6))
    return S + "<h1>Review " + name + "</h1><p>How was your " + str(escape(b.get("service", ""))) + "?</p><form method='post'>" + stars + "<textarea name='text' rows='4' style='width:100%' placeholder='Tell others about your visit (optional)'></textarea><button>Submit review</button></form>"


@app.route("/done/<sid>")
def setup_done(sid):
    from urllib.parse import quote
    d = load()
    if sid not in d:
        return S + "<h1>Not found</h1>", 404
    dl = "/d/" + sid + "?pw=" + quote(request.args.get("pw", ""))
    b1 = "display:block;background:#1a6dff;color:#fff;padding:14px;border-radius:12px;text-decoration:none;text-align:center;margin:12px 0;font-weight:700"
    b2 = "display:block;border:2px solid #1a6dff;color:#1a6dff;padding:12px;border-radius:12px;text-decoration:none;text-align:center;margin:12px 0;font-weight:700"
    return S + "<h1>You're all set!</h1><p><b>" + str(escape(d[sid]["name"])) + "</b> is ready. Check your email and tap the confirm link to go live.</p><a style='" + b1 + "' href='" + dl + "'>Go to my dashboard</a><a style='" + b2 + "' href='/b/" + sid + "'>See my booking page</a><a style='" + b2 + "' href='/'>Back to home</a>"


def _bb_save(d):
    open(DB, "w").write(__import__("json").dumps(d, indent=2))

def _bb_err(e):
    return S + "<h1>Stripe error</h1><p>" + str(__import__("markupsafe").escape(str(e)[:300])) + "</p>", 500

@app.route("/connect/<sid>")
def connect_start(sid):
    import stripe
    from urllib.parse import quote
    d = load()
    if sid not in d: return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    pw = request.args.get("pw", "")
    if not _bb_ok(sid, pw, shop):
        return S + "<h1>Wrong password</h1>", 403
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key: return S + "<h1>Payments not set up yet</h1>", 500
    stripe.api_key = key
    try:
        acct = shop.get("acct")
        if not acct:
            kw = {"type": "express", "metadata": {"sid": sid},
                  "capabilities": {"card_payments": {"requested": True}, "transfers": {"requested": True}}}
            if shop.get("email"): kw["email"] = shop["email"]
            acct = _v2("POST", "/v2/core/accounts", _v2_body(shop, sid))["id"]
            shop["acct"] = acct
            _bb_save(d)
        base = request.host_url.rstrip("/")
        q = "?pw=" + quote(pw)
        link = _v2_link(acct,
            refresh_url=base + "/connect/" + sid + q, return_url=base + "/connected/" + sid + q)
    except Exception as e:
        return _bb_err(e)
    return redirect(link.url)

@app.route("/connected/<sid>")
def connect_back(sid):
    import stripe
    from urllib.parse import quote
    d = load()
    if sid not in d: return S + "<h1>Not found</h1>", 404
    shop = d[sid]
    pw = request.args.get("pw", "")
    if not _bb_ok(sid, pw, shop):
        return S + "<h1>Wrong password</h1>", 403
    dl = "/d/" + sid + "?pw=" + quote(pw)
    if not shop.get("acct"): return redirect(dl)
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    try:
        a = _v2("GET", "/v2/core/accounts/" + shop["acct"] + "?include=configuration.recipient")
    except Exception as e:
        return _bb_err(e)
    on = _v2_on(a)
    shop["payouts_on"] = on
    _bb_save(d)
    if on:
        msg = "<h1>You're connected!</h1><p>Customer payments will now go to your bank.</p>"
    else:
        msg = "<h1>Almost there</h1><p>Stripe still needs a bit more info, or is reviewing it. You can finish from your dashboard.</p>"
    return S + msg + "<p><a href='" + dl + "'>Back to my dashboard</a></p>"


BB_CUT = 0.037
def _bb_pi(shop, fee):
    acct = shop.get("acct")
    if not (acct and shop.get("payouts_on")):
        return {}
    cents = int(round(float(fee) * 100))
    stripe_fee = int(round(cents * 0.029)) + 30
    app_fee = min(cents, int(round(cents * BB_CUT)) + stripe_fee)
    return {"payment_intent_data": {"application_fee_amount": app_fee,
            "transfer_data": {"destination": acct}}}


BB_STRIPE_VER = "2026-09-30.endive"
def _v2(method, path, body=None):
    import urllib.request, urllib.error, json as _j
    req = urllib.request.Request("https://api.stripe.com" + path, method=method,
        data=_j.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", "Bearer " + os.environ.get("STRIPE_SECRET_KEY", ""))
    req.add_header("Stripe-Version", BB_STRIPE_VER)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return _j.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = _j.loads(e.read().decode()).get("error", {})
            msg = str(err.get("code", "")) + ": " + str(err.get("message", ""))
        except Exception:
            msg = "HTTP " + str(e.code)
        raise RuntimeError(msg)

def _v2_body(shop, sid):
    b = {"display_name": shop.get("name", sid),
         "identity": {"country": "us"},
         "dashboard": "express",
         "defaults": {"responsibilities": {"fees_collector": "application", "losses_collector": "application"}},
         "configuration": {"recipient": {"capabilities": {"stripe_balance": {"stripe_transfers": {"requested": True}}}}},
         "metadata": {"sid": sid}}
    if shop.get("email"):
        b["contact_email"] = shop["email"]
    return b

def _v2_link(acct, refresh_url, return_url):
    from types import SimpleNamespace
    r = _v2("POST", "/v2/core/account_links", {"account": acct, "use_case": {
        "type": "account_onboarding",
        "account_onboarding": {"refresh_url": refresh_url, "return_url": return_url}}})
    return SimpleNamespace(url=r["url"])

def _v2_on(a):
    try:
        st = a["configuration"]["recipient"]["capabilities"]["stripe_balance"]["stripe_transfers"]["status"]
    except Exception:
        return False
    return st == "active"

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
