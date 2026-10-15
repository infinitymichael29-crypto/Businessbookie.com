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
    taken=_bb_full(shop)
    labels=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    out=[]
    today=(datetime.utcnow() - timedelta(hours=10))
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
 "Barber": {"Haircut": 20, "Skin fade": 25, "Beard trim": 15, "Haircut + beard": 35, "Kids cut": 15},
 "Cleaning": {"Standard clean (deposit)": 50, "Deep clean (deposit)": 100, "Move-out clean (deposit)": 150, "Free estimate": 0},
 "Hair salon": {"Women's haircut": 30, "Men's haircut": 25, "Blowout": 25, "Color (deposit)": 60, "Treatment": 40, "Free consultation": 0},
 "Lashes and brows": {"Classic lash set": 50, "Lash fill": 30, "Brow shape": 15, "Brow tint": 15},
 "Massage": {"30 min massage": 30, "60 min massage": 50, "90 min massage": 70},
 "Nails": {"Manicure": 20, "Gel manicure": 30, "Pedicure": 30, "Full set": 40, "Fill": 25},
 "Personal trainer": {"30 min session": 15, "60 min session": 25, "Free consultation": 0},
 "Photography": {"Mini session (deposit)": 50, "Full session (deposit)": 100, "Event (deposit)": 200},
 "Restaurant": {"Table reservation": 0},
 "Tattoo": {"Free consultation": 0, "Small tattoo (deposit)": 50, "Medium piece (deposit)": 100, "Large piece (deposit)": 200},
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
<div class='cal'><svg width='96' height='96' viewBox='0 0 100 100' role='img' aria-label='Business-Bookie logo'><rect width='100' height='100' rx='22' fill='#ffffff'/><g transform='translate(17 16) scale(0.66)'><rect x='10' y='18' width='80' height='76' rx='16' fill='#1a6dff'/><rect x='28' y='6' width='10' height='24' rx='5' fill='#0b1f4d'/><rect x='62' y='6' width='10' height='24' rx='5' fill='#0b1f4d'/><text x='50' y='80' text-anchor='middle' font-family='Sora, Segoe UI, Arial, sans-serif' font-weight='800' font-size='54' fill='#ffffff'>B</text></g></svg></div>
<div class="logo">Business-Bookie</div>
<div class="head">Sign up your business for free</div>
<div class="sub">Your own booking page in minutes.</div>
<div style='margin:18px 0 6px'><div style='color:#fff;font-size:15px;margin:6px 0 8px'>For customers</div><a href='/find' style='display:block;box-sizing:border-box;width:100%;max-width:340px;margin:0 auto 14px;padding:14px;background:#fff;color:#1a6dff;border:2px solid #1a6dff;border-radius:14px;font-weight:800;font-size:18px;text-decoration:none;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.15)'>&#128197; Book an appointment</a><div style='color:#fff;font-size:15px;margin:6px 0 8px'>New to Business-Bookie?</div><a href='/new' style='display:block;box-sizing:border-box;width:100%;max-width:340px;margin:0 auto 14px;padding:14px;background:#fff;color:#1a6dff;border:2px solid #1a6dff;border-radius:14px;font-weight:800;font-size:18px;text-decoration:none;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.15)'>&#127970; Sign up my business</a><div style='color:#fff;font-size:15px;margin:6px 0 8px'>Already have a business?</div><a href='/login' style='display:block;box-sizing:border-box;width:100%;max-width:340px;margin:0 auto 14px;padding:14px;background:#fff;color:#1a6dff;border:2px solid #1a6dff;border-radius:14px;font-weight:800;font-size:18px;text-decoration:none;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.15)'>&#128273; Log in to check bookings</a></div>
<div class="benes">&#9989; Your own booking link<br>&#9989; Get paid up front<br>&#9989; No more DMs</div>
<div class="trust">Free business signup &middot; No credit card needed</div><div style='margin-top:10px;font-size:13px'><a href='/privacy' style='color:#fff'>Privacy Policy</a> &middot; <a href='/terms' style='color:#fff'>Terms</a></div><div style='margin-top:14px'></div>
</div>
<p style='text-align:center;font-size:15px;margin:4px 0 20px'><a href='/qrcode' style='color:#fff;text-decoration:underline;font-weight:bold'>&#128241; Get our QR code</a></p></body></html>
""")


@app.route("/new")
def new():
    opts = "".join(f"<option>{t}</option>" for t in TEMPLATES)
    return S + f"""<h1>Set up your business</h1>
<form method='post' action='/setup'>
<input name='shop' placeholder='Business name' required>{_bb_owner_input()}
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
<input name='addr' placeholder='Business address'><input name='bphone' type='tel' placeholder='Business phone (customers can call)' required><label style='display:flex;gap:10px;align-items:flex-start;font-size:13px;color:#334;margin:6px 0 10px;line-height:1.4'><input type='checkbox' name='owner_sms' value='1' style='width:auto;margin:3px 0 0;flex:none'><span>Yes, text me new-booking and cancellation alerts from Business-Bookie at this number. Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out, HELP for help. Optional. <a href='/privacy'>Privacy Policy</a> &middot; <a href='/terms'>Terms</a></span></label>{_bb_acct_inputs()}<textarea name='custom' rows='3' placeholder='Deluxe package | 40'></textarea>
<input type='hidden' name='lat' id='glat'><input type='hidden' name='lng' id='glng'><button type='button' onclick='navigator.geolocation.getCurrentPosition(p=>(glat.value=p.coords.latitude,glng.value=p.coords.longitude,this.innerText="Location saved"))'>Use my location</button><p><b>Days you're open:</b></p><label style='margin-right:10px'><input type='checkbox' name='days' value='0' checked style='width:auto'> Mon</label><label style='margin-right:10px'><input type='checkbox' name='days' value='1' checked style='width:auto'> Tue</label><label style='margin-right:10px'><input type='checkbox' name='days' value='2' checked style='width:auto'> Wed</label><label style='margin-right:10px'><input type='checkbox' name='days' value='3' checked style='width:auto'> Thu</label><label style='margin-right:10px'><input type='checkbox' name='days' value='4' checked style='width:auto'> Fri</label><label style='margin-right:10px'><input type='checkbox' name='days' value='5'  style='width:auto'> Sat</label><label style='margin-right:10px'><input type='checkbox' name='days' value='6'  style='width:auto'> Sun</label><p>Opening time</p><input type='time' name='open' value='09:00'><p>Closing time</p><input type='time' name='close' value='17:00'><p>Appointment length</p><select name='slot'><option value='30'>30 minutes</option><option value='60'>1 hour</option><option value='90'>90 minutes</option><option value='120'>2 hours</option></select><button>Create my booking page</button></form>"""
@app.route("/create", methods=["POST"])
def create():
    if request.form.get("use_acct") == "1":
        _me = _bb_me()
        if not _me:
            return S + "<h1>Please log in again</h1><a href='/login'>Log in</a>"
        from werkzeug.datastructures import ImmutableMultiDict
        _f = request.form.to_dict(flat=False)
        _f["email"] = [_me["email"]]
        _f["pw"] = [_me["pw"]]
        _f["pw2"] = [_me["pw"]]
        request.form = ImmutableMultiDict([(k, v) for k, vs in _f.items() for v in vs])
    if request.form.get("pw2") is not None and request.form.get("pw2") != request.form.get("pw", ""):
        return S + "<h1>Passwords don't match</h1><p>Go back and type the same password in both boxes.</p><a href='javascript:history.back()'>Go back</a>"
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
    d[sid] = {"live": bool(request.form.get("use_acct") == "1"), "token": tok, "name": request.form["shop"], "owner": request.form.get("owner", ""), "bphone": request.form.get("bphone", "").strip()[:30], "owner_sms": request.form.get("owner_sms") == "1", "addr": request.form.get("addr",""), "email": request.form.get("email",""), "pw": request.form.get("pw",""), "lat": request.form.get("lat",""), "lng": request.form.get("lng",""), "type": request.form.get("btype","Other"), "type": request.form.get("btype","Other"), "services": svc, "days": request.form.getlist("days"), "open": request.form.get("open","09:00"), "close": request.form.get("close","17:00"), "slot": request.form.get("slot","30"), "bookings": []}
    save(d)
    notify("New business signed up", request.form["shop"])
    notify("Confirm your business on Business-Bookie", "Tap to confirm and go live: " + request.host_url + "confirm/" + sid + "/" + tok + "\n\nYour QR code to print, customers scan it to book: " + request.host_url + "qr/" + sid, request.form["email"])
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
    return S + f"""<h1>{escape(shop['name'])}</h1>{ow}<p>Location: {escape(shop.get('addr',''))}</p>{_bb_phone_html(shop)}{revs}{prices}<p>Book an appointment</p>
<form method='post' action='/book/{sid}'>
<input name='name' placeholder='Your name' required>
<input name='phone' placeholder='Phone number' required>{_bb_guests_sel(shop)}{_bb_fee_box(shop)}<label style='display:flex;gap:10px;align-items:flex-start;font-size:13px;color:#334;margin:6px 0 10px;line-height:1.4'><input type='checkbox' name='sms_ok' value='1' style='width:auto;margin:3px 0 0;flex:none'><span>Yes, text me appointment confirmations, reminders and cancellation notices from Business-Bookie at this number. Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out, HELP for help. Consent is not a condition of booking. <a href='/privacy'>Privacy Policy</a> &middot; <a href='/terms'>Terms</a></span></label>
<input name='email' type='email' placeholder='Email (we send your booking link)' required>
<select name='service'>{opts}</select>
{slots}
<div style='background:#fff6e5;border:1px solid #f0c36d;border-radius:10px;padding:12px;margin:12px 0;font-size:14px'><b>Cancellation &amp; no-show terms</b><br>You pay in full now to hold your spot. You can <b>reschedule with the owner</b>. If you <b>cancel</b>, you get a refund minus a small processing fee (card fees + 3.7% service fee).<br><b>No-shows:</b> if you miss your appointment without cancelling, your payment is non-refundable.</div>
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
    fee = _bb_gross(_bb_party_fee(shop, fee))
    if request.form.get("when", "") in _bb_full(shop) or _bb_blocked(shop, request.form.get("when", "")):
        return _bb_taken(sid, shop)
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
                metadata={"sid": sid, "name": request.form["name"], "phone": request.form["phone"], "sms": request.form.get("sms_ok", ""), "service": s, "when": request.form["when"], "email": request.form.get("email", "")[:200]},
                success_url=base + "/paid/" + sid + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=base + "/b/" + sid)
        except Exception as ex:
            return _bb_payerr(d, sid, shop, ex)
        return redirect(cs.url, code=303)
    rt = secrets.token_urlsafe(8)
    shop["bookings"].append({"name": request.form["name"], "phone": request.form["phone"], "sms": request.form.get("sms_ok") == "1", "service": s, "when": request.form["when"], "fee": fee, "rt": rt, "email": request.form.get("email", "")})
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
    hrs = _bb_hours_text(shop)
    ref = "<meta http-equiv='refresh' content='30;url=/d/" + sid + "?pw=" + quote(pw) + "'>"
    head = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;font-family:system-ui,Arial;background:#eef3ff}.top{background:#1a6dff;color:#fff;padding:22px 18px}.top h1{margin:0;font-size:26px}.top p{margin:4px 0 0;opacity:.9}.wrap{padding:16px;max-width:460px;margin:auto}.card{background:#fff;padding:16px;border-radius:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08)}.big{font-size:34px;font-weight:800;color:#1a6dff}a{color:#1a6dff}.note{background:#fff3cd}</style>"
    note = "" if shop.get("live", True) else "<div class='card note'><b>&#9888; Confirm your email to go live.</b> Your business won't show in the directory until you tap the link we emailed you. Check spam too.<br><a href='/resend/" + sid + "' style='display:inline-block;margin-top:8px;font-weight:700'>Resend confirm link</a></div>"
    if not shop.get("payouts_on"): note += "<div class='card note'><b>&#9888; Connect payments to go live.</b> Customers can't find or book you in the directory until payments are set up. Use the Connect payments button below.</div>"
    for _x in shop.get("dbl", []): note += "<div class='card' style='background:#fde8e8;border-left:6px solid #e23b3b'><b>&#9888; Double-booking caught</b><br>" + escape(_x.get("name", "")) + " tried to book " + escape(_x.get("service", "")) + " at " + escape(_x.get("when", "")) + ", a time already taken. They were refunded in full, so you are <b>not</b> double-booked.<br><a href='/dbl/" + sid + "' style='display:inline-block;margin-top:8px;font-weight:700;color:#e23b3b'>Got it, dismiss</a></div>"
    if bk:
        rows = "".join("<div class='card'><b>" + escape(x['name']) + "</b> - " + escape(x['service']) + "<br>" + escape(x['when']) + "<br>" + escape(x['phone']) + " - fee $" + str(x.get('fee', x.get('deposit', 0))) + "</div>" for x in reversed(bk))
    else:
        rows = "<div class='card'>No bookings yet. Share your link to get your first one!</div>"
    _now = datetime.utcnow() - timedelta(hours=10)
    _due = []
    for x in bk:
        try: _t = datetime.strptime(x.get("when", ""), "%Y-%m-%d %H:%M")
        except Exception: continue
        if _t <= _now and x.get("rt") and not x.get("done"):
            _due.append(x)
    _up, _dn = [], [x for x in bk if x.get("done")]
    for x in bk:
        if x.get("done") or x in _due: continue
        try: _t = datetime.strptime(x.get("when", ""), "%Y-%m-%d %H:%M")
        except Exception: _t = None
        if _t is None or _t > _now: _up.append(x)
        else: _dn.append(x)
    _up.sort(key=lambda x: x.get("when", ""))
    _dn.sort(key=lambda x: x.get("when", ""), reverse=True)
    _ns = list(reversed(shop.get("noshows", [])))
    def _card(x, extra="", clr="#1a6dff"):
        ph = str(x.get("phone", "")); em = str(x.get("email", ""))
        try: fee = "%.2f" % float(x.get("fee", x.get("deposit", 0)) or 0)
        except Exception: fee = str(x.get("fee", ""))
        c = "<div class='card' style='border-left:6px solid " + clr + "'><b>" + escape(x.get("name", "")) + "</b><br>" + escape(x.get("service", "")) + " &middot; " + escape(x.get("when", ""))
        if x.get("moved_from"): c += "<br><b style='color:#e08a00'>&#128260; Moved by customer</b> (was " + escape(x["moved_from"]) + ")"
        if ph: c += "<br>&#128222; <a href='tel:" + escape(ph) + "'>" + escape(ph) + "</a>"
        if em: c += "<br>&#9993; <a href='mailto:" + escape(em) + "'>" + escape(em) + "</a>"
        return c + "<br>Fee: $" + fee + extra + "</div>"
    def _sec(title, items, empty, extra=lambda x: "", clr="#1a6dff"):
        return "<h3 style='color:" + clr + "'>" + title + " (" + str(len(items)) + ")</h3>" + ("".join(_card(x, extra(x), clr) for x in items) if items else "<div class='card' style='color:#777'>" + empty + "</div>")
    _btn = lambda x: "<form method='post' action='/ns/" + sid + "/" + x["rt"] + "' style='margin-top:8px'><button name='a' value='showed'>Showed up &#10003;</button> <button name='a' value='noshow' onclick=\"return confirm('Mark as no-show? They will NOT get a refund.')\">Mark no-show</button></form><a href='/ns/" + sid + "/" + x["rt"] + "'>Reschedule</a>"
    rows = ""
    toprows = ""
    if _due: toprows += _sec("&#9888; Did they show up?", _due, "", _btn, "#f0a500")
    rows += _sec("Upcoming", _up, "No upcoming appointments.", clr="#1a6dff")
    rows += _sec("Completed", _dn, "None yet.", clr="#1faa59")
    rows += _sec("No-shows", _ns, "None. Nice!", clr="#e23b3b")
    acct = shop.get("acct", "")
    pq = "?pw=" + quote(pw)
    cb = "display:block;text-align:center;background:#1a6dff;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:700;margin-top:10px"
    if shop.get("payouts_on"):
        pay = "<div class='card'><b>&#9989; Payments on</b><br>Customer payments go to your bank.</div>"
    elif acct:
        pay = "<div class='card note'><b>Payment setup not finished</b><a style='" + cb + "' href='/connect/" + sid + pq + "'>Finish payment setup</a></div>"
    else:
        pay = "<div class='card'><b>Get paid online</b><br>Connect your bank so customers can pay when they book. Takes a few minutes.<a style='" + cb + "' href='/connect/" + sid + pq + "'>Connect payments</a></div>"
    body = ref + head + "<div class='top' style='text-align:center;position:relative;padding-top:56px'><a href='/mine?em=" + quote(shop.get('email','')) + "' style='position:absolute;top:14px;left:14px;background:#fff;color:#1a6dff;font-weight:700;text-decoration:none;padding:8px 14px;border-radius:8px'>&#127970; All my businesses</a><h1>" + escape(shop['name']) + "</h1></div><div class='wrap'>" + note + toprows + "<h3>Upcoming</h3>" + _bb_uptiles(_up) + "<h3>&#128197; This month</h3>" + _bb_month(shop, sid) + "<div class='card'><div class='big'>" + str(len(bk)) + "</div>total bookings</div><div class='card'><b>Your booking link</b><br><a href='/b/" + sid + "'>" + escape(link) + "</a><br><button onclick=\"if(navigator.share){navigator.share({title:'Book with us',url:'" + link + "'})}else{navigator.clipboard.writeText('" + link + "');this.innerText='Copied!'}\" style='margin-top:10px'>Share link</button></div><div class='card'><b>Open:</b> " + escape(hrs) + "</div><div class='card' style='display:flex;gap:10px;flex-wrap:wrap'><a href='/edit/" + sid + "' style='flex:1;min-width:40%;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700'>&#9999;&#65039; Edit customer booking page</a><a href='/block/" + sid + "' style='flex:1;min-width:40%;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700'>&#9940; Block off time</a><a href='/del/" + sid + "' style='flex-basis:100%;text-align:center;border:2px solid #e23b3b;color:#e23b3b;padding:10px;border-radius:10px;text-decoration:none;font-weight:700;margin-top:6px'>Delete business</a></div>" + pay + rows + "<div class='card'><a href='/pw/" + sid + "'>Change password</a> | <a href='/logout'>Log out</a></div></div>"
    return body.replace("<", chr(60)).replace(">", chr(62))

import smtplib
from email.message import EmailMessage
GMAIL = "infinitymichael29@gmail.com"
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
def notify(subject, body, to=None):
    rk = os.environ.get("RESEND_API_KEY")
    if rk:
        try:
            import json as _j, urllib.request as _u
            dt = _j.dumps({"from": "Business-Bookie <bookings@business-bookie.com>", "to": [to or GMAIL], "subject": subject, "text": body}).encode()
            rq = _u.Request("https://api.resend.com/emails", data=dt, headers={"Authorization": "Bearer " + rk, "Content-Type": "application/json", "User-Agent": "BusinessBookie/1.0"})
            _u.urlopen(rq, timeout=20).read()
        except Exception as e:
            print("resend failed:", e)
        return
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
    rows = "".join(f"<a href='/b/{sid}' style='text-decoration:none'><div class='card'><b>{escape(v['name'])}</b><br>{escape(v.get('addr',''))}</div></a>" for sid, v in d.items() if v.get("type", "Other") == cat and _bb_listed(v))
    return S + f"<h1>{escape(cat)}</h1>" + (rows or "<p>None yet.</p>") + "<a href='/'>Back</a>"
@app.route("/confirm/<sid>/<tok>")
def confirm(sid, tok):
    d = load()
    if sid in d and d[sid].get("token") == tok:
        d[sid]["live"] = True
        save(d)
        b1 = "display:block;background:#1a6dff;color:#fff;padding:14px;border-radius:12px;text-decoration:none;text-align:center;margin:12px 0;font-weight:700"
        b2 = "display:block;border:2px solid #1a6dff;color:#1a6dff;padding:12px;border-radius:12px;text-decoration:none;text-align:center;margin:12px 0;font-weight:700"
        return "<meta http-equiv='refresh' content='4;url=/d/" + sid + "'>" + S + "<h1>&#127881; You're live!</h1><p><b>" + str(escape(d[sid].get("name", ""))) + "</b> is confirmed! " + ("It now shows in the Business-Bookie directory." if d[sid].get("payouts_on") else "Last step: connect payments on your dashboard so customers can find and book you.") + "</p><p>Taking you to your dashboard...</p><a style='" + b1 + "' href='/d/" + sid + "'>Go to my dashboard</a><a style='" + b2 + "' href='/b/" + sid + "'>See my booking page</a>"
    return S + "<h1>Link not valid</h1>", 404
@app.route("/find")
def find():
    from urllib.parse import quote
    d = load()
    counts = {}
    for v in d.values():
        if not _bb_listed(v): continue
        k = v.get("type", "Other")
        counts[k] = counts.get(k, 0) + 1
    cats = "".join(f"<a href='/c/{quote(k)}' style='text-decoration:none'><div class='card'><b>{escape(k)}</b> - {n} businesses</div></a>" for k, n in [(k, counts.get(k, 0)) for k in TEMPLATES])
    return S + "<h1>Find a business</h1><form action='/search'><input name='q' placeholder='Search by name or type'><button>Search</button></form><button onclick='navigator.geolocation.getCurrentPosition(p=>location.href=`/near?lat=${p.coords.latitude}&lng=${p.coords.longitude}`)'>Businesses near me</button><p>Or browse by category:</p>" + (cats or "<p>No businesses yet.</p>") + "<a href='/'>Back</a>"
@app.route("/search")
def search():
    d = load()
    q = request.args.get("q", "").lower()
    rows = "".join(f"<a href='/b/{sid}' style='text-decoration:none'><div class='card'><b>{escape(v['name'])}</b><br>{escape(v.get('type',''))} - {escape(v.get('addr',''))}</div></a>" for sid, v in d.items() if _bb_listed(v) and (q in v['name'].lower() or q in v.get('type','').lower()))
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
        if not _bb_listed(v): continue
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
            if v.get("email") == em and _bb_pw_ok(v.get("pw"), pw):
                for _k, _v in d.items():
                    if _v.get("email") == em and _bb_pw_ok(_v.get("pw"), pw): _bb_sess["own_" + _k] = True
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
    owned = [(sid, v) for sid, v in d.items() if em and v.get("email") == em and (pw and _bb_pw_ok(v.get("pw"), pw) or _bb_sess.get("own_" + sid))]
    if not owned: return redirect("/login")
    head = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;font-family:system-ui,Arial;background:#eef3ff}.top{background:#1a6dff;color:#fff;padding:22px 18px}.top h1{margin:0;font-size:26px}.wrap{padding:16px;max-width:460px;margin:auto}.card{display:block;background:#fff;padding:16px;border-radius:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);color:#123;text-decoration:none}a{color:#1a6dff}</style>"
    _now = (datetime.utcnow() - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M")
    _bs = "flex:1;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:8px;border-radius:8px;text-decoration:none;font-weight:700"
    _num = "font-size:26px;font-weight:800;color:#1a6dff"
    def _card(sid, v):
        bk = v.get("bookings", [])
        up = len([b for b in bk if str(b.get("when", "")) >= _now])
        ok = _bb_listed(v)
        tag = "<span style='color:#1faa59;font-weight:700'>&#9679; Live</span>" if ok else ("<span style='color:#b37400;font-weight:700'>&#9888; Needs email confirmation</span>" if not v.get("live", True) else "<span style='color:#b37400;font-weight:700'>&#9888; Needs payments connected</span>")
        return "<div class='card' style='border-left:6px solid " + ("#1faa59" if ok else "#f0a500;background:#fff8e1") + "'><b style='font-size:18px'>" + escape(v.get("name", "")) + "</b> " + tag + "<br><span style='color:#667'>" + escape(v.get("type", "")) + "</span><div style='display:flex;gap:24px;margin:10px 0'><div><div style='" + _num + "'>" + str(up) + "</div>upcoming</div><div><div style='" + _num + "'>" + str(len(bk)) + "</div>total bookings</div></div><div style='display:flex;gap:8px'><a style='" + _bs + "' href='/d/" + sid + "?pw=" + quote(pw) + "'>Open</a></div></div>"
    rows = "".join(_card(sid, v) for sid, v in owned)
    _tu = sum(len([b for b in v.get("bookings", []) if str(b.get("when", "")) >= _now]) for _, v in owned)
    _tb = sum(len(v.get("bookings", [])) for _, v in owned)
    summ = "<div class='card' style='display:flex;justify-content:space-around;text-align:center'><div><div style='" + _num + "'>" + str(len(owned)) + "</div>businesses</div><div><div style='" + _num + "'>" + str(_tu) + "</div>upcoming</div><div><div style='" + _num + "'>" + str(_tb) + "</div>total bookings</div></div>"
    return head + "<div class='top' style='text-align:center'><h1>My businesses</h1></div><div class='wrap'>" + summ + rows + "<div style='display:flex;gap:10px;margin-top:12px'><a href='/new' style='flex:1;text-align:center;background:#1a6dff;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:700'>+ Add another business</a><a href='/find' style='flex:1;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700'>&#128269; Find a business</a></div><p style='text-align:center'><a href='/logout'>Log out</a></p></div>"


import os, secrets as _bb_secrets
from flask import session as _bb_sess
app.secret_key = os.environ.get("SECRET_KEY") or app.secret_key or _bb_secrets.token_hex(32)

def _bb_ok(sid, pw, shop):
    if _bb_sess.get("own_" + sid):
        return True
    if pw and (_bb_pw_ok(shop.get("pw"), pw) if shop.get("pw") else pw == DASH_PASS):
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
        if not _bb_pw_ok(d[sid].get("pw"), old):
            return S + "<h1>Current password is wrong</h1><a href='/pw/" + sid + "'>Try again</a>"
        if len(new) < 6 or new != request.form.get("new2", ""):
            return S + "<h1>New passwords must match and be at least 6 characters</h1><a href='/pw/" + sid + "'>Try again</a>"
        em = d[sid].get("email")
        for k, v in d.items():
            if v.get("email") == em and _bb_pw_ok(v.get("pw"), old):
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
                notify("Business-Bookie - reset your password", "Tap this link to set a new password (works for 1 hour):\n\n" + link, to=em)
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
    if not ex and m.get("when") in _bb_full(shop):
        try:
            import stripe as _s
            _s.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            kw = {"payment_intent": _bb_g(info, "payment_intent")}
            if shop.get("acct") and shop.get("payouts_on"):
                kw["reverse_transfer"] = True
                kw["refund_application_fee"] = True
            _s.Refund.create(**kw)
        except Exception as e:
            print("double-book refund failed:", e)
        shop.setdefault("dbl", []).append({"name": m.get("name", ""), "service": m.get("service", ""), "when": m.get("when", "")})
        save(d)
        return S + "<h1>Sorry, that time was just taken</h1><p>Someone booked it a moment before you. You've been refunded in full. It can take 5 to 10 business days to show on your card.</p><a href='/b/" + sid + "'>Pick another time</a>"
    if not ex:
        shop["bookings"].append({"name": m["name"], "phone": m["phone"], "sms": m.get("sms") == "1", "service": m["service"], "when": m["when"], "fee": fee, "paid": True, "paid_id": info["id"], "rt": rt, "email": m.get("email", ""), "pi": _bb_g(info, "payment_intent"), "keep": (_bb_pi(shop, fee).get("payment_intent_data") or {}).get("application_fee_amount")})
        save(d)
        notify("New PAID booking at " + shop["name"], m["name"] + " - " + m["service"] + " - " + m["when"] + " - " + m["phone"] + " - paid $" + ("%.2f" % fee), shop.get("email") or GMAIL)
        if m.get("email"):
            ml = request.host_url + "m/" + sid + "/" + rt
            notify("Your booking at " + shop["name"], "You're booked and paid!\n\n" + m["service"] + " at " + shop["name"] + "\nWhen: " + m["when"] + "\nPaid: $" + ("%.2f" % fee) + "\n\nNeed to cancel or reschedule? Use this link:\n" + ml + "\n\nTo reschedule, work it out with the business owner. If you cancel, you get a refund minus a small processing fee (card fees + 3.7% service fee). If you miss your appointment without cancelling, your payment is non-refundable.", m["email"])
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
        started = datetime.strptime(b.get("when", ""), "%Y-%m-%d %H:%M") <= (datetime.utcnow() - timedelta(hours=10))
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
        b["cancelled_at"] = (datetime.utcnow() - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M")
        shop["bookings"].remove(b)
        shop.setdefault("cancelled", []).append(b)
        save(d)
        try:
            notify("Booking CANCELLED at " + shop["name"], b.get("name", "") + " - " + b.get("service", "") + " - " + b.get("when", "") + " - refunded $" + amt_s, shop.get("email") or GMAIL)
            if b.get("email"):
                notify("Your booking at " + shop["name"] + " is cancelled", "Hi " + b.get("name", "") + ",\n\nYour " + b.get("service", "") + " at " + shop["name"] + " on " + b.get("when", "") + " has been cancelled.\n\nRefund: $" + amt_s + ". It can take 5 to 10 business days to show on your card.\n\nWant to book again? " + request.host_url + "b/" + sid, b["email"])
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
        b["moved_from"] = old
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


@app.route("/ns/<sid>/<rt>", methods=["GET", "POST"])
def _bb_noshow(sid, rt):
    d = load()
    shop = d.get(sid)
    if not shop or not _bb_ok(sid, "", shop):
        return redirect("/d/" + sid)
    b = next((x for x in shop.get("bookings", []) if x.get("rt") == rt), None)
    if not b:
        return redirect("/d/" + sid)
    a = request.form.get("a", "")
    if request.method == "POST" and a == "noshow":
        shop["bookings"].remove(b)
        b["noshow_at"] = (datetime.utcnow() - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M")
        shop.setdefault("noshows", []).append(b)
        _bb_noshow_alert(shop, sid, b)
        save(d)
        return redirect("/d/" + sid)
    if request.method == "POST" and a == "showed":
        b["done"] = True
        save(d)
        return redirect("/d/" + sid)
    if request.method == "POST" and a == "move":
        w = request.form.get("when", "").replace("T", " ")[:16]
        try: datetime.strptime(w, "%Y-%m-%d %H:%M")
        except Exception: return S + "<h1>Pick a new date and time</h1><a href='/ns/" + sid + "/" + rt + "'>Back</a>"
        _e = _bb_propose(shop, sid, b, w, 'owner')
        if _e:
            return S + _e
        save(d)
        return redirect('/d/' + sid)
        if b.get("email"):
            notify("Your appointment at " + shop["name"] + " was moved", "Your " + b.get("service", "") + " at " + shop["name"] + " is now:\n" + w + "\n\nNeed to change it? Use this link:\n" + request.host_url + "m/" + sid + "/" + rt, b["email"])
        return redirect("/d/" + sid)
    return S + "<h1>Reschedule</h1><p><b>" + str(escape(b.get("name", ""))) + "</b> - " + str(escape(b.get("service", ""))) + "<br>Was: " + str(escape(b.get("when", ""))) + "</p><form method='post'><input type='hidden' name='a' value='move'><input name='when' type='datetime-local' required><button>Move appointment</button></form><a href='/d/" + sid + "'>Back to dashboard</a>"

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
    return S + "<h1>You're all set!</h1><p><b>" + str(escape(d[sid]["name"])) + "</b> is ready.</p><div style='background:#fff3cd;border:2px solid #f0a500;border-radius:12px;padding:14px;margin:12px 0'><b>&#9888; Two steps to go live:</b><br>1. Tap the confirm link we emailed from bookings@business-bookie.com (check spam).<br>2. Connect payments (tap the blue button below, takes a few minutes).<br>Customers can find and book you once both are done.</div><a style='" + b1 + "' href='/connect/" + sid + "?pw=" + quote(request.args.get("pw", "")) + "'>&#128179; Connect payments now</a><a style='" + b2 + "' href='" + dl + "'>Go to my dashboard</a><a style='" + b2 + "' href='/b/" + sid + "'>See my booking page</a><a style='" + b2 + "' href='/'>Back to home</a>"


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


_bb_fload, _bb_fsave = load, save
def _bb_db():
    import pg8000.native, ssl
    from urllib.parse import urlparse, unquote
    u = urlparse(os.environ["DATABASE_URL"])
    c = pg8000.native.Connection(user=unquote(u.username), password=unquote(u.password), host=u.hostname, port=u.port or 5432, database=u.path.lstrip("/"), ssl_context=ssl.create_default_context(), timeout=20)
    c.run("CREATE TABLE IF NOT EXISTS bb_kv (k TEXT PRIMARY KEY, v TEXT)")
    return c
def load():
    if not os.environ.get("DATABASE_URL"):
        return _bb_fload()
    c = _bb_db()
    try:
        r = c.run("SELECT v FROM bb_kv WHERE k IN (:k, 'shops') ORDER BY (k = :k) DESC LIMIT 1", k=_bb_dbkey())
    finally:
        c.close()
    if r:
        return json.loads(r[0][0])
    try:
        d = _bb_fload()
    except Exception:
        d = {}
    save(d)
    return d
def save(d):
    if not os.environ.get("DATABASE_URL"):
        return _bb_fsave(d)
    c = _bb_db()
    try:
        c.run("INSERT INTO bb_kv (k, v) VALUES (:k, :v) ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v", k=_bb_dbkey(), v=json.dumps(d))
    finally:
        c.close()


@app.route("/resend/<sid>")
def _bb_resend(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    if shop.get("live", True):
        return S + "<h1>Already confirmed</h1><p>Your business is live.</p><a href='/d/" + sid + "'>Back to dashboard</a>"
    notify("Confirm your business on Business-Bookie", "Tap to confirm and go live: " + request.host_url + "confirm/" + sid + "/" + shop.get("token", ""), shop.get("email"))
    return S + "<h1>Sent!</h1><p>We sent a new confirm link to " + str(escape(shop.get("email", ""))) + ". Check your inbox and spam folder.</p><a href='/d/" + sid + "'>Back to dashboard</a>"


@app.route("/del/<sid>", methods=["GET", "POST"])
def _bb_delete(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    now = datetime.utcnow() - timedelta(hours=10)
    def _isup(b):
        try:
            return datetime.strptime(b.get("when", ""), "%Y-%m-%d %H:%M") >= now
        except Exception:
            return False
    up = [b for b in shop.get("bookings", []) if _isup(b)]
    total = sum(float(b.get("fee") or 0) for b in up if b.get("pi"))
    name = shop.get("name", "")
    if request.method == "POST":
        if not _bb_ok(sid, request.form.get("pw", ""), shop):
            return S + "<h1>Wrong password</h1><a href='/del/" + sid + "'>Try again</a>"
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        for b in up:
            if b.get("pi") and not b.get("full_refund"):
                kw = {"payment_intent": b["pi"]}
                if b.get("keep") is not None:
                    kw["reverse_transfer"] = True
                    kw["refund_application_fee"] = True
                try:
                    stripe.Refund.create(**kw)
                except Exception as e:
                    save(d)
                    return S + "<h1>Refund failed</h1><p>" + str(escape(str(e))) + "</p><p>Your business was NOT deleted.</p><a href='/d/" + sid + "'>Back</a>"
                b["full_refund"] = True
        for b in up:
            if b.get("email"):
                notify("Your booking at " + name + " was cancelled", "Sorry! " + name + " has closed on Business-Bookie, so your " + b.get("service", "") + " on " + b.get("when", "") + " is cancelled." + (" You will be refunded. It can take 5 to 10 business days to show on your card." if b.get("pi") else ""), b["email"])
        notify("Business deleted: " + name, "Your business was removed from Business-Bookie. " + str(len(up)) + " upcoming booking(s) were cancelled and the customers will be refunded.", shop.get("email") or GMAIL)
        del d[sid]
        save(d)
        _bb_sess.pop("own_" + sid, None)
        em = shop.get("email", "")
        left = [k for k, v in d.items() if em and v.get("email") == em]
        dest = ("/mine?em=" + quote(em)) if left else "/"
        return "<meta http-equiv='refresh' content='4;url=" + dest + "'>" + S + "<h1>Business deleted</h1><p>" + str(escape(name)) + " has been removed. " + str(len(up)) + " upcoming booking(s) were cancelled and the customers will be refunded.</p><p>" + ("Taking you back to your businesses..." if left else "Taking you back to Business-Bookie...") + "</p><a href='" + dest + "'>Go now</a>"
    msg = "Delete " + str(escape(name)) + "? " + str(len(up)) + " upcoming booking(s) will be cancelled and the customers refunded ($" + ("%.2f" % total) + "). This can't be undone."
    return S + "<h1>Delete business</h1><p><b>" + str(escape(name)) + "</b></p><div style='background:#fde8e8;border:2px solid #e23b3b;border-radius:12px;padding:14px;margin:12px 0'><b>&#9888; This can't be undone.</b><br>" + str(len(up)) + " upcoming booking(s) will be cancelled and <b>refunded</b> ($" + ("%.2f" % total) + "). Customers get an email. Your business and booking link will be removed.</div><form method='post' data-m='" + msg.replace("'", "") + "' onsubmit='return confirm(this.dataset.m)'><input name='pw' type='password' placeholder='Type your password to confirm' required><button style='background:#e23b3b'>Delete my business</button></form><a href='/d/" + sid + "'>Cancel, go back</a>"

def _bb_save(d):
    return save(d)


@app.after_request
def _bb_homebar(resp):
    try:
        if resp.status_code != 200 or not (resp.mimetype or "").startswith("text/html") or request.path.startswith("/d/") or request.path.startswith("/mine") or request.headers.get("Sec-Fetch-Dest") == "iframe":
            return resp
        own = [k[4:] for k in list(_bb_sess.keys()) if k.startswith("own_") and _bb_sess.get(k)]
        if not own:
            return resp
        if True:
            d = load()
            em = next((d[s].get("email", "") for s in own if s in d), "")
            href = ("/mine?em=" + quote(em)) if em else "/d/" + own[0]
        _lab = "&#127970; All my businesses"
        _p = request.path.split("/")
        if len(_p) > 2 and _p[1] in ("edit", "cal", "block", "del", "pw") and _p[2] in own:
            href = "/d/" + _p[2]
            _lab = "&#8592; Back"
        bar = "<div style='position:sticky;top:0;z-index:999;background:#1a6dff;padding:10px 14px;display:flex;justify-content:space-between;font-family:system-ui,Arial;margin:-16px -16px 12px'><a href='" + href + "' style='background:#fff;color:#1a6dff;font-weight:700;text-decoration:none;padding:8px 14px;border-radius:8px'>" + _lab + "</a><a href='/logout' style='background:rgba(255,255,255,.2);color:#fff;font-weight:700;text-decoration:none;padding:8px 14px;border-radius:8px'>Log out</a></div>"
        resp.set_data(bar + resp.get_data(as_text=True))
    except Exception:
        pass
    return resp

def _bb_listed(v):
    return bool(v.get("live", True) and v.get("payouts_on"))


def _bb_taken(sid, shop):
    sl = build_slots(shop)
    if not sl:
        return S + "<h1>Sorry, that time was just taken</h1><p>You have <b>not</b> been charged. There are no other open times right now.</p><a href='/b/" + sid + "'>Back</a>"
    h = "".join("<input type='hidden' name='" + k + "' value='" + str(escape(request.form.get(k, ""))) + "'>" for k in ("name", "phone", "email", "service", "agree"))
    opts = "".join("<option value='" + str(escape(v)) + "'>" + str(escape(lab)) + "</option>" for v, lab in sl)
    return S + "<h1>Sorry, that time was just taken</h1><p>Someone booked it a moment ago. You have <b>not</b> been charged. Pick another time:</p><form method='post' action='/book/" + sid + "'>" + h + "<select name='when' required>" + opts + "</select><button>Book this time</button></form><a href='/b/" + sid + "'>Start over</a>"


@app.route("/dbl/<sid>")
def _bb_dbl_clear(sid):
    d = load()
    if sid in d and _bb_sess.get("own_" + sid):
        d[sid].pop("dbl", None)
        save(d)
    return redirect("/d/" + sid)


def _bb_blocked(shop, when):
    try:
        day, tm = when.split(" ")
    except Exception:
        return False
    for b in shop.get("blocks", []):
        if b.get("date") != day:
            continue
        if not b.get("start") or not b.get("end"):
            return True
        if b["start"] <= tm < b["end"]:
            return True
    return False

_bb_build_slots_orig = build_slots
def build_slots(shop):
    return [(v, lab) for v, lab in _bb_build_slots_orig(shop) if not _bb_blocked(shop, v)]

@app.route("/block/<sid>", methods=["GET", "POST"])
def _bb_block(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    if not _bb_sess.get("own_" + sid):
        return redirect("/d/" + sid)
    today = (datetime.utcnow() - timedelta(hours=10)).strftime("%Y-%m-%d")
    if request.method == "POST":
        if request.form.get("act") == "del":
            try:
                shop.get("blocks", []).pop(int(request.form.get("i", "-1")))
            except Exception:
                pass
        else:
            dt = request.form.get("date", "")
            st = request.form.get("start", "")
            en = request.form.get("end", "")
            if not dt or dt < today:
                return S + "<h1>Pick a date from today on</h1><a href='/block/" + sid + "'>Back</a>"
            if (st or en) and not (st and en and st < en):
                return S + "<h1>For a time range, set both times and make the end later than the start</h1><p>Or leave both blank to block the whole day.</p><a href='/block/" + sid + "'>Back</a>"
            shop.setdefault("blocks", []).append({"date": dt, "start": st, "end": en, "why": request.form.get("why", "")[:60]})
        shop["blocks"] = [b for b in shop.get("blocks", []) if b.get("date", "") >= today]
        save(d)
        return redirect("/block/" + sid)
    rows = ""
    for i, b in enumerate(shop.get("blocks", [])):
        if b.get("date", "") < today:
            continue
        span = (b["start"] + " - " + b["end"]) if b.get("start") else "Whole day"
        rows += "<div class='card' style='border-left:6px solid #e23b3b'><b>" + str(escape(b["date"])) + "</b> &middot; " + span + ("<br>" + str(escape(b["why"])) if b.get("why") else "") + "<form method='post' style='margin:6px 0 0'><input type='hidden' name='act' value='del'><input type='hidden' name='i' value='" + str(i) + "'><button style='background:#e23b3b;padding:8px'>Remove</button></form></div>"
    return S + "<h1>&#9940; Block off time</h1><p>Customers can't book blocked times.</p><form method='post'><p><b>Date</b></p><input type='date' name='date' min='" + today + "' required><p><b>From / to</b> (leave both blank to block the whole day)</p><input type='time' name='start'><input type='time' name='end'><input name='why' placeholder='Note (optional) e.g. Lunch, Vacation'><button>Block it</button></form><h3>Upcoming blocks</h3>" + (rows or "<p>No blocked time yet.</p>") + "<a href='/d/" + sid + "'>&#8592; Back to dashboard</a>"


@app.route("/cal/<sid>")
def _bb_cal(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    if not _bb_sess.get("own_" + sid):
        return redirect("/d/" + sid)
    try:
        w = int(request.args.get("w", "0"))
    except Exception:
        w = 0
    e = lambda s: str(escape(s))
    today = (datetime.utcnow() - timedelta(hours=10)).date()
    start = today + timedelta(days=7 * w)
    open_days = [int(x) for x in shop.get("days", [])] or [0, 1, 2, 3, 4]
    out = ""
    for i in range(7):
        day = start + timedelta(days=i)
        ds = day.strftime("%Y-%m-%d")
        items = []
        for b in shop.get("bookings", []):
            if str(b.get("when", "")).startswith(ds):
                tm = str(b.get("when", ""))[11:16]
                items.append((tm, "<div style='border-left:4px solid #1a6dff;background:#eef3ff;padding:8px 10px;margin:6px 0;border-radius:6px'><b>" + e(tm) + "</b> " + e(b.get("name", "")) + " &middot; " + e(b.get("service", "")) + "</div>"))
        for bl in shop.get("blocks", []):
            if bl.get("date") == ds:
                span = (bl["start"] + " - " + bl["end"]) if bl.get("start") else "Whole day"
                items.append((bl.get("start") or "00:00", "<div style='border-left:4px solid #e23b3b;background:#fde8e8;padding:8px 10px;margin:6px 0;border-radius:6px'><b>&#9940; " + e(span) + "</b>" + (" &middot; " + e(bl["why"]) if bl.get("why") else "") + "</div>"))
        items.sort(key=lambda x: x[0])
        body = "".join(x[1] for x in items)
        if day.weekday() not in open_days:
            body = "<p style='color:#888;margin:4px 0'>Closed</p>" + body
        elif not body:
            body = "<p style='color:#888;margin:4px 0'>No bookings</p>"
        is_today = day == today
        out += "<div class='card' style='" + ("border:2px solid #1a6dff;" if is_today else "") + "'><b>" + day.strftime("%a %b %d") + (" &middot; Today" if is_today else "") + "</b>" + body + "</div>"
    nb = "flex:1;text-align:center;border:2px solid #1a6dff;color:#1a6dff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700"
    nav = "<div style='display:flex;gap:10px;margin:10px 0'><a style='" + nb + "' href='/cal/" + sid + "?w=" + str(w - 1) + "'>&#8592; Prev week</a><a style='" + nb + "' href='/cal/" + sid + "?w=" + str(w + 1) + "'>Next week &#8594;</a></div>"
    return S + "<h1>&#128197; Calendar</h1><p>" + e(shop.get("name", "")) + " &middot; " + start.strftime("%b %d") + " - " + (start + timedelta(days=6)).strftime("%b %d") + "</p>" + nav + out + nav + "<a href='/d/" + sid + "'>&#8592; Back to dashboard</a>"


def _bb_week(shop, sid):
    e = lambda s: str(escape(s))
    today = (datetime.utcnow() - timedelta(hours=10)).date()
    open_days = [int(x) for x in shop.get("days", [])] or [0, 1, 2, 3, 4]
    out = ""
    for i in range(7):
        day = today + timedelta(days=i)
        ds = day.strftime("%Y-%m-%d")
        items = []
        for b in shop.get("bookings", []):
            if str(b.get("when", "")).startswith(ds):
                tm = str(b.get("when", ""))[11:16]
                items.append((tm, "<div style='border-left:4px solid #1a6dff;background:#eef3ff;padding:6px 10px;margin:4px 0;border-radius:6px'><b>" + e(tm) + "</b> " + e(b.get("name", "")) + " &middot; " + e(b.get("service", "")) + "</div>"))
        for bl in shop.get("blocks", []):
            if bl.get("date") == ds:
                span = (bl["start"] + " - " + bl["end"]) if bl.get("start") else "Whole day"
                items.append((bl.get("start") or "00:00", "<div style='border-left:4px solid #e23b3b;background:#fde8e8;padding:6px 10px;margin:4px 0;border-radius:6px'><b>&#9940; " + e(span) + "</b>" + (" &middot; " + e(bl["why"]) if bl.get("why") else "") + "</div>"))
        items.sort(key=lambda x: x[0])
        body = "".join(x[1] for x in items)
        if day.weekday() not in open_days:
            body = "<span style='color:#888'> Closed</span>" + body
        elif not body:
            body = "<span style='color:#888'> No bookings</span>"
        out += "<div class='card' style='padding:10px 14px;" + ("border:2px solid #1a6dff;" if i == 0 else "") + "'><b>" + day.strftime("%a %b %d") + (" &middot; Today" if i == 0 else "") + "</b>" + body + "</div>"
    return out + "<a href='/cal/" + sid + "' style='display:block;text-align:right;font-weight:700;margin:4px 0 12px'>Full calendar &#8594;</a>"


def _bb_uptiles(up):
    e = lambda s: str(escape(s))
    if not up:
        return "<div class='card' style='color:#888'>No upcoming appointments.</div>"
    tiles = ""
    for b in up[:20]:
        w = str(b.get("when", ""))
        try:
            dl = datetime.strptime(w, "%Y-%m-%d %H:%M").strftime("%a %b %d")
        except Exception:
            dl = w[:10]
        ph = str(b.get("phone", ""))
        tiles += "<div style='flex:0 0 150px;background:#fff;border-left:5px solid #1a6dff;border-radius:12px;padding:10px;box-shadow:0 1px 4px rgba(0,0,0,.08)'><div style='color:#1a6dff;font-weight:800'>" + e(dl) + "</div><div style='font-size:20px;font-weight:800'>" + e(w[11:16]) + "</div><div><b>" + e(b.get("name", "")) + "</b></div><div style='color:#556'>" + e(b.get("service", "")) + "</div>" + ("<a href='tel:" + e(ph) + "' style='font-size:13px'>&#128222; " + e(ph) + "</a>" if ph else "") + "</div>"
    return "<div style='display:flex;gap:10px;overflow-x:auto;padding:4px 2px 10px'>" + tiles + "</div>"

def _bb_month(shop, sid):
    import calendar as _cal
    e = lambda s: str(escape(s))
    today = (datetime.utcnow() - timedelta(hours=10)).date()
    y, mo = today.year, today.month
    key = "%04d-%02d" % (y, mo)
    cnt, blk = {}, set()
    for b in shop.get("bookings", []):
        w = str(b.get("when", ""))
        if w[:7] == key:
            try:
                cnt[int(w[8:10])] = cnt.get(int(w[8:10]), 0) + 1
            except Exception:
                pass
    for bl in shop.get("blocks", []):
        dt = str(bl.get("date", ""))
        if dt[:7] == key:
            try:
                blk.add(int(dt[8:10]))
            except Exception:
                pass
    open_days = [int(x) for x in shop.get("days", [])] or [0, 1, 2, 3, 4]
    hd = "".join("<div style='text-align:center;font-size:12px;font-weight:700;color:#667'>" + d + "</div>" for d in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"])
    cells = ""
    for wk in _cal.Calendar(firstweekday=6).monthdayscalendar(y, mo):
        for dy in wk:
            if dy == 0:
                cells += "<div></div>"
                continue
            day = today.replace(day=dy)
            off = (day - today).days // 7
            closed = day.weekday() not in open_days
            bg = "#f1f1f1" if closed else "#fff"
            ring = "border:2px solid #1a6dff;" if day == today else "border:1px solid #e3e3e3;"
            badge = ("<div style='background:#1a6dff;color:#fff;border-radius:10px;font-size:11px;font-weight:700;padding:0 6px;display:inline-block'>" + str(cnt[dy]) + "</div>") if dy in cnt else ""
            dot = "<div style='width:8px;height:8px;border-radius:50%;background:#e23b3b;margin:2px auto 0'></div>" if dy in blk else ""
            cells += "<a href='/cal/" + sid + "?w=" + str(off) + "' style='display:block;min-height:46px;background:" + bg + ";" + ring + "border-radius:8px;padding:3px;text-align:center;text-decoration:none;color:" + ("#999" if closed else "#222") + "'><div style='font-size:13px;font-weight:" + ("800" if day == today else "600") + "'>" + str(dy) + "</div>" + badge + dot + "</a>"
    legend = "<div style='font-size:12px;color:#556;margin-top:8px'><span style='color:#1a6dff'>&#9679;</span> bookings &nbsp; <span style='color:#e23b3b'>&#9679;</span> blocked &nbsp; <span style='color:#999'>&#9632;</span> closed &nbsp; tap a day for details</div>"
    return "<div class='card'><div style='font-weight:800;margin-bottom:8px'>" + _cal.month_name[mo] + " " + str(y) + "</div><div style='display:grid;grid-template-columns:repeat(7,1fr);gap:4px'>" + hd + cells + "</div>" + legend + "</div>"


@app.route("/edit/<sid>", methods=["GET", "POST"])
def _bb_edit(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    if not _bb_sess.get("own_" + sid):
        return redirect("/d/" + sid)
    e = lambda s: str(escape(s))
    msg = ""
    if request.method == "POST":
        f = request.form
        svc = {}
        i = 0
        while ("sn%d" % i) in f:
            n = f.get("sn%d" % i, "").strip()
            if n and not f.get("sx%d" % i):
                try:
                    svc[n[:60]] = round(float(f.get("sp%d" % i, "0") or 0), 2)
                except Exception:
                    svc[n[:60]] = 0.0
            i += 1
        err = ""
        if not f.get("name", "").strip():
            err = "Business name can't be empty."
        elif not svc:
            err = "Keep at least one service."
        elif not f.getlist("days"):
            err = "Pick at least one day you're open."
        elif f.get("open", "") >= f.get("close", ""):
            err = "Closing time must be after opening time."
        if err:
            msg = "<div class='card' style='background:#fde8e8;border-left:6px solid #e23b3b'><b>&#9888; " + e(err) + "</b> Nothing was saved.</div>"
        else:
            shop["name"] = f.get("name", "").strip()[:80]
            shop["owner"] = f.get("owner", "").strip()[:80]
            shop["addr"] = f.get("addr", "").strip()[:200]
            shop["bphone"] = f.get("bphone", "").strip()[:30]
            shop["guests_on"] = f.get("guests_on") == "1"
            shop["tables"] = max(1, min(99, int(f.get("tables") or 5))) if (f.get("tables") or "5").strip().isdigit() else 5
            shop["deposit"] = int(f.get("deposit")) if (f.get("deposit") or "").strip().isdigit() else 25
            shop["about"] = (f.get("about") or "").strip()[:600]
            if f.get("photo_rm") == "1":
                shop.pop("photo", None)
            elif (f.get("photo_data") or "").startswith("data:image/jpeg;base64,") and len(f.get("photo_data")) < 450000:
                shop["photo"] = f.get("photo_data")
            shop["days"] = f.getlist("days")
            shop["open"] = f.get("open", "09:00")
            shop["close"] = f.get("close", "17:00")
            shop["slot"] = f.get("slot", "30")
            shop["services"] = svc
            save(d)
            msg = "<div class='card' style='background:#e6f7ee;border-left:6px solid #1faa59'><b>&#10003; Saved!</b> Your public page is updated.</div>"
    days = [str(x) for x in shop.get("days", [])] or ["0", "1", "2", "3", "4"]
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dbox = "".join("<label style='margin-right:10px;white-space:nowrap'><input type='checkbox' name='days' value='" + str(i) + "'" + (" checked" if str(i) in days else "") + " style='width:auto'> " + n + "</label>" for i, n in enumerate(names))
    sl = str(shop.get("slot", "30"))
    sopt = "".join("<option value='" + v + "'" + (" selected" if v == sl else "") + ">" + lab + "</option>" for v, lab in [("30", "30 minutes"), ("60", "1 hour"), ("90", "90 minutes"), ("120", "2 hours")])
    rows = ""
    items = list(shop.get("services", {}).items())
    for i, (n, p) in enumerate(items):
        try:
            ps = "%g" % float(p)
        except Exception:
            ps = str(p)
        rows += "<div class='card'><input name='sn" + str(i) + "' value='" + e(n) + "' placeholder='Service name'><input name='sp" + str(i) + "' type='number' step='0.01' min='0' value='" + e(ps) + "' placeholder='Price $'><label style='color:#e23b3b'><input type='checkbox' name='sx" + str(i) + "' value='1' style='width:auto'> Remove this service</label></div>"
    for j in range(len(items), len(items) + 3):
        rows += "<div class='card' style='background:#f7f9ff'><input name='sn" + str(j) + "' placeholder='New service (optional)'><input name='sp" + str(j) + "' type='number' step='0.01' min='0' placeholder='Price $'></div>"
    return S + "<h1>&#9999;&#65039; Edit customer booking page</h1>" + msg + "<form method='post'><h3>Business info</h3><p>Business name</p><input name='name' value='" + e(shop.get("name", "")) + "' required><p>Your name</p><input name='owner' value='" + e(shop.get("owner", "")) + "'><p>Address</p><input name='addr' value='" + e(shop.get("addr", "")) + "'>" + _bb_bphone_in(shop) + "<h3>Hours</h3><p><b>Days you're open:</b></p>" + dbox + "<p>Opening time</p><input type='time' name='open' value='" + e(shop.get("open", "09:00")) + "'><p>Closing time</p><input type='time' name='close' value='" + e(shop.get("close", "17:00")) + "'><p>Appointment length</p><select name='slot'>" + sopt + "</select><h3>Services &amp; prices</h3>" + rows + "<button>Save changes</button></form><p><a href='/b/" + sid + "'>&#128064; Preview my page</a></p><a href='/d/" + sid + "'>&#8592; Back to dashboard</a>"


def _bb_me():
    try:
        own = [k[4:] for k in list(_bb_sess.keys()) if k.startswith("own_") and _bb_sess.get(k)]
    except Exception:
        return None
    if not own:
        return None
    d = load()
    for s in own:
        if s in d and d[s].get("email") and d[s].get("pw"):
            return d[s]
    return None

def _bb_owner_input():
    me = _bb_me()
    if not me:
        return "<input name='owner' placeholder='Your name' required>"
    return "<input type='hidden' name='owner' value='" + str(escape(me.get("owner", ""))) + "'><div class='card'>Adding to your account: <b>" + str(escape(me.get("email", ""))) + "</b></div>"

def _bb_acct_inputs():
    me = _bb_me()
    if not me:
        return """<input name='email' placeholder='Your email (we send a confirm link)' type='email' required><input name='pw' type='password' placeholder='Create a password' required><input name='pw2' type='password' placeholder='Confirm password' required oninput="this.setCustomValidity(this.value==this.form.pw.value?'':'Passwords do not match')">"""
    return "<input type='hidden' name='use_acct' value='1'><div class='card' style='background:#e6f7ee;border-left:6px solid #1faa59'>&#10003; Using your account <b>" + str(escape(me.get("email", ""))) + "</b>. No new password needed.</div>"


_BB_CONTACT = "infinitymichael29@gmail.com"

@app.route("/privacy")
def _bb_privacy():
    return S + """<h1>Privacy Policy</h1><p><i>Last updated: October 10, 2026</i></p>
<p>Business-Bookie (business-bookie.com) is an online booking service that lets businesses take appointments and payments, and lets customers book with them. This policy explains what we collect and how we use it.</p>
<h3>What we collect</h3>
<p><b>Customers:</b> your name, phone number, email address, the service and time you book, and any review you leave.<br><b>Business owners:</b> business name, owner name, address, email, password, hours, services and prices.<br><b>Payments:</b> card payments are processed by Stripe. We never see or store your full card number.</p>
<h3>How we use it</h3>
<p>We use your information only to run bookings: confirming and managing appointments, sending reminders, confirmations, and cancellation notices, processing payments and refunds, and letting the business you booked with see your booking.</p>
<h3>Text messages (SMS)</h3>
<p>If you give your phone number when booking, you agree to receive appointment-related text messages: reminders, confirmations, and cancellation notices. Message frequency varies. Message and data rates may apply. Reply <b>STOP</b> to opt out at any time, or <b>HELP</b> for help.</p>
<p><b>No mobile information will be shared with third parties or affiliates for marketing or promotional purposes.</b> Text messaging opt-in data and consent will not be shared with any third parties.</p>
<h3>Who we share with</h3>
<p>We share your booking details with the business you booked with, and we use trusted service providers to run the site: Stripe (payments), Twilio (text messages), Resend (email), Neon (database), and Render (hosting). They only use your data to provide those services. <b>We do not sell your personal information.</b></p>
<h3>Keeping and deleting data</h3>
<p>We keep booking records as long as needed to run the service and meet legal and payment requirements. To ask us to delete your information, email us below.</p>
<h3>Security</h3>
<p>We use HTTPS and trusted providers to protect your data, but no system is 100% secure.</p>
<h3>Age requirement</h3>
<p>Business-Bookie is intended for users 18 and older. It is not intended for anyone under 18.</p>
<h3>Changes</h3>
<p>We may update this policy. The date at the top shows the latest version.</p>
<h3>Contact</h3>
<p>Questions or requests: <a href='mailto:""" + _BB_CONTACT + "'>" + _BB_CONTACT + """</a></p>
<p><a href='/terms'>Terms</a> &middot; <a href='/'>Home</a></p>"""

@app.route("/terms")
def _bb_terms():
    return S + """<h1>Terms &amp; Conditions</h1><p><i>Last updated: October 10, 2026</i></p>
<p>By using Business-Bookie (business-bookie.com), you agree to these terms. You must be 18 or older to use Business-Bookie.</p>
<h3>The service</h3>
<p>Business-Bookie lets businesses list their services and take bookings, and lets customers book and pay. Each business is responsible for its own services, prices, hours, and for showing up to appointments.</p>
<h3>Booking and payment</h3>
<p>Customers pay the full price when booking. Payments are processed securely by Stripe. Business-Bookie keeps a small service fee from each payment.</p>
<h3>Cancellations, rescheduling, and no-shows</h3>
<p>If you cancel before your appointment, you are refunded the amount paid minus a processing fee (card fees plus a 3.7% service fee). To reschedule, work it out with the business owner. If you miss your appointment without cancelling, your payment is non-refundable. If a business removes itself from Business-Bookie, upcoming bookings are cancelled and the customers are refunded. If a time slot is booked by someone else at the same moment, the later payment is refunded in full.</p>
<h3>Text messages (SMS)</h3>
<p>By giving your phone number when booking, you agree to receive appointment-related text messages: reminders, confirmations, and cancellation notices. Message frequency varies. Message and data rates may apply. Reply <b>STOP</b> to stop receiving messages. Reply <b>HELP</b> for help, or email us below. Carriers are not liable for delayed or undelivered messages.</p>
<h3>Business owners</h3>
<p>Owners must give accurate information, connect a valid payout account through Stripe, keep their login private, and honor the bookings they accept.</p>
<h3>Acceptable use</h3>
<p>Don't misuse the site: no fake bookings, fraud, spam, or attempts to break or overload the service. We may suspend accounts that do.</p>
<h3>We are a booking platform only</h3>
<p>Business-Bookie only provides software that connects customers with independent businesses. We do not provide, supervise, or guarantee any service a business offers. Each business is solely responsible for its services, staff, premises, pricing, licenses, safety, and conduct. Any dispute about a service is between the customer and the business.</p>
<h3>Third-party services</h3>
<p>We rely on outside providers, including Stripe (payments), Twilio (text messages), Resend (email), Neon (database), and Render (hosting). We are not responsible for their errors, outages, or delays, and their own terms apply to your use of them.</p>
<h3>No warranties</h3>
<p>The service is provided <b>"as is" and "as available,"</b> without warranties of any kind, express or implied, including fitness for a particular purpose. We don't promise the site will always be available, error-free, or that messages will always be delivered.</p>
<h3>Limitation of liability</h3>
<p>To the fullest extent the law allows, Business-Bookie and its owner will not be liable for any indirect, incidental, special, consequential, or punitive damages, or for lost profits, data, or business, arising from your use of the service or any service provided by a business. <b>Our total liability for any claim is limited to the greater of the amount you paid for the booking involved or $100.</b></p>
<h3>Indemnification</h3>
<p>You agree to defend, indemnify, and hold harmless Business-Bookie and its owner from any claims, losses, damages, and costs (including reasonable attorney fees) arising from your use of the service, your violation of these terms, or, for business owners, the services you provide to customers.</p>
<h3>Disputes and arbitration</h3>
<p><b>Informal resolution first:</b> before filing any claim, you agree to email us and try to resolve it informally for at least 30 days.</p>
<p><b>Binding arbitration:</b> any dispute that isn't resolved informally will be settled by binding individual arbitration administered by the American Arbitration Association under its consumer rules, held in Honolulu, Hawaii, or by video. Either party may instead bring an individual claim in small claims court if it qualifies.</p>
<p><b>No class actions:</b> you agree to bring claims only in your individual capacity, not as a plaintiff or class member in any class, group, or representative action, and the arbitrator may not combine claims of different people.</p>
<p><b>Opt-out:</b> you may opt out of arbitration by emailing us within 30 days of first using Business-Bookie.</p>
<p><b>Time limit:</b> any claim must be brought within one year after it arises, or it is permanently barred.</p>
<h3>Suspension and termination</h3>
<p>We may suspend or remove any account or business listing at any time if we believe these terms were violated or the service is being misused.</p>
<h3>Events beyond our control</h3>
<p>We are not responsible for delays or failures caused by events beyond our reasonable control, such as outages, natural disasters, or provider failures.</p>
<h3>General</h3>
<p>If any part of these terms is found unenforceable, the rest stays in effect. These terms, together with our Privacy Policy, are the entire agreement between you and Business-Bookie. We may transfer these terms if the business changes ownership or structure.</p>
<h3>Changes</h3>
<p>We may update these terms. The date at the top shows the latest version.</p>
<h3>Governing law</h3>
<p>These terms are governed by the laws of the State of Hawaii.</p>
<h3>Contact</h3>
<p><a href='mailto:""" + _BB_CONTACT + "'>" + _BB_CONTACT + """</a></p>
<p><a href='/privacy'>Privacy Policy</a> &middot; <a href='/'>Home</a></p>"""

def _bb_phone_html(shop):
    p = (shop.get("bphone") or "").strip()
    if not p:
        return ""
    d = "".join(c for c in p if c.isdigit() or c == "+")
    return "<p>Phone: <a href='tel:" + str(escape(d)) + "'>" + str(escape(p)) + "</a></p>"


def _bb_bphone_in(shop):
    return "<p>Business phone</p><input name='bphone' type='tel' placeholder='(808) 555-1234' value='" + str(escape(shop.get("bphone", ""))) + "'>"


def _bb_guests_on(shop):
    if "guests_on" in shop:
        return bool(shop["guests_on"])
    ty = (shop.get("type") or "").lower()
    return any(w in ty for w in ("restaurant", "cafe", "diner", "bar", "grill", "bistro", "eatery"))


def _bb_guests_sel(shop):
    if not _bb_guests_on(shop):
        return ""
    o = "".join("<option value='" + str(i) + "'" + (" selected" if i == 2 else "") + ">" + str(i) + "</option>" for i in range(1, 9))
    return "<p>Number of guests</p><select name='guests' required>" + o + "<option value='9+'>9+ (large party)</option></select>"


_bb_bphone_in_old = _bb_bphone_in


def _bb_bphone_in(shop):
    ck = " checked" if _bb_guests_on(shop) else ""
    return _bb_bphone_in_old(shop) + "<p><label><input type='checkbox' name='guests_on' value='1'" + ck + " style='width:auto'> Ask customers for number of guests (restaurants)</label></p>"


@app.before_request
def _bb_guests_hook():
    if request.method != "POST":
        return
    g = (request.form.get("guests") or "").strip()[:6]
    n = request.form.get("name") or ""
    if not g or not n or "party of" in n or "when" not in request.form:
        return
    from werkzeug.datastructures import ImmutableMultiDict
    d = request.form.to_dict(flat=False)
    d["name"] = [n + " (party of " + g + ")"]
    request.form = ImmutableMultiDict(d)


def _bb_full(shop):
    cap = 1
    if _bb_guests_on(shop):
        try:
            cap = max(1, int(shop.get("tables") or 5))
        except Exception:
            cap = 5
    c = {}
    for x in shop.get("bookings", []):
        w = x.get("when")
        c[w] = c.get(w, 0) + 1
    return {w for w, k in c.items() if k >= cap}


_bb_bphone_in_old2 = _bb_bphone_in


def _bb_bphone_in(shop):
    return _bb_bphone_in_old2(shop) + "<p>Tables per time slot (restaurants)</p><input name='tables' type='number' min='1' max='99' value='" + str(shop.get("tables") or 5) + "'>"


def _bb_dep(shop):
    try:
        return max(0, int(shop.get("deposit", 25)))
    except Exception:
        return 25


def _bb_party_fee(shop, fee):
    if not _bb_guests_on(shop):
        return fee
    g = (request.form.get("guests") or "").strip()
    big = g == "9+" or "party of 9+" in (request.form.get("name") or "")
    if big and _bb_dep(shop) > 0:
        return float(fee or 0) + _bb_dep(shop)
    return fee


_bb_guests_sel_old = _bb_guests_sel


def _bb_guests_sel(shop):
    h = _bb_guests_sel_old(shop)
    if h and _bb_dep(shop) > 0:
        h += "<p style='font-size:12px;color:#556;margin:2px 0 8px'>Parties of 9 or more require a $" + str(_bb_dep(shop)) + " deposit at booking.</p>"
    return h


_bb_bphone_in_old3 = _bb_bphone_in


def _bb_bphone_in(shop):
    return _bb_bphone_in_old3(shop) + "<p>Large party (9+) deposit in $ (0 = no deposit)</p><input name='deposit' type='number' min='0' max='999' value='" + str(_bb_dep(shop)) + "'>"


def _bb_gross(fee):
    try:
        c = int(round(float(fee or 0) * 100))
    except Exception:
        return fee
    if c <= 0:
        return fee
    t = int(-(-(c + 30) // (1 - BB_CUT - 0.029)))
    while t - (int(round(t * BB_CUT)) + int(round(t * 0.029)) + 30) < c:
        t += 1
    return t / 100


def _bb_fee_box(shop):
    import json
    dep = _bb_dep(shop) if _bb_guests_on(shop) else 0
    m = {}
    for k, v in (shop.get("services") or {}).items():
        try:
            b = float(v or 0)
        except Exception:
            b = 0
        m[k] = [b, float(_bb_gross(b) or 0), b + dep, float(_bb_gross(b + dep) or 0)]
    js = json.dumps(m).replace("</", "<\\/")
    return ("<div id='bbfee' class='card' style='font-size:14px;margin:8px 0'></div><script>(function(){var M=" + js + ";"
            "function f(x){return '$'+x.toFixed(2)}"
            "function u(){var e=document.querySelector('[name=service]:checked')||document.querySelector('select[name=service]');"
            "var g=document.querySelector('[name=guests]');var big=g&&g.value=='9+';var d=document.getElementById('bbfee');"
            "if(!e||!M[e.value]){d.style.display='none';return}var r=M[e.value];var b=big?r[2]:r[0],t=big?r[3]:r[1];"
            "if(t<=0){d.innerHTML='<b>Total: Free</b> - no card needed';d.style.display='block';return}"
            "d.innerHTML=(big&&r[2]>r[0]?e.value+' + large party deposit: ':e.value+': ')+f(b)+'<br>Service &amp; card fees: '+f(t-b)+'<br><b>Total charged today: '+f(t)+'</b>';d.style.display='block'}"
            "document.addEventListener('change',u);document.addEventListener('DOMContentLoaded',u);u()})();</script>")


@app.route("/qr/<sid>")
def bb_qr(sid):
    d = load()
    if sid not in d:
        return S + "<h1>Not found</h1>", 404
    import segno
    base = request.host_url.rstrip("/") if "localhost" in request.host else "https://" + request.host
    url = base + "/b/" + sid
    q = segno.make(url, error="m")
    img = q.png_data_uri(scale=10, border=2)
    nm = str(escape(d[sid].get("name", "")))
    fn = "".join(c for c in d[sid].get("name", "qr") if c.isalnum()) or "qr"
    return (S + "<style>@media print{.noprint{display:none!important}}</style>"
            "<div style='text-align:center'><h1>" + nm + "</h1><p style='font-size:20px;margin:4px 0'><b>Scan to book</b></p>"
            "<img src='" + img + "' alt='QR code' style='width:280px;max-width:90%;image-rendering:pixelated'>"
            "<p style='font-size:13px;color:#556;word-break:break-all'>" + str(escape(url)) + "</p>"
            "<div class='noprint'><a href='" + img + "' download='" + fn + "-qr.png' style='display:block;max-width:340px;margin:10px auto;padding:14px;border:2px solid #1a6dff;border-radius:12px;text-decoration:none;font-weight:bold'>&#11015;&#65039; Download QR image</a>"
            "<a href='#' onclick='window.print();return false' style='display:block;max-width:340px;margin:10px auto;padding:14px;border:2px solid #1a6dff;border-radius:12px;text-decoration:none;font-weight:bold'>&#128424;&#65039; Print</a>"
            "<p style='font-size:13px;color:#556'>Put it on your counter, mirror, door or tables. Customers scan it with their phone camera to book.</p></div></div>")


@app.after_request
def _bb_qr_btn(resp):
    try:
        p = request.path
        if request.method == "GET" and p.startswith("/d/") and resp.status_code == 200 and resp.mimetype == "text/html":
            sid = p.split("/")[2]
            h = resp.get_data(as_text=True)
            if "Block off time" in h and "/qr/" + sid not in h and "</h1>" in h:
                b = "<a href='/qr/" + sid + "' style='display:block;max-width:340px;margin:10px auto;padding:12px;border:2px solid #1a6dff;border-radius:12px;text-align:center;text-decoration:none;font-weight:bold'>&#128241; My QR code (scan to book)</a>"
                h = h.replace(">Share link</button>", ">Share link</button>" + b, 1) if ">Share link</button>" in h else h.replace("</h1>", "</h1>" + b, 1)
                resp.set_data(h)
    except Exception as e:
        print("qr btn:", e)
    return resp


def _bb_base():
    return request.host_url.rstrip("/") if "localhost" in request.host else "https://" + request.host


def _bb_qr_page(url, title, sub, note):
    import segno
    img = segno.make(url, error="m").png_data_uri(scale=10, border=2)
    fn = "".join(c for c in title if c.isalnum()) or "qr"
    btn = "display:block;max-width:340px;margin:10px auto;padding:14px;border:2px solid #1a6dff;border-radius:12px;text-decoration:none;font-weight:bold"
    return (S + "<style>@media print{.noprint{display:none!important}}</style>"
            "<div style='text-align:center'><h1>" + str(escape(title)) + "</h1>"
            "<p style='font-size:20px;margin:4px 0'><b>" + str(escape(sub)) + "</b></p>"
            "<img src='" + img + "' alt='QR code' style='width:280px;max-width:90%;image-rendering:pixelated'>"
            "<p style='font-size:13px;color:#556;word-break:break-all'>" + str(escape(url)) + "</p>"
            "<div class='noprint'><a href='" + img + "' download='" + fn + "-qr.png' style='" + btn + "'>&#11015;&#65039; Download QR image</a>"
            "<a href='#' onclick='window.print();return false' style='" + btn + "'>&#128424;&#65039; Print</a>"
            "<p style='font-size:13px;color:#556'>" + str(escape(note)) + "</p></div></div>")


@app.route("/qrcode")
def bb_qr_platform():
    return _bb_qr_page(_bb_base() + "/", "Business-Bookie", "Scan to get started", "Post it anywhere. People scan to book a business or sign up their own.")


@app.route("/myqr/<sid>/<rt>")
def bb_qr_customer(sid, rt):
    d = load()
    if sid not in d:
        return S + "<h1>Not found</h1>", 404
    if not any(b.get("rt") == rt for b in d[sid].get("bookings", [])):
        return S + "<h1>Booking not found</h1>", 404
    url = _bb_base() + "/m/" + sid + "/" + rt
    return _bb_qr_page(url, d[sid].get("name", "Your booking"), "Scan to view your booking", "Scan anytime to see, reschedule or cancel your booking.")


_bb_notify_old = notify


def notify(subject, body, to=None):
    try:
        import re
        m = re.search(r"(https?://[^\s/]+)/m/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", body or "")
        if m and "/myqr/" not in body:
            body = body + "\n\nYour booking QR code (scan to view, reschedule or cancel): " + m.group(1) + "/myqr/" + m.group(2) + "/" + m.group(3)
    except Exception as e:
        print("qr mail:", e)
    return _bb_notify_old(subject, body, to)


def _bb_dbkey():
    return "shops_test" if os.environ.get("STRIPE_SECRET_KEY", "").startswith("sk_test") else "shops"


def _bb_payerr(d, sid, shop, ex):
    msg = str(ex)
    if "No such destination" in msg or "No such account" in msg:
        shop.pop("acct", None)
        shop["payouts_on"] = False
        try:
            save(d)
        except Exception as e:
            print("payerr save:", e)
        try:
            notify("Action needed: reconnect payments for " + shop.get("name", ""), "A customer tried to book a paid service at " + shop.get("name", "") + ", but your payment account needs to be reconnected. Log in to your dashboard and tap Connect payments: " + request.host_url + "d/" + sid, shop.get("email"))
        except Exception as e:
            print("payerr mail:", e)
        ph = shop.get("bphone", "")
        return S + "<h1>Online payments are being set up</h1><p>" + str(escape(shop.get("name", ""))) + " is finishing its payment setup, so paid bookings aren't available right now. <b>You have not been charged.</b></p>" + ("<p>Please call to book: <a href='tel:" + str(escape(ph)) + "'>" + str(escape(ph)) + "</a></p>" if ph else "<p>Please try again later.</p>") + "<a href='/b/" + sid + "'>Back</a>"
    return S + "<h1>Payment error</h1><p>" + str(escape(msg)) + "</p><a href='/b/" + sid + "'>Back</a>"


@app.route("/favicon.ico")
@app.route("/favicon-32.png")
def bb_favicon():
    from flask import send_from_directory
    return send_from_directory(app.root_path, "favicon-32.png", mimetype="image/png", max_age=86400)


@app.route("/icon-192.png")
@app.route("/icon-512.png")
def bb_icons():
    from flask import send_from_directory
    return send_from_directory(app.root_path, request.path.lstrip("/"), mimetype="image/png", max_age=86400)


@app.route("/manifest.json")
def bb_manifest():
    import json as _j
    m = {"name": "Business-Bookie", "short_name": "Business-Bookie", "description": "Book appointments with local businesses, or take bookings for your own.",
         "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#1a6dff",
         "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                   {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                   {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    return app.response_class(_j.dumps(m), mimetype="application/manifest+json")


@app.route("/sw.js")
def bb_sw():
    js = "self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());self.addEventListener('fetch',e=>{});"
    return app.response_class(js, mimetype="application/javascript")


_bb_icon_head = ("<link rel='icon' type='image/png' href='/favicon-32.png'><link rel='apple-touch-icon' href='/icon-192.png'>"
                 "<link rel='manifest' href='/manifest.json'><meta name='theme-color' content='#1a6dff'>"
                 "<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(function(){})}</script>")


@app.after_request
def _bb_icons_inject(resp):
    try:
        if resp.mimetype == "text/html" and resp.status_code == 200 and not resp.direct_passthrough:
            h = resp.get_data(as_text=True)
            if "rel='manifest'" not in h:
                h = h.replace("</head>", _bb_icon_head + "</head>", 1) if "</head>" in h else _bb_icon_head + h
                resp.set_data(h)
    except Exception as e:
        print("icons:", e)
    return resp


@app.before_request
def _bb_dupe_email():
    try:
        if request.method != "POST" or request.endpoint != "create" or request.form.get("use_acct") == "1":
            return None
        em = (request.form.get("email") or "").strip().lower()
        if not em:
            return None
        d = load()
        if any((v.get("email") or "").strip().lower() == em for v in d.values()):
            btn = "display:block;box-sizing:border-box;width:100%;max-width:340px;margin:12px auto;padding:14px;border:2px solid #1a6dff;border-radius:12px;text-align:center;text-decoration:none;font-weight:bold"
            return (S + "<h1>You already have an account</h1>"
                    "<p><b>" + str(escape(em)) + "</b> already has a business on Business-Bookie.</p>"
                    "<p>Log in with that email, then tap <b>Add another business</b> on your My businesses page. Everything stays under one account.</p>"
                    "<a href='/login' style='" + btn + "'>&#128273; Log in</a>"
                    "<a href='/new' style='" + btn + "'>Use a different email</a>")
    except Exception as e:
        print("dupe email check:", e)
    return None


_BB_SMS_POLICY = ("<h3>Text messages (SMS)</h3><p>If you check the text-message box when booking or signing up, Business-Bookie sends appointment "
                  "confirmations, reminders, cancellation notices and (for business owners) new-booking alerts to the number you give. Message frequency varies. "
                  "Msg &amp; data rates may apply. Reply STOP to opt out at any time, or HELP for help. Consent to texts is not a condition of booking. "
                  "<b>No mobile information will be shared with third parties or affiliates for marketing or promotional purposes.</b> "
                  "Text-messaging opt-in data and consent are never shared with any third parties.</p>")


@app.route("/sms")
def bb_sms_info():
    box = "background:#fff;border:1px solid #dfe5f1;border-radius:12px;padding:16px;margin:12px 0"
    return (S + "<h1>Text message opt-in</h1>"
            "<p>Business-Bookie lets customers book appointments with local businesses. Customers can choose to get text messages about their booking.</p>"
            "<h3>How customers opt in</h3>"
            "<p>On every business booking page (for example <a href='/find'>www.business-bookie.com/find</a> &rarr; pick a business), the customer enters their "
            "name, email and mobile number. Under the phone field is a checkbox that is <b>unchecked by default</b>. Texts are only sent if the customer checks it. "
            "Consent is not required to book.</p>"
            "<div style='" + box + "'><p style='margin:0 0 6px;font-weight:700'>The booking form looks like this:</p>"
            "<input placeholder='Your name' disabled><input placeholder='Email' disabled><input placeholder='Phone number' type='tel' disabled>"
            "<label style='display:flex;gap:10px;align-items:flex-start;font-size:13px;color:#334;margin:6px 0 10px;line-height:1.4'>"
            "<input type='checkbox' disabled style='width:auto;margin:3px 0 0;flex:none'>"
            "<span>Yes, text me appointment confirmations, reminders and cancellation notices from Business-Bookie at this number. "
            "Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out, HELP for help. Consent is not a condition of booking. "
            "<a href='/privacy'>Privacy Policy</a> &middot; <a href='/terms'>Terms</a></span></label></div>"
            "<h3>How business owners opt in</h3>"
            "<p>When a business signs up, the owner enters a business phone number and may check a separate, unchecked-by-default box to get new-booking and "
            "cancellation alerts by text.</p>"
            "<h3>Example messages</h3>"
            "<div style='" + box + "'>Business-Bookie: You're booked at Island Cuts for Haircut on Dec 1 at 10:00 AM. Questions? Call (808) 555-0100. Reply STOP to opt out.</div>"
            "<div style='" + box + "'>Business-Bookie reminder: Haircut at Island Cuts tomorrow at 10:00 AM. Manage your booking: https://www.business-bookie.com/m/... Reply STOP to opt out.</div>"
            "<div style='" + box + "'>Business-Bookie: New booking at Island Cuts - Haircut, Dec 1 at 10:00 AM. Reply STOP to opt out.</div>"
            "<h3>Opting out and help</h3><p>Reply <b>STOP</b> to any message to stop texts. Reply <b>HELP</b> for help. Message frequency varies. "
            "Msg &amp; data rates may apply.</p>" + _BB_SMS_POLICY +
            "<p><a href='/privacy'>Privacy Policy</a> &middot; <a href='/terms'>Terms of Service</a></p>")


@app.after_request
def _bb_privacy_sms(resp):
    try:
        if request.path == "/privacy" and resp.status_code == 200 and resp.mimetype == "text/html":
            h = resp.get_data(as_text=True)
            if "No mobile information will be shared" not in h:
                h = h.replace("</body>", _BB_SMS_POLICY + "</body>", 1) if "</body>" in h else h + _BB_SMS_POLICY
                resp.set_data(h)
    except Exception as e:
        print("privacy sms:", e)
    return resp


def _bb_fmt(w):
    try:
        x = datetime.strptime(w, "%Y-%m-%d %H:%M")
        return x.strftime("%a %b %d, %I:%M %p").replace(" 0", " ")
    except Exception:
        return w or ""


def _bb_noshow_alert(shop, sid, b):
    try:
        nm, sv, wh = b.get("name", ""), b.get("service", ""), _bb_fmt(b.get("when", ""))
        ph = shop.get("bphone", "")
        if b.get("email"):
            notify("You missed your appointment at " + shop["name"],
                   "Hi " + nm + ",\n\nYou were marked as a no-show for your " + sv + " at " + shop["name"] + " on " + wh + ".\n\n"
                   "Under the cancellation and no-show terms you agreed to when booking, the booking fee is not refunded.\n\n"
                   "Want to book again? " + request.host_url + "b/" + sid + ("\n\nQuestions? Call " + ph if ph else ""), b["email"])
        notify("No-show recorded at " + shop["name"], nm + " - " + sv + " - " + wh + " was marked as a no-show. The customer has been notified by email.",
               shop.get("email") or GMAIL)
    except Exception as e:
        print("noshow alert:", e)


_bb_full_base = _bb_full


def _bb_full(shop):
    held = [{"when": x["prop"]["when"]} for x in shop.get("bookings", []) if x.get("prop")]
    if not held:
        return _bb_full_base(shop)
    s2 = dict(shop)
    s2["bookings"] = list(shop.get("bookings", [])) + held
    return _bb_full_base(s2)


def _bb_free_for(shop, b, w):
    s2 = dict(shop)
    s2["bookings"] = [dict(x, prop=None) if x is b else x for x in shop.get("bookings", [])]
    try:
        if _bb_blocked(shop, w):
            return False
    except Exception:
        pass
    return w not in _bb_full(s2)


def _bb_neg_link(sid, b, role):
    return request.host_url + "neg/" + sid + "/" + b.get("rt", "") + "?as=" + role


def _bb_propose(shop, sid, b, w, role):
    if w == b.get("when"):
        return "<h1>That's already the booked time</h1><a href='/d/" + sid + "'>Back</a>"
    if not _bb_free_for(shop, b, w):
        return "<h1>That time is full or blocked</h1><p>Pick another time.</p><a href='javascript:history.back()'>Back</a>"
    p = b.get("prop") or {"hist": []}
    p["hist"] = (p.get("hist") or []) + [("Business" if role == "owner" else "Customer") + " suggested " + _bb_fmt(w)]
    p["when"], p["by"] = w, role
    b["prop"] = p
    try:
        if role == "owner" and b.get("email"):
            notify(shop["name"] + " wants to move your appointment",
                   "Hi " + b.get("name", "") + ",\n\n" + shop["name"] + " would like to move your " + b.get("service", "") + "\nfrom: " + _bb_fmt(b.get("when", "")) +
                   "\nto:   " + _bb_fmt(w) + "\n\nAccept it, suggest a different time, or keep your original time here:\n" + _bb_neg_link(sid, b, "c"), b["email"])
        elif role == "customer":
            notify("Time change request at " + shop["name"],
                   b.get("name", "") + " (" + b.get("service", "") + ") would like " + _bb_fmt(w) + " instead of " + _bb_fmt(b.get("when", "")) +
                   ".\n\nAccept, suggest another time, or keep the original:\n" + _bb_neg_link(sid, b, "o"), shop.get("email") or GMAIL)
    except Exception as e:
        print("propose mail:", e)
    return ""


@app.route("/neg/<sid>/<rt>", methods=["GET", "POST"])
def bb_negotiate(sid, rt):
    d = load()
    shop = d.get(sid)
    b = next((x for x in (shop or {}).get("bookings", []) if x.get("rt") == rt), None)
    if not shop or not b:
        return S + "<h1>Booking not found</h1>", 404
    role = "owner" if request.args.get("as") == "o" else "customer"
    back = ("/d/" + sid) if role == "owner" else ("/m/" + sid + "/" + rt)
    if role == "owner" and not _bb_ok(sid, "", shop):
        return S + "<h1>Please log in first</h1><p>Log in to your business, then open this link again.</p><a href='/login'>Log in</a>"
    other = "customer" if role == "owner" else "owner"
    p = b.get("prop")
    if request.method == "POST":
        act = request.form.get("act", "")
        if not p:
            return redirect(request.full_path)
        if act == "accept" and p.get("by") != role:
            old = b.get("when", "")
            b["moved_from"], b["when"] = old, p["when"]
            b.pop("prop", None)
            save(d)
            msg = "Your " + b.get("service", "") + " at " + shop["name"] + " is now confirmed for " + _bb_fmt(b["when"]) + " (moved from " + _bb_fmt(old) + ")."
            try:
                if b.get("email"):
                    notify("New time confirmed at " + shop["name"], "Hi " + b.get("name", "") + ",\n\n" + msg + "\n\nManage your booking: " + request.host_url + "m/" + sid + "/" + rt, b["email"])
                notify("New time confirmed: " + b.get("name", ""), b.get("name", "") + " - " + b.get("service", "") + " moved from " + _bb_fmt(old) + " to " + _bb_fmt(b["when"]) + ".", shop.get("email") or GMAIL)
            except Exception as e:
                print("accept mail:", e)
            return S + "<h1>&#9989; New time confirmed</h1><p>" + str(escape(msg)) + "</p><a href='" + back + "'>Back</a>"
        if act == "keep":
            b.pop("prop", None)
            save(d)
            try:
                txt = "The time change for " + b.get("name", "") + " (" + b.get("service", "") + ") was called off. The appointment stays at " + _bb_fmt(b.get("when", "")) + "."
                if role == "owner" and b.get("email"):
                    notify("Your appointment at " + shop["name"] + " stays the same", "Hi " + b.get("name", "") + ",\n\n" + txt, b["email"])
                elif role == "customer":
                    notify("Time change declined: " + b.get("name", ""), txt, shop.get("email") or GMAIL)
            except Exception as e:
                print("keep mail:", e)
            return S + "<h1>Original time kept</h1><p>The appointment stays at " + str(escape(_bb_fmt(b.get("when", "")))) + ".</p><a href='" + back + "'>Back</a>"
        if act == "counter" and p.get("by") != role:
            w = request.form.get("when", "")
            if w not in [v for v, _ in build_slots(shop)] and not (role == "owner" and w):
                return S + "<h1>That time isn't available</h1><a href='" + request.full_path + "'>Pick another</a>"
            e = _bb_propose(shop, sid, b, w, role)
            if e:
                return S + e
            save(d)
            return S + "<h1>&#128257; Suggestion sent</h1><p>We sent " + ("the customer" if role == "owner" else shop["name"]) + " your suggested time: <b>" + str(escape(_bb_fmt(w))) + "</b>. You'll get an email when they answer.</p><a href='" + back + "'>Back</a>"
        return redirect(request.full_path)
    head = (S + "<h1>Time change</h1><p><b>" + str(escape(shop["name"])) + "</b><br>" + str(escape(b.get("name", ""))) + " - " + str(escape(b.get("service", ""))) +
            "<br>Booked time: <b>" + str(escape(_bb_fmt(b.get("when", "")))) + "</b></p>")
    if not p:
        return head + "<p>There's no time change pending for this booking.</p><a href='" + back + "'>Back</a>"
    hist = "<div class='card'><b>History</b><br>" + "<br>".join(str(escape(h)) for h in p.get("hist", [])) + "</div>"
    who = "The business" if p.get("by") == "owner" else "The customer"
    cur = "<div class='card' style='background:#fff6e5'><b>" + who + " suggested:</b><br><span style='font-size:22px;font-weight:800'>" + str(escape(_bb_fmt(p["when"]))) + "</span></div>"
    keep = "<form method='post'><input type='hidden' name='act' value='keep'><button style='background:#fff;color:#1a6dff;border:2px solid #1a6dff'>&#10060; Keep the original time</button></form>"
    if p.get("by") == role:
        return head + cur + "<p>Waiting for the " + other + " to answer. We'll email you when they do.</p>" + keep + hist + "<a href='" + back + "'>Back</a>"
    slots = [(v, lab) for v, lab in build_slots(shop) if v not in (b.get("when"), p["when"])]
    acc = "<form method='post'><input type='hidden' name='act' value='accept'><button>&#9989; Accept " + str(escape(_bb_fmt(p["when"]))) + "</button></form>"
    if slots:
        ctr = ("<h3>&#128257; Suggest a different time</h3><form method='post'><input type='hidden' name='act' value='counter'><select name='when' required>" +
               "".join("<option value='" + str(escape(v)) + "'>" + str(escape(lab)) + "</option>" for v, lab in slots) + "</select><button>Send my suggestion</button></form>")
    else:
        ctr = "<p>No other open times to suggest right now.</p>"
    return head + cur + acc + ctr + "<h3>Or</h3>" + keep + hist + "<a href='" + back + "'>Back</a>"


@app.after_request
def _bb_neg_banners(resp):
    try:
        if request.method != "GET" or resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        parts = request.path.strip("/").split("/")
        if parts[0] == "d" and len(parts) == 2:
            shop = load().get(parts[1]) or {}
            pend = [x for x in shop.get("bookings", []) if x.get("prop")]
            if pend:
                rows = "".join("<a href='/neg/" + parts[1] + "/" + x.get("rt", "") + "?as=o' style='display:block;margin-top:6px;font-weight:700'>" +
                               str(escape(x.get("name", ""))) + ": " + str(escape(_bb_fmt(x.get("when", "")))) + " &rarr; " + str(escape(_bb_fmt(x["prop"]["when"]))) +
                               (" (your turn)" if x["prop"].get("by") == "customer" else " (waiting on customer)") + "</a>" for x in pend)
                ban = "<div class='card' style='background:#fff6e5;border-left:6px solid #f0a500'><b>&#9203; Time changes pending</b>" + rows + "</div>"
                h = resp.get_data(as_text=True)
                if "<div class='wrap'>" in h:
                    resp.set_data(h.replace("<div class='wrap'>", "<div class='wrap'>" + ban, 1))
        elif parts[0] == "m" and len(parts) == 3:
            shop = load().get(parts[1]) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == parts[2]), None)
            if b and b.get("prop"):
                ban = ("<div class='card' style='background:#fff6e5;border-left:6px solid #f0a500'><b>&#9203; Time change pending</b><br>" +
                       ("The business suggested " if b["prop"].get("by") == "owner" else "You suggested ") + str(escape(_bb_fmt(b["prop"]["when"]))) +
                       "<br><a href='/neg/" + parts[1] + "/" + parts[2] + "?as=c' style='font-weight:700'>Respond / view</a></div>")
                h = resp.get_data(as_text=True)
                i = h.find("</h1>")
                resp.set_data(h[:i + 5] + ban + h[i + 5:] if i >= 0 else ban + h)
    except Exception as e:
        print("neg banner:", e)
    return resp


_BB_SW = ("self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>{});"
          "self.addEventListener('push',e=>{let d={};try{d=e.data.json()}catch(x){d={title:'Business-Bookie',body:e.data?e.data.text():''}}"
          "e.waitUntil(self.registration.showNotification(d.title||'Business-Bookie',{body:d.body||'',icon:'/icon-192.png',badge:'/favicon-32.png',data:{url:d.url||'/'}}))});"
          "self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(clients.openWindow((e.notification.data&&e.notification.data.url)||'/'))});")


def bb_sw_push():
    return app.response_class(_BB_SW, mimetype="application/javascript")


app.view_functions["bb_sw"] = bb_sw_push


def _bb_push_send(subs, title, body, url):
    import json as _j
    priv = os.environ.get("VAPID_PRIVATE", "")
    if not priv or not subs:
        return
    from pywebpush import webpush
    data = _j.dumps({"title": title[:80], "body": body[:180], "url": url})
    for s in subs:
        try:
            webpush(subscription_info=s, data=data, vapid_private_key=priv,
                    vapid_claims={"sub": "mailto:" + globals().get("_BB_CONTACT", "infinitymichael29@gmail.com")}, timeout=10)
        except Exception as e:
            print("push send:", str(e)[:200])


def _bb_push_for(subject, body, to):
    import re, threading
    if not os.environ.get("VAPID_PRIVATE"):
        return
    to = (to or "").strip().lower()
    if not to:
        return
    subs, seen = [], set()
    for shop in load().values():
        cand = list(shop.get("push", [])) if (shop.get("email") or "").strip().lower() == to else []
        for b in shop.get("bookings", []):
            if (b.get("email") or "").strip().lower() == to:
                cand += b.get("push", [])
        for s in cand:
            if s.get("endpoint") and s["endpoint"] not in seen:
                seen.add(s["endpoint"])
                subs.append(s)
    if not subs:
        return
    m = re.search(r"https?://\S+", body or "")
    url = m.group(0) if m else "/"
    text = re.sub(r"https?://\S+", "", body or "").replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    threading.Thread(target=_bb_push_send, args=(subs, subject, text, url), daemon=True).start()


_bb_notify_push_old = notify


def notify(subject, body, to=None):
    r = _bb_notify_push_old(subject, body, to)
    try:
        _bb_push_for(subject, body, to or GMAIL)
    except Exception as e:
        print("push:", e)
    return r


@app.route("/push/sub", methods=["POST"])
def bb_push_sub():
    j = request.get_json(silent=True) or {}
    sub, sid, rt, role = j.get("sub"), str(j.get("sid", "")), str(j.get("rt", "")), j.get("role", "")
    if not isinstance(sub, dict) or not str(sub.get("endpoint", "")).startswith("https://"):
        return "bad subscription", 400
    d = load()
    shop = d.get(sid)
    if not shop:
        return "not found", 404
    if role == "owner":
        if not _bb_ok(sid, "", shop):
            return "log in first", 403
        tgt = shop
    else:
        tgt = next((b for b in shop.get("bookings", []) if b.get("rt") == rt), None)
        if not tgt:
            return "not found", 404
    lst = [s for s in tgt.get("push", []) if s.get("endpoint") != sub["endpoint"]]
    lst.append({"endpoint": sub["endpoint"], "keys": sub.get("keys", {})})
    tgt["push"] = lst[-5:]
    save(d)
    return "ok"


@app.route("/push/test/<sid>", methods=["POST"])
def bb_push_test(sid):
    d = load()
    shop = d.get(sid)
    if not shop or not _bb_ok(sid, "", shop):
        return "log in first", 403
    if not shop.get("push"):
        return "no devices yet", 400
    import threading
    threading.Thread(target=_bb_push_send, args=(list(shop["push"]), "Business-Bookie test", "Notifications are working for " + shop.get("name", "your business") + ".", request.host_url + "d/" + sid), daemon=True).start()
    return "sent"


def _bb_push_box(sid, rt, role):
    key = os.environ.get("VAPID_PUBLIC", "")
    if not key:
        return ""
    test = ("<button type='button' onclick='bbPushTest()' style='margin-top:6px;background:#fff;color:#1a6dff;border:2px solid #1a6dff'>Send me a test notification</button>" if role == "owner" else "")
    return ("<div class='card' id='bbpush'><b>&#128276; Notifications</b><div style='font-size:13px;color:#556;margin:4px 0'>" +
            ("Get an alert on this phone for new bookings, time-change requests and cancellations." if role == "owner" else "Get an alert on this phone if your appointment changes.") +
            "</div><button type='button' onclick='bbPush()'>&#128276; Turn on notifications</button>" + test + "<div id='bbps' style='font-size:13px;color:#556;margin-top:6px'></div></div>"
            "<script>(function(){var K='" + key + "',SID='" + sid + "',RT='" + rt + "',ROLE='" + role + "';"
            "function u(b){var p='='.repeat((4-b.length%4)%4),s=(b+p).replace(/-/g,'+').replace(/_/g,'/'),r=atob(s),o=new Uint8Array(r.length);for(var i=0;i<r.length;i++)o[i]=r.charCodeAt(i);return o}"
            "function say(t){document.getElementById('bbps').textContent=t}"
            "window.bbPush=async function(){try{if(!('serviceWorker' in navigator)||!('PushManager' in window)||!('Notification' in window)){say('This browser cannot show notifications. On iPhone, add this site to your Home Screen first, then open it from there.');return}"
            "var p=await Notification.requestPermission();if(p!=='granted'){say('Notifications are blocked. Allow them for this site in your browser settings, then try again.');return}"
            "var r=await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;"
            "var s=await r.pushManager.getSubscription()||await r.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:u(K)});"
            "var x=await fetch('/push/sub',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sub:s.toJSON(),sid:SID,rt:RT,role:ROLE})});"
            "say(x.ok?'\\u2705 Notifications are on for this device.':'Could not turn on notifications ('+(await x.text())+').')}catch(e){say('Could not turn on notifications: '+e)}};"
            "window.bbPushTest=async function(){var x=await fetch('/push/test/'+SID,{method:'POST'});say(x.ok?'Test sent. It should pop up in a few seconds.':'Test failed: '+(await x.text()))};"
            "})();</script>")


@app.after_request
def _bb_push_inject(resp):
    try:
        if resp.status_code != 200 or resp.mimetype != "text/html" or not os.environ.get("VAPID_PUBLIC"):
            return resp
        import re
        h = resp.get_data(as_text=True)
        if "id='bbpush'" in h:
            return resp
        parts = request.path.strip("/").split("/")
        box = ""
        if request.method == "GET" and parts[0] == "d" and len(parts) == 2 and "Block off time" in h:
            box = _bb_push_box(parts[1], "", "owner")
        else:
            m = re.search(r"/(?:m|r|neg)/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", h if parts[0] != "m" else request.path)
            if m and (parts[0] in ("m", "neg") or "booked" in h.lower()):
                box = _bb_push_box(m.group(1), m.group(2), "customer")
        if box:
            i = h.rfind("</body>")
            resp.set_data(h[:i] + box + h[i:] if i >= 0 else h + box)
    except Exception as e:
        print("push inject:", e)
    return resp


def _bb_is_hash(p):
    return isinstance(p, str) and (p.startswith("pbkdf2:") or p.startswith("scrypt:"))


def _bb_hash(p):
    if not p or _bb_is_hash(p):
        return p
    from werkzeug.security import generate_password_hash
    return generate_password_hash(p, method="pbkdf2:sha256")


def _bb_pw_ok(stored, given):
    if not stored or not given:
        return False
    if _bb_is_hash(stored):
        from werkzeug.security import check_password_hash
        try:
            return check_password_hash(stored, given)
        except Exception:
            return False
    import hmac
    return hmac.compare_digest(str(stored), str(given))


_bb_save_plain = save


def save(d):
    try:
        for v in d.values():
            if isinstance(v, dict) and v.get("pw") and not _bb_is_hash(v["pw"]):
                v["pw"] = _bb_hash(v["pw"])
    except Exception as e:
        print("hash on save:", e)
    return _bb_save_plain(d)


_BB_FAILS = {}


@app.before_request
def _bb_login_guard():
    try:
        if request.method != "POST" or request.path != "/login":
            return None
        import time as _t
        em = (request.form.get("em") or "").strip().lower()
        pw = request.form.get("pw", "")
        if not em:
            return None
        cnt, until = _BB_FAILS.get(em, (0, 0))
        if until and _t.time() < until:
            mins = int((until - _t.time()) // 60) + 1
            return S + ("<h1>Too many tries</h1><p>For your security, log in is paused for this email for about " + str(mins) +
                        " more minute" + ("s" if mins != 1 else "") + ".</p><p>Forgot your password? <a href='/forgot'>Reset it here</a>.</p><a href='/login'>Back</a>"), 429
        ok = any((v.get("email") or "").strip().lower() == em and _bb_pw_ok(v.get("pw"), pw) for v in load().values())
        if ok:
            _BB_FAILS.pop(em, None)
        else:
            cnt += 1
            _BB_FAILS[em] = (cnt, _t.time() + 15 * 60 if cnt >= 5 else 0)
    except Exception as e:
        print("login guard:", e)
    return None


def _bb_hst_now():
    return datetime.utcnow() - timedelta(hours=10)


def _bb_slot_min(shop):
    for k in ("slot", "slot_min", "minutes"):
        try:
            v = int(shop.get(k) or 0)
            if 5 <= v <= 600:
                return v
        except Exception:
            pass
    return 60


def _bb_cal_times(shop, b):
    st = datetime.strptime(b["when"], "%Y-%m-%d %H:%M") + timedelta(hours=10)
    en = st + timedelta(minutes=_bb_slot_min(shop))
    f = "%Y%m%dT%H%M%SZ"
    return st.strftime(f), en.strftime(f)


@app.route("/ics/<sid>/<rt>")
def bb_ics(sid, rt):
    shop = load().get(sid) or {}
    b = next((x for x in shop.get("bookings", []) if x.get("rt") == rt), None)
    if not b:
        return S + "<h1>Booking not found</h1>", 404
    try:
        st, en = _bb_cal_times(shop, b)
    except Exception:
        return S + "<h1>This booking has no valid time</h1>", 400
    esc = lambda s: str(s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")
    desc = (b.get("service", "") + " at " + shop.get("name", "") + ("\nCall: " + shop["bphone"] if shop.get("bphone") else "") +
            "\nManage your booking: " + request.host_url + "m/" + sid + "/" + rt)
    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Business-Bookie//EN", "METHOD:PUBLISH", "BEGIN:VEVENT",
        "UID:" + sid + "-" + rt + "@business-bookie.com", "DTSTAMP:" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "DTSTART:" + st, "DTEND:" + en,
        "SUMMARY:" + esc(b.get("service", "Appointment") + " at " + shop.get("name", "")),
        "LOCATION:" + esc(shop.get("addr", "")), "DESCRIPTION:" + esc(desc),
        "BEGIN:VALARM", "TRIGGER:-PT2H", "ACTION:DISPLAY", "DESCRIPTION:" + esc("Appointment at " + shop.get("name", "")), "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", ""])
    return app.response_class(ics, mimetype="text/calendar", headers={"Content-Disposition": "attachment; filename=appointment.ics"})


def _bb_gcal_link(shop, b, sid, rt):
    from urllib.parse import quote as _q
    st, en = _bb_cal_times(shop, b)
    return ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _q(b.get("service", "Appointment") + " at " + shop.get("name", "")) +
            "&dates=" + st + "/" + en + "&location=" + _q(shop.get("addr", "")) +
            "&details=" + _q("Manage your booking: " + request.host_url + "m/" + sid + "/" + rt))


def _bb_cal_box(sid, rt):
    shop = load().get(sid) or {}
    b = next((x for x in shop.get("bookings", []) if x.get("rt") == rt), None)
    if not b:
        return ""
    try:
        g = _bb_gcal_link(shop, b, sid, rt)
    except Exception:
        return ""
    btn = "display:block;text-align:center;padding:12px;margin:6px 0;border:2px solid #1a6dff;border-radius:10px;text-decoration:none;font-weight:700"
    return ("<div class='card' id='bbcal'><b>&#128197; Add to your calendar</b>"
            "<a href='" + str(escape(g)) + "' target='_blank' rel='noopener' style='" + btn + "'>Google Calendar</a>"
            "<a href='/ics/" + sid + "/" + rt + "' style='" + btn + "'>Apple / Outlook / other (.ics)</a></div>")


@app.after_request
def _bb_cal_inject(resp):
    try:
        if resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        import re
        h = resp.get_data(as_text=True)
        if "id='bbcal'" in h:
            return resp
        parts = request.path.strip("/").split("/")
        m = None
        if parts[0] == "m" and len(parts) == 3:
            m = (parts[1], parts[2])
        elif "booked" in h.lower():
            x = re.search(r"/(?:m|r)/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", h)
            m = (x.group(1), x.group(2)) if x else None
        if m:
            box = _bb_cal_box(m[0], m[1])
            if box:
                i = h.find("id='bbpush'")
                i = h.rfind("<div", 0, i) if i >= 0 else h.rfind("</body>")
                resp.set_data(h[:i] + box + h[i:] if i >= 0 else h + box)
    except Exception as e:
        print("cal inject:", e)
    return resp


_bb_notify_cal_old = notify


def notify(subject, body, to=None):
    try:
        import re
        m = re.search(r"(https?://[^\s/]+)/m/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", body or "")
        if m and "/ics/" not in body:
            body = body + "\n\nAdd it to your calendar: " + m.group(1) + "/ics/" + m.group(2) + "/" + m.group(3)
    except Exception as e:
        print("cal mail:", e)
    return _bb_notify_cal_old(subject, body, to)


_BB_REM = {"last": 0.0}


def _bb_run_reminders(host):
    now = _bb_hst_now()
    d = load()
    due = []
    for sid, shop in d.items():
        for b in shop.get("bookings", []):
            if b.get("done") or not b.get("email") or not b.get("when"):
                continue
            try:
                hrs = (datetime.strptime(b["when"], "%Y-%m-%d %H:%M") - now).total_seconds() / 3600
            except Exception:
                continue
            if 20 <= hrs <= 24 and not b.get("rem24"):
                b["rem24"] = True
                due.append(("24", sid, shop, dict(b)))
            elif 0 < hrs <= 2.5 and not b.get("rem2"):
                b["rem2"] = True
                b["rem24"] = True
                due.append(("2", sid, shop, dict(b)))
    if not due:
        return 0
    save(d)
    for kind, sid, shop, b in due:
        try:
            wh = _bb_fmt(b["when"]) if "_bb_fmt" in globals() else b["when"]
            when_word = "tomorrow" if kind == "24" else "in about 2 hours"
            body = ("Hi " + b.get("name", "") + ",\n\nReminder: your " + b.get("service", "appointment") + " at " + shop.get("name", "") + " is " + when_word +
                    " (" + wh + ")." + ("\nAddress: " + shop["addr"] if shop.get("addr") else "") +
                    ("\nQuestions? Call " + shop["bphone"] if shop.get("bphone") else "") +
                    "\n\nNeed to reschedule or cancel? " + host + "m/" + sid + "/" + b.get("rt", ""))
            notify("Reminder: " + b.get("service", "your appointment") + " at " + shop.get("name", "") + " " + when_word, body, b["email"])
        except Exception as e:
            print("reminder send:", e)
    return len(due)


@app.route("/cron/reminders")
def bb_cron_reminders():
    import time as _t
    _BB_REM["last"] = _t.time()
    n = _bb_run_reminders(request.host_url)
    return app.response_class("reminders sent: " + str(n) + "\n", mimetype="text/plain")


@app.before_request
def _bb_reminder_tick():
    try:
        import time as _t
        if request.method == "GET" and _t.time() - _BB_REM["last"] > 300 and not request.path.startswith(("/cron/", "/sw.js", "/favicon", "/icon-", "/manifest")):
            _BB_REM["last"] = _t.time()
            _bb_run_reminders(request.host_url)
    except Exception as e:
        print("reminder tick:", e)
    return None


app.config["MAX_FORM_MEMORY_SIZE"] = 2000000


_bb_bphone_in_old4 = _bb_bphone_in


def _bb_bphone_in(shop):
    has = bool(shop.get("photo"))
    return (_bb_bphone_in_old4(shop) +
            "<h3>Your page</h3><p>About your business (shows on your booking page)</p>"
            "<textarea name='about' rows='4' maxlength='600' placeholder='What you do, specialties, parking tips...'>" + str(escape(shop.get("about", ""))) + "</textarea>"
            "<p>Photo or logo</p>" + ("<img src='/photo/" + str(escape(shop.get("_sid", ""))) + "' style='max-width:160px;border-radius:10px;display:block;margin:4px 0' alt=''>" if has and shop.get("_sid") else "") +
            "<input type='file' accept='image/*' id='bbphotofile'><input type='hidden' name='photo_data' id='bbphotodata'>"
            "<div id='bbphotomsg' style='font-size:13px;color:#556'></div>" +
            ("<label style='display:flex;gap:8px;align-items:center;font-size:14px'><input type='checkbox' name='photo_rm' value='1' style='width:auto'> Remove current photo</label>" if has else "") +
            "<script>(function(){var f=document.getElementById('bbphotofile');if(!f)return;f.addEventListener('change',function(){var x=f.files[0];if(!x)return;"
            "var r=new FileReader();r.onload=function(){var im=new Image();im.onload=function(){var m=800,w=im.width,h=im.height;if(w>m||h>m){var s=Math.min(m/w,m/h);w=Math.round(w*s);h=Math.round(h*s)}"
            "var c=document.createElement('canvas');c.width=w;c.height=h;var g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,w,h);g.drawImage(im,0,0,w,h);"
            "var u=c.toDataURL('image/jpeg',0.75);if(u.length>350000)u=c.toDataURL('image/jpeg',0.5);if(u.length>350000){document.getElementById('bbphotomsg').textContent='That photo is too big. Try a smaller one.';return}document.getElementById('bbphotodata').value=u;"
            "document.getElementById('bbphotomsg').textContent='Photo ready. Tap Save to keep it.'};im.src=r.result};r.readAsDataURL(x)})})();</script>")


@app.before_request
def _bb_tag_sid():
    try:
        p = request.path.strip("/").split("/")
        if len(p) == 2 and p[0] == "edit":
            globals()["_BB_EDIT_SID"] = p[1]
    except Exception:
        pass
    return None


_bb_load_pg = load


def load():
    d = _bb_load_pg()
    try:
        sid = globals().get("_BB_EDIT_SID")
        if sid and sid in d and isinstance(d[sid], dict):
            d[sid]["_sid"] = sid
    except Exception:
        pass
    return d


_bb_save_pg = save


def save(d):
    try:
        for v in d.values():
            if isinstance(v, dict):
                v.pop("_sid", None)
    except Exception:
        pass
    return _bb_save_pg(d)


@app.route("/photo/<sid>")
def bb_photo(sid):
    import base64
    shop = load().get(sid) or {}
    p = shop.get("photo") or ""
    if not p.startswith("data:image/jpeg;base64,"):
        return "", 404
    try:
        data = base64.b64decode(p.split(",", 1)[1])
    except Exception:
        return "", 404
    r = app.response_class(data, mimetype="image/jpeg")
    r.headers["Cache-Control"] = "public, max-age=300"
    return r


def _bb_page_extras(sid, shop):
    from urllib.parse import quote as _q
    out = ""
    if shop.get("photo"):
        out += "<img src='/photo/" + sid + "' alt='" + str(escape(shop.get("name", ""))) + "' style='width:100%;max-height:260px;object-fit:cover;border-radius:14px;margin:6px 0 10px'>"
    if shop.get("about"):
        out += "<p style='white-space:pre-line;line-height:1.5'>" + str(escape(shop["about"])) + "</p>"
    if shop.get("addr"):
        out += ("<a href='https://www.google.com/maps/search/?api=1&query=" + _q(shop["addr"]) + "' target='_blank' rel='noopener' "
                "style='display:inline-block;margin:2px 0 10px;font-weight:700'>&#128205; Get directions</a>")
    return out


@app.after_request
def _bb_page_inject(resp):
    try:
        if request.method != "GET" or resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        p = request.path.strip("/").split("/")
        if len(p) == 2 and p[0] == "b":
            shop = load().get(p[1])
            if not shop:
                return resp
            h = resp.get_data(as_text=True)
            if "id='bbpage'" in h:
                return resp
            ex = _bb_page_extras(p[1], shop)
            if ex:
                i = h.find("</h1>")
                if i >= 0:
                    h = h[:i + 5] + "<div id='bbpage'>" + ex + "</div>" + h[i + 5:]
            nm = str(escape(shop.get("name", "Business-Bookie")))
            ds = str(escape((shop.get("about") or "Book an appointment online with " + shop.get("name", "us") + ".")[:200]))
            img = request.host_url + ("photo/" + p[1] if shop.get("photo") else "icon-512.png")
            og = ("<meta property='og:type' content='website'><meta property='og:title' content='" + nm + " | Book online'>"
                  "<meta property='og:description' content='" + ds + "'><meta property='og:image' content='" + img + "'>"
                  "<meta property='og:url' content='" + request.base_url + "'><meta name='description' content='" + ds + "'>"
                  "<meta name='twitter:card' content='summary_large_image'>")
            h = h.replace("</head>", og + "</head>", 1) if "</head>" in h else og + h
            resp.set_data(h)
        elif request.path == "/":
            h = resp.get_data(as_text=True)
            if "og:title" not in h:
                og = ("<meta property='og:type' content='website'><meta property='og:title' content='Business-Bookie | Online booking for local businesses'>"
                      "<meta property='og:description' content='Book appointments with local businesses, or sign up your business for free.'>"
                      "<meta property='og:image' content='" + request.host_url + "icon-512.png'><meta name='description' content='Book appointments with local businesses, or sign up your business for free.'>")
                h = h.replace("</head>", og + "</head>", 1) if "</head>" in h else og + h
                resp.set_data(h)
    except Exception as e:
        print("page inject:", e)
    return resp


# ===== BB UPGRADE: hours per day, service length, waitlist, owner stats, time zones =====
_BB_F = "%Y-%m-%d %H:%M"
_BB_DAYN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_BB_TZS = [("Pacific/Honolulu", "Hawaii", -10, False), ("America/Anchorage", "Alaska", -9, True),
           ("America/Los_Angeles", "Pacific", -8, True), ("America/Phoenix", "Arizona", -7, False),
           ("America/Denver", "Mountain", -7, True), ("America/Chicago", "Central", -6, True),
           ("America/New_York", "Eastern", -5, True)]
_BB_DURS = [15, 20, 30, 45, 60, 75, 90, 120, 150, 180, 240, 300, 360, 480]


def _bb_tzinfo(shop):
    k = (shop or {}).get("tz") or "Pacific/Honolulu"
    for t in _BB_TZS:
        if t[0] == k:
            return t
    return _BB_TZS[0]


def _bb_nth_sunday(y, mo, n):
    d = datetime(y, mo, 1)
    d += timedelta(days=(6 - d.weekday()) % 7)
    return d + timedelta(days=7 * (n - 1))


def _bb_is_dst(local_std):
    y = local_std.year
    return _bb_nth_sunday(y, 3, 2).replace(hour=2) <= local_std < _bb_nth_sunday(y, 11, 1).replace(hour=1)


def _bb_utc_off(shop, utc):
    t = _bb_tzinfo(shop)
    return t[2] + (1 if t[3] and _bb_is_dst(utc + timedelta(hours=t[2])) else 0)


def _bb_local_now(shop):
    u = datetime.utcnow()
    return u + timedelta(hours=_bb_utc_off(shop, u))


def _bb_local_to_utc(shop, loc):
    t = _bb_tzinfo(shop)
    return loc - timedelta(hours=t[2] + (1 if t[3] and _bb_is_dst(loc) else 0))


def _bb_hm(s):
    try:
        h, m = [int(x) for x in str(s).split(":")[:2]]
        if 0 <= h <= 23 and 0 <= m <= 59:
            return (h, m)
    except Exception:
        pass
    return None


def _bb_hours(shop):
    out = {}
    hv = shop.get("hours")
    if isinstance(hv, dict) and hv:
        for k, v in hv.items():
            try:
                i, o, c = int(k), _bb_hm(v[0]), _bb_hm(v[1])
                if o and c and 0 <= i <= 6 and c > o:
                    out[i] = (o, c)
            except Exception:
                pass
        if out:
            return out
    try:
        days = [int(x) for x in shop.get("days", [])] or [0, 1, 2, 3, 4]
    except Exception:
        days = [0, 1, 2, 3, 4]
    o = _bb_hm(shop.get("open", "09:00")) or (9, 0)
    c = _bb_hm(shop.get("close", "17:00")) or (17, 0)
    return {i: (o, c) for i in days if 0 <= i <= 6}


def _bb_t12(hm):
    h, m = hm
    return "%d:%02d %s" % ((h % 12) or 12, m, "AM" if h < 12 else "PM")


def _bb_hours_text(shop, sep=" · "):
    hrs = _bb_hours(shop)
    groups = []
    for i in range(7):
        v = hrs.get(i)
        if groups and groups[-1][2] == v and groups[-1][1] == i - 1:
            groups[-1][1] = i
        else:
            groups.append([i, i, v])
    parts = []
    for a, b, v in groups:
        if v:
            nm = _BB_DAYN[a] if a == b else _BB_DAYN[a] + "–" + _BB_DAYN[b]
            parts.append(nm + " " + _bb_t12(v[0]) + "–" + _bb_t12(v[1]))
    txt = sep.join(parts) or "Not set"
    if _bb_tzinfo(shop)[0] != "Pacific/Honolulu":
        txt += " (" + _bb_tzinfo(shop)[1] + " time)"
    return txt


def _bb_step(shop):
    try:
        v = int(shop.get("slot") or 30)
        return v if 5 <= v <= 600 else 30
    except Exception:
        return 30


def _bb_dur(shop, svc):
    try:
        v = int((shop.get("dur") or {}).get(svc) or 0)
        if 5 <= v <= 720:
            return v
    except Exception:
        pass
    return 0


def _bb_len(shop, svc):
    return _bb_dur(shop, svc) or _bb_step(shop)


def _bb_len_txt(m):
    if m < 60:
        return str(m) + " min"
    return (str(m // 60) + " hr" + (" " + str(m % 60) + " min" if m % 60 else ""))


def _bb_gv(k):
    try:
        from flask import g
        return g.get(k)
    except Exception:
        return None


def _bb_pdt(w):
    try:
        return datetime.strptime(str(w).replace("T", " ")[:16], _BB_F)
    except Exception:
        return None


def _bb_is_cxl(b):
    return bool(b.get("cancelled") or b.get("canceled") or str(b.get("status", "")).lower().startswith("cancel"))


def _bb_full_base(shop):
    cap = 1
    if _bb_guests_on(shop):
        try:
            cap = max(1, int(shop.get("tables") or 5))
        except Exception:
            cap = 5
    skip = _bb_gv("bb_skip_rt")
    c = {}
    for x in shop.get("bookings", []):
        if (skip and x.get("rt") == skip) or _bb_is_cxl(x):
            continue
        w = x.get("when")
        st = _bb_pdt(w)
        keys = {w}
        if st:
            en = st + timedelta(minutes=_bb_len(shop, x.get("service")))
            t = st - timedelta(minutes=st.minute % 5)
            while t < en:
                keys.add(t.strftime(_BB_F))
                t += timedelta(minutes=5)
        for k in keys:
            c[k] = c.get(k, 0) + 1
    return {w for w, k in c.items() if k >= cap}


def _bb_range_ok(shop, st, ln, taken=None, check_blocks=False):
    if taken is None:
        taken = _bb_full(shop)
    if st.strftime(_BB_F) in taken:
        return False
    en = st + timedelta(minutes=ln)
    t = st - timedelta(minutes=st.minute % 5)
    while t < en:
        if t.strftime(_BB_F) in taken:
            return False
        t += timedelta(minutes=5)
    if check_blocks:
        t = st + timedelta(minutes=_bb_step(shop))
        while t < en:
            try:
                if _bb_blocked(shop, t.strftime(_BB_F)):
                    return False
            except Exception:
                pass
            t += timedelta(minutes=_bb_step(shop))
    return True


def _bb_slots_for(shop, svc=None):
    hrs = _bb_hours(shop)
    step = _bb_step(shop)
    exact = _bb_dur(shop, svc) if svc else 0
    ln = exact or step
    taken = _bb_full(shop)
    now = _bb_local_now(shop)
    out = []
    for dd in range(14):
        day = now + timedelta(days=dd)
        wd = day.weekday()
        if wd not in hrs:
            continue
        (oh, om), (ch, cm) = hrs[wd]
        cur = day.replace(hour=oh, minute=om, second=0, microsecond=0)
        end = day.replace(hour=ch, minute=cm, second=0, microsecond=0)
        while cur < end:
            if cur > now and (not exact or cur + timedelta(minutes=exact) <= end) and _bb_range_ok(shop, cur, ln, taken, bool(exact)):
                out.append((cur.strftime(_BB_F), _BB_DAYN[wd] + " " + day.strftime("%b %d") + " at " + cur.strftime("%I:%M %p")))
            cur += timedelta(minutes=step)
    return out


def _bb_build_slots_orig(shop):
    return _bb_slots_for(shop, _bb_gv("bb_svc"))


def _bb_open_days(shop, n=14):
    hrs = _bb_hours(shop)
    now = _bb_local_now(shop)
    out = []
    for dd in range(n):
        day = now + timedelta(days=dd)
        if day.weekday() in hrs:
            out.append((day.strftime("%Y-%m-%d"), _BB_DAYN[day.weekday()] + " " + day.strftime("%b %d")))
    return out


def _bb_hours_from_form(f):
    hours = {}
    on = f.getlist("hd")
    for i in range(7):
        if str(i) not in on:
            continue
        o, c = _bb_hm(f.get("ho_%d" % i)), _bb_hm(f.get("hc_%d" % i))
        if not o or not c:
            return None, "Set opening and closing times for " + _BB_DAYN[i] + "."
        if c <= o:
            return None, "On " + _BB_DAYN[i] + ", closing time must be after opening time."
        hours[str(i)] = ["%02d:%02d" % o, "%02d:%02d" % c]
    return hours, ""


@app.before_request
def _bb_v2_before():
    try:
        from flask import g
        p = request.path.strip("/").split("/")
        if request.method == "POST" and len(p) == 2 and p[0] == "book":
            g.bb_svc = request.form.get("service")
            shop = load().get(p[1])
            st = _bb_pdt(request.form.get("when", ""))
            if shop and st and not _bb_range_ok(shop, st, _bb_len(shop, g.bb_svc), None, bool(_bb_dur(shop, g.bb_svc))):
                return _bb_taken(p[1], shop)
        elif len(p) == 3 and p[0] in ("m", "neg"):
            g.bb_skip_rt = p[2]
            shop = load().get(p[1]) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == p[2]), None)
            if b:
                g.bb_svc = b.get("service")
        elif request.method == "POST" and len(p) == 2 and p[0] == "edit" and request.form.get("bb_hours") == "1":
            sid = p[1]
            if not _bb_sess.get("own_" + sid):
                return None
            f = request.form
            hours, err = _bb_hours_from_form(f)
            if err:
                return S + "<h1>Hours not saved</h1><p>" + str(escape(err)) + "</p><a href='javascript:history.back()'>Go back</a>"
            if not hours:
                return None
            d = load()
            shop = d.get(sid)
            if not shop:
                return None
            names = set()
            i = 0
            while ("sn%d" % i) in f:
                n = f.get("sn%d" % i, "").strip()[:60]
                if n and not f.get("sx%d" % i):
                    names.add(n)
                i += 1
            if not names:
                names = set((shop.get("services") or {}).keys())
            dur = {}
            i = 0
            while ("durn_%d" % i) in f:
                n = f.get("durn_%d" % i, "")
                v = f.get("dur_%d" % i, "")
                if n in names and v.isdigit() and 5 <= int(v) <= 720:
                    dur[n] = int(v)
                i += 1
            shop["hours"] = hours
            shop["dur"] = dur
            tz = f.get("tz", "")
            if any(t[0] == tz for t in _BB_TZS):
                shop["tz"] = tz
            save(d)
            from werkzeug.datastructures import ImmutableMultiDict
            _f = f.to_dict(flat=False)
            _f["days"] = sorted(hours.keys())
            _f["open"] = [min(v[0] for v in hours.values())]
            _f["close"] = [max(v[1] for v in hours.values())]
            request.form = ImmutableMultiDict([(k, v) for k, vs in _f.items() for v in vs])
    except Exception as e:
        print("v2 before:", e)
    return None


_bb_bphone_in_old5 = _bb_bphone_in


def _bb_bphone_in(shop):
    base = _bb_bphone_in_old5(shop)
    if not isinstance(shop, dict) or "services" not in shop:
        return base
    e = lambda s: str(escape(s))
    hrs = _bb_hours(shop)
    ti = "style='width:auto;display:inline-block;margin:2px 4px'"
    rows = ""
    for i in range(7):
        v = hrs.get(i)
        o = "%02d:%02d" % v[0] if v else "09:00"
        c = "%02d:%02d" % v[1] if v else "17:00"
        rows += ("<div style='display:flex;align-items:center;flex-wrap:wrap;gap:4px;padding:6px 0;border-bottom:1px solid #eef'>"
                 "<label style='display:flex;align-items:center;gap:6px;min-width:70px;font-weight:700'><input type='checkbox' name='hd' value='" + str(i) + "'" + (" checked" if v else "") + " style='width:auto'> " + _BB_DAYN[i] + "</label>"
                 "<input type='time' name='ho_%d' value='%s' %s> to <input type='time' name='hc_%d' value='%s' %s></div>" % (i, o, ti, i, c, ti))
    svs = ""
    for j, n in enumerate((shop.get("services") or {}).keys()):
        cur = _bb_dur(shop, n)
        op = "<option value=''>Same as time slot (" + str(_bb_step(shop)) + " min)</option>" + "".join(
            "<option value='" + str(m) + "'" + (" selected" if m == cur else "") + ">" + _bb_len_txt(m) + "</option>" for m in _BB_DURS)
        svs += ("<div style='margin:6px 0'><b>" + e(n) + "</b><input type='hidden' name='durn_%d' value='%s'><select name='dur_%d'>%s</select></div>" % (j, e(n), j, op))
    tzo = "".join("<option value='" + t[0] + "'" + (" selected" if t[0] == _bb_tzinfo(shop)[0] else "") + ">" + t[1] + "</option>" for t in _BB_TZS)
    js = ("<script>document.addEventListener('DOMContentLoaded',function(){var sec=document.getElementById('bbhrs');if(!sec)return;var f=sec.closest('form');if(!f)return;"
          "var els=[].slice.call(f.querySelectorAll('input[name=days],input[name=open],input[name=close]')).filter(function(x){return !sec.contains(x)});if(!els.length)return;"
          "var hide=function(x){if(x&&!x.contains(sec)&&!sec.contains(x))x.style.display='none'};"
          "var first=els[0].closest('label')||els[0];var cap=first.previousElementSibling;var anchor=first;"
          "if(cap&&!cap.querySelector('input,select,textarea')&&/^(P|B|DIV|SPAN|LABEL)$/.test(cap.tagName)){anchor=cap}"
          "var hd=anchor.previousElementSibling;if(hd&&/^H[1-6]$/.test(hd.tagName)&&/hour/i.test(hd.textContent)){hide(hd);}"
          "anchor.parentNode.insertBefore(sec,anchor);"
          "els.forEach(function(x){x.required=false;var l=x.closest('label');var t=(l&&l!==f)?l:x;hide(t);var p=t.previousElementSibling;"
          "if(p&&p!==sec&&!p.querySelector('input,select,textarea')&&/^(P|B|SPAN)$/.test(p.tagName))hide(p)});"
          "var sl=f.querySelector('select[name=slot]'),dh=document.getElementById('bbdurh');if(sl&&dh){var sp=sl.previousElementSibling;"
          "if(sp&&sp.tagName==='P'){sp.textContent='Booking times start every';dh.parentNode.insertBefore(sp,dh)}dh.parentNode.insertBefore(sl,dh)}});</script>")
    return (base + "<div id='bbhrs'><input type='hidden' name='bb_hours' value='1'>"
            "<h3>Open hours</h3><p style='font-size:13px;color:#556'>Tick the days you're open and set the hours for each day.</p>" + rows +
            "<p>Time zone</p><select name='tz'>" + tzo + "</select>"
            "<h3 id='bbdurh'>How long each service takes</h3><p style='font-size:13px;color:#556'>Longer services block more time, so nobody gets booked on top of them. New services can be set after you save.</p>" + svs +
            "</div>" + js)


def _bb_svc_script(shop):
    import json
    data, lens = {}, {}
    for n in (shop.get("services") or {}).keys():
        m = _bb_dur(shop, n)
        if m:
            lens[n] = _bb_len_txt(m)
            data[n] = [v for v, _ in _bb_slots_for(shop, n) if not _bb_blocked(shop, v)]
    if not lens:
        return ""
    js = json.dumps({"d": data, "n": lens}).replace("</", "<\\/")
    return ("<script>(function(){var X=" + js + ",s=document.querySelector('select[name=service]'),w=document.querySelector('select[name=when]');if(!s||!w)return;"
            "[].forEach.call(s.options,function(o){if(X.n[o.value])o.text+=' ('+X.n[o.value]+')'});"
            "var all=[].map.call(w.options,function(o){return [o.value,o.text]});"
            "function f(){var ok=X.d[s.value];w.innerHTML='';all.forEach(function(a){if(!ok||ok.indexOf(a[0])>=0){var o=document.createElement('option');o.value=a[0];o.text=a[1];w.appendChild(o)}});"
            "if(!w.options.length){var o=document.createElement('option');o.value='';o.text='No open times for this service. Try the waitlist below.';w.appendChild(o)}}"
            "s.addEventListener('change',f);f()})();</script>")


def _bb_wait_form(sid, shop):
    e = lambda s: str(escape(s))
    days = _bb_open_days(shop)
    if not days:
        return ""
    so = "".join("<option value='" + e(n) + "'>" + e(n) + "</option>" for n in (shop.get("services") or {}).keys())
    do = "".join("<option value='" + v + "'>" + lab + "</option>" for v, lab in days)
    return ("<div id='bbwait' style='background:#f4f7ff;border:1px solid #cfdcff;border-radius:12px;padding:14px;margin:16px 0'>"
            "<b>&#9203; Can't find a time that works?</b><p style='font-size:14px;margin:6px 0'>Join the waitlist. If a spot opens up on your day, we'll email you right away.</p>"
            "<form method='post' action='/wait/" + sid + "'><select name='date' required>" + do + "</select><select name='service'>" + so + "</select>"
            "<input name='name' placeholder='Your name' required><input name='email' type='email' placeholder='Email' required>"
            "<input name='phone' placeholder='Phone (optional)'><button>Join the waitlist</button></form></div>")


_bb_page_extras_old2 = _bb_page_extras


def _bb_page_extras(sid, shop):
    out = _bb_page_extras_old2(sid, shop)
    try:
        out += "<p style='font-size:14px;color:#334'><b>&#128336; Hours:</b> " + str(escape(_bb_hours_text(shop))) + "</p>"
    except Exception as ex:
        print("hours text:", ex)
    return out


@app.after_request
def _bb_v2_page(resp):
    try:
        if request.method != "GET" or resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        p = request.path.strip("/").split("/")
        if len(p) != 2 or p[0] not in ("b", "d"):
            return resp
        h = resp.get_data(as_text=True)
        shop = load().get(p[1])
        if not shop:
            return resp
        if p[0] == "b" and "id='bbwait'" not in h:
            i = h.find("action='/book/")
            j = h.find("</form>", i) if i >= 0 else -1
            add = _bb_wait_form(p[1], shop) + _bb_svc_script(shop)
            h = h[:j + 7] + add + h[j + 7:] if j >= 0 else h + add
            resp.set_data(h)
        elif p[0] == "d" and "total bookings" in h and "id='bbstats'" not in h:
            add = _bb_stats_html(shop) + _bb_wait_owner(shop)
            i = h.find("total bookings</div>")
            i = i + len("total bookings</div>") if i >= 0 else -1
            h = h[:i] + add + h[i:] if i >= 0 else h + add
            resp.set_data(h)
    except Exception as ex:
        print("v2 page:", ex)
    return resp


def _bb_stats_html(shop):
    now = _bb_local_now(shop)
    wk0 = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    wk1 = wk0 + timedelta(days=7)
    up = wk = mo = 0
    money = 0.0
    svc, dow = {}, [0] * 7
    for b in shop.get("bookings", []):
        st = _bb_pdt(b.get("when"))
        if not st or _bb_is_cxl(b):
            continue
        if st >= now:
            up += 1
        if wk0 <= st < wk1:
            wk += 1
        if st.year == now.year and st.month == now.month:
            mo += 1
            try:
                money += float(b.get("fee") or 0)
            except Exception:
                pass
            sv = b.get("service") or "Other"
            svc[sv] = svc.get(sv, 0) + 1
        dow[st.weekday()] += 1
    box = "flex:1;min-width:40%;background:#f4f7ff;border-radius:10px;padding:10px;text-align:center"
    num = "font-size:26px;font-weight:800;color:#1a6dff"
    cell = lambda n, lab: "<div style='" + box + "'><div style='" + num + "'>" + n + "</div><div style='font-size:13px'>" + lab + "</div></div>"
    top = sorted(svc.items(), key=lambda x: -x[1])[:3]
    tops = ", ".join(str(escape(k)) + " (" + str(v) + ")" for k, v in top) or "None yet"
    busy = _BB_DAYN[dow.index(max(dow))] if max(dow) else "Not enough data yet"
    return ("<div class='card' id='bbstats'><b>&#128202; Your numbers</b><div style='display:flex;flex-wrap:wrap;gap:8px;margin-top:8px'>" +
            cell(str(up), "upcoming") + cell(str(wk), "this week") + cell(str(mo), "this month") + cell("$%.0f" % money, "booked this month") +
            "</div><p style='font-size:14px;margin:10px 0 0'><b>Top services this month:</b> " + tops + "<br><b>Busiest day:</b> " + busy + "</p></div>")


def _bb_wait_owner(shop):
    today = _bb_local_now(shop).strftime("%Y-%m-%d")
    w = [x for x in shop.get("wait", []) if x.get("date", "") >= today]
    if not w:
        return ""
    e = lambda s: str(escape(s))
    rows = "".join("<p style='margin:6px 0;font-size:14px'><b>" + e(x.get("name", "")) + "</b> - " + e(x.get("service", "")) + " on " + e(x.get("date", "")) +
                   "<br>" + e(x.get("email", "")) + (" &middot; " + e(x["phone"]) if x.get("phone") else "") + "</p>" for x in sorted(w, key=lambda x: x.get("date", "")))
    return ("<div class='card' id='bbwaitlist'><b>&#9203; Waitlist (" + str(len(w)) + ")</b><p style='font-size:13px;color:#556;margin:4px 0'>"
            "These customers get an email automatically if a spot opens on their day.</p>" + rows + "</div>")


@app.route("/wait/<sid>", methods=["POST"])
def bb_wait(sid):
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    f = request.form
    nm = (f.get("name") or "").strip()[:80]
    em = (f.get("email") or "").strip()[:200]
    dt = (f.get("date") or "")[:10]
    sv = (f.get("service") or "").strip()[:60]
    back = "<a href='/b/" + sid + "'>Back to booking page</a>"
    if not nm or "@" not in em or dt not in [v for v, _ in _bb_open_days(shop, 30)]:
        return S + "<h1>Please fill in your name, email and day</h1>" + back
    today = _bb_local_now(shop).strftime("%Y-%m-%d")
    w = [x for x in shop.get("wait", []) if x.get("date", "") >= today]
    if any(x.get("email", "").lower() == em.lower() and x.get("date") == dt for x in w):
        return S + "<h1>You're already on the waitlist</h1><p>We'll email you if a spot opens that day.</p>" + back
    if len(w) >= 100:
        return S + "<h1>The waitlist is full</h1><p>Please check back later or pick another day.</p>" + back
    w.append({"name": nm, "email": em, "phone": (f.get("phone") or "").strip()[:30], "date": dt, "service": sv,
              "ts": _bb_local_now(shop).strftime(_BB_F)})
    shop["wait"] = w
    save(d)
    try:
        notify("Waitlist signup at " + shop.get("name", ""), nm + " wants " + (sv or "an appointment") + " on " + dt + ".\nEmail: " + em +
               ("\nPhone: " + w[-1]["phone"] if w[-1]["phone"] else "") + "\n\nThey'll get an email automatically if a spot opens that day.", shop.get("email") or None)
    except Exception as ex:
        print("wait notify:", ex)
    lab = next((l for v, l in _bb_open_days(shop, 30) if v == dt), dt)
    return S + "<h1>&#9989; You're on the waitlist!</h1><p>We'll email <b>" + str(escape(em)) + "</b> right away if a spot opens on <b>" + str(escape(lab)) + "</b> at " + str(escape(shop.get("name", ""))) + ".</p>" + back


def _bb_wl_freed(old, new):
    out = []
    for sid, shop in (new or {}).items():
        if not isinstance(shop, dict) or not shop.get("wait"):
            continue
        o = (old or {}).get(sid) or {}
        nm = {b.get("rt"): b for b in shop.get("bookings", []) if b.get("rt")}
        now = _bb_local_now(shop)
        for b in o.get("bookings", []):
            rt, w = b.get("rt"), b.get("when")
            st = _bb_pdt(w)
            if not rt or not st or st < now or _bb_is_cxl(b):
                continue
            nb = nm.get(rt)
            if nb is None or nb.get("when") != w or _bb_is_cxl(nb):
                out.append((sid, w))
    return out


def _bb_wl_notify(d, freed):
    changed = False
    try:
        host = request.host_url
    except Exception:
        host = "https://www.business-bookie.com/"
    for sid, w in freed:
        shop = d.get(sid) or {}
        day = str(w)[:10]
        keep = []
        for x in shop.get("wait", []):
            if x.get("date") == day and x.get("email"):
                changed = True
                try:
                    notify("A spot just opened at " + shop.get("name", ""),
                           "Hi " + x.get("name", "") + ",\n\nGood news: a time just opened up at " + shop.get("name", "") + " on " + day +
                           ". Spots go fast, so book it now:\n" + host + "b/" + sid +
                           "\n\nYou were on the waitlist, so we let you know first. You've been taken off the waitlist for that day.", x["email"])
                except Exception as ex:
                    print("waitlist mail:", ex)
            else:
                keep.append(x)
        shop["wait"] = keep
    return changed


_bb_save_wl = save


def save(d):
    freed = []
    try:
        if any(isinstance(v, dict) and v.get("wait") for v in d.values()):
            freed = _bb_wl_freed(load(), d)
    except Exception as ex:
        print("waitlist check:", ex)
    r = _bb_save_wl(d)
    if freed:
        try:
            if _bb_wl_notify(d, freed):
                _bb_save_wl(d)
        except Exception as ex:
            print("waitlist send:", ex)
    return r


def _bb_cal_times(shop, b):
    st = _bb_local_to_utc(shop, datetime.strptime(b["when"], _BB_F))
    en = st + timedelta(minutes=_bb_dur(shop, b.get("service")) or _bb_slot_min(shop))
    f = "%Y%m%dT%H%M%SZ"
    return st.strftime(f), en.strftime(f)


def _bb_run_reminders(host):
    d = load()
    due = []
    for sid, shop in d.items():
        if not isinstance(shop, dict):
            continue
        now = _bb_local_now(shop)
        for b in shop.get("bookings", []):
            if b.get("done") or not b.get("email") or not b.get("when") or _bb_is_cxl(b):
                continue
            try:
                hrs = (datetime.strptime(b["when"], _BB_F) - now).total_seconds() / 3600
            except Exception:
                continue
            if 20 <= hrs <= 24 and not b.get("rem24"):
                b["rem24"] = True
                due.append(("24", sid, shop, dict(b)))
            elif 0 < hrs <= 2.5 and not b.get("rem2"):
                b["rem2"] = True
                b["rem24"] = True
                due.append(("2", sid, shop, dict(b)))
    if not due:
        return 0
    save(d)
    for kind, sid, shop, b in due:
        try:
            wh = _bb_fmt(b["when"])
            when_word = "tomorrow" if kind == "24" else "in about 2 hours"
            body = ("Hi " + b.get("name", "") + ",\n\nReminder: your " + b.get("service", "appointment") + " at " + shop.get("name", "") + " is " + when_word +
                    " (" + wh + ")." + ("\nAddress: " + shop["addr"] if shop.get("addr") else "") +
                    ("\nQuestions? Call " + shop["bphone"] if shop.get("bphone") else "") +
                    "\n\nNeed to reschedule or cancel? " + host + "m/" + sid + "/" + b.get("rt", ""))
            notify("Reminder: " + b.get("service", "your appointment") + " at " + shop.get("name", "") + " " + when_word, body, b["email"])
        except Exception as ex:
            print("reminder send:", ex)
    return len(due)
# ===== END BB UPGRADE =====


# ===== BB UPGRADE 2: staff, clients, rebook, walk-in line, repeats, notes =====
_BB_CTX = {"staff": None}


def _bb_staff(shop):
    if not isinstance(shop, dict) or _bb_guests_on(shop):
        return []
    return [s for s in (shop.get("staff") or []) if isinstance(s, dict) and s.get("id")]


def _bb_staff_name(shop, sid_):
    return next((s.get("name", "") for s in _bb_staff(shop) if s["id"] == sid_), "")


def _bb_cur_staff():
    if _BB_CTX["staff"] is not None:
        return _BB_CTX["staff"]
    return _bb_gv("bb_staff") or ""


def _bb_b_staff(shop, b, st):
    v = b.get("staff")
    return v if v in [s["id"] for s in st] else st[0]["id"]


def _bb_marks(shop, bookings, skip=None):
    c = {}
    for x in bookings:
        if (skip and x.get("rt") == skip) or _bb_is_cxl(x):
            continue
        w = x.get("when")
        st = _bb_pdt(w)
        keys = {w}
        if st:
            en = st + timedelta(minutes=_bb_len(shop, x.get("service")))
            t = st - timedelta(minutes=st.minute % 5)
            while t < en:
                keys.add(t.strftime(_BB_F))
                t += timedelta(minutes=5)
        for k in keys:
            c[k] = c.get(k, 0) + 1
    return c


_bb_full_base_v1 = _bb_full_base


def _bb_full_base(shop):
    st = _bb_staff(shop)
    if not st:
        return _bb_full_base_v1(shop)
    skip = _bb_gv("bb_skip_rt")
    who = _bb_cur_staff()
    per = {s["id"]: set() for s in st}
    for b in shop.get("bookings", []):
        k = _bb_b_staff(shop, b, st)
        per[k] |= set(_bb_marks(shop, [b], skip).keys())
    if who in per:
        return per[who]
    sets = list(per.values())
    out = set(sets[0])
    for s in sets[1:]:
        out &= s
    return out


def _bb_as_staff(who, fn):
    old = _BB_CTX["staff"]
    _BB_CTX["staff"] = who
    try:
        return fn()
    finally:
        _BB_CTX["staff"] = old


_bb_slots_for_v1 = _bb_slots_for


def _bb_slots_for(shop, svc=None, staff=None):
    st = _bb_staff(shop)
    if not st:
        return _bb_slots_for_v1(shop, svc)
    if staff is None:
        staff = _bb_cur_staff()
    if staff and staff in [s["id"] for s in st]:
        return _bb_as_staff(staff, lambda: _bb_slots_for_v1(shop, svc))
    seen = {}
    for s in st:
        for v, lab in _bb_as_staff(s["id"], lambda: _bb_slots_for_v1(shop, svc)):
            seen[v] = lab
    return sorted(seen.items())


def _bb_free_staff(shop, st_dt, svc, want=""):
    st = _bb_staff(shop)
    ln = _bb_len(shop, svc)
    ids = [want] if want in [s["id"] for s in st] else [s["id"] for s in st]
    for i in ids:
        if _bb_as_staff(i, lambda: _bb_range_ok(shop, st_dt, ln, None, bool(_bb_dur(shop, svc)))):
            return i
    return None


def _bb_pkey(when, email):
    return str(when or "")[:16] + "|" + str(email or "").strip().lower()


@app.before_request
def _bb_v3_before():
    try:
        from flask import g
        p = request.path.strip("/").split("/")
        if request.method == "POST" and len(p) == 2 and p[0] == "book":
            d = load()
            shop = d.get(p[1])
            if not shop:
                return None
            f = request.form
            note = (f.get("note") or "").strip()[:300]
            st = _bb_staff(shop)
            pick = ""
            if st:
                want = f.get("staff", "")
                st_dt = _bb_pdt(f.get("when", ""))
                if st_dt:
                    pick = _bb_free_staff(shop, st_dt, f.get("service"), want)
                    if not pick:
                        g.bb_staff = want if want in [s["id"] for s in st] else ""
                        g.bb_svc = f.get("service")
                        return _bb_taken(p[1], shop)
                g.bb_staff = pick
            if pick or note:
                pend = {k: v for k, v in (shop.get("pend") or {}).items() if (_bb_pdt(k[:16]) or datetime(2000, 1, 1)) > datetime.utcnow() - timedelta(days=2)}
                pend[_bb_pkey(f.get("when"), f.get("email"))] = {"staff": pick, "note": note}
                shop["pend"] = pend
                save(d)
    except Exception as e:
        print("v3 before:", e)
    return None


_bb_save_v3 = save


def save(d):
    try:
        for v in d.values():
            if not isinstance(v, dict) or not v.get("bookings"):
                continue
            pend = v.get("pend") or {}
            st = _bb_staff(v)
            for b in v["bookings"]:
                k = _bb_pkey(b.get("when"), b.get("email"))
                if k in pend:
                    pe = pend.pop(k)
                    if pe.get("note") and not b.get("note"):
                        b["note"] = pe["note"]
                    if st and pe.get("staff") and not b.get("staff"):
                        b["staff"] = pe["staff"]
                if st and not b.get("staff") and _bb_pdt(b.get("when")):
                    others = [x for x in v["bookings"] if x is not b and x.get("staff")]
                    s2 = dict(v)
                    s2["bookings"] = others
                    b["staff"] = _bb_free_staff(s2, _bb_pdt(b["when"]), b.get("service")) or st[0]["id"]
            if "pend" in v:
                v["pend"] = pend
    except Exception as e:
        print("staff assign:", e)
    return _bb_save_v3(d)


_bb_notify_v3 = notify


def notify(subject, body, to=None):
    try:
        p = request.path.strip("/").split("/")
        if len(p) >= 2 and p[0] in ("book", "paid") and "booking" in (subject or "").lower():
            shop = load().get(p[1]) or {}
            b = (shop.get("bookings") or [None])[-1]
            if b and b.get("when") and b["when"] in (body or ""):
                extra = ""
                if b.get("staff") and _bb_staff_name(shop, b["staff"]):
                    extra += "\nWith: " + _bb_staff_name(shop, b["staff"])
                if b.get("note"):
                    extra += "\nNote from customer: " + b["note"]
                if extra and extra not in body:
                    body = body + "\n" + extra
    except Exception:
        pass
    return _bb_notify_v3(subject, body, to)


def _bb_staff_form(shop):
    names = "\n".join(s.get("name", "") for s in _bb_staff(shop))
    rd = str(int(shop.get("rebook_days") or 0))
    return ("<h3>Staff</h3><p style='font-size:13px;color:#556'>One name per line. Customers can pick who they want, or \"Anyone available\". "
            "Each person can take one appointment at a time. Leave empty if it's just you.</p>"
            "<textarea name='staff_names' rows='4' placeholder='Kawika&#10;Leilani&#10;Noa'>" + str(escape(names)) + "</textarea>"
            "<h3>Walk-ins</h3><label style='display:flex;gap:8px;align-items:center'><input type='checkbox' name='walkins' value='1' style='width:auto'" +
            (" checked" if shop.get("walkins") else "") + "> Let walk-ins join a line online (shows a \"Join the line\" button on your page)</label>"
            "<h3>Bring customers back</h3><p style='font-size:13px;color:#556'>Email customers a \"time to book again\" reminder this many days after their visit (0 = off). "
            "Skipped if they already have a booking.</p><input type='number' name='rebook_days' min='0' max='120' value='" + rd + "'>")


_bb_bphone_in_old6 = _bb_bphone_in


def _bb_bphone_in(shop):
    h = _bb_bphone_in_old6(shop)
    if isinstance(shop, dict) and "services" in shop and "id='bbhrs'" in h:
        i = h.rfind("</div><script>document.addEventListener")
        if i < 0:
            i = h.find("<h3 id='bbdurh'>")
        if i >= 0:
            h = h[:i] + _bb_staff_form(shop) + h[i:]
    return h


@app.before_request
def _bb_v3_edit():
    try:
        p = request.path.strip("/").split("/")
        if not (request.method == "POST" and len(p) == 2 and p[0] == "edit" and request.form.get("bb_hours") == "1"):
            return None
        sid = p[1]
        if not _bb_sess.get("own_" + sid):
            return None
        import re as _re, secrets as _sec
        d = load()
        shop = d.get(sid)
        if not shop:
            return None
        f = request.form
        old = {s.get("name", "").strip().lower(): s for s in (shop.get("staff") or []) if isinstance(s, dict)}
        new = []
        for n in (f.get("staff_names") or "").splitlines():
            n = n.strip()[:40]
            if not n or n.lower() in [x["name"].lower() for x in new]:
                continue
            if n.lower() in old:
                o = dict(old[n.lower()])
                o["name"] = n
                new.append(o)
            else:
                new.append({"id": (_re.sub(r"[^a-z0-9]+", "", n.lower())[:12] or "staff") + _sec.token_hex(2), "name": n})
        shop["staff"] = new[:20]
        shop["walkins"] = f.get("walkins") == "1"
        rd = (f.get("rebook_days") or "0").strip()
        shop["rebook_days"] = max(0, min(120, int(rd))) if rd.isdigit() else 0
        save(d)
    except Exception as e:
        print("v3 edit:", e)
    return None


def _bb_svc_script(shop):
    import json
    st = _bb_staff(shop)
    svcs = list((shop.get("services") or {}).keys())
    lens = {n: _bb_len_txt(_bb_dur(shop, n)) for n in svcs if _bb_dur(shop, n)}
    if not st and not lens:
        return ""
    base = [v for v, _ in _bb_slots_for(shop, None, "") if not _bb_blocked(shop, v)]
    pos = {v: i for i, v in enumerate(base)}
    data = {}
    for who in ([""] + [s["id"] for s in st] if st else [""]):
        for n in svcs:
            if not who and not _bb_dur(shop, n):
                continue
            data[who + "|" + n] = [pos[v] for v, _ in _bb_slots_for(shop, n, who) if v in pos and not _bb_blocked(shop, v)]
    js = json.dumps({"b": base, "d": data, "n": lens}).replace("</", "<\\/")
    return ("<script>(function(){var X=" + js + ",s=document.querySelector('select[name=service]'),w=document.querySelector('select[name=when]'),p=document.querySelector('select[name=staff]');if(!s||!w)return;"
            "[].forEach.call(s.options,function(o){if(X.n[o.value])o.text+=' ('+X.n[o.value]+')'});"
            "var lab={};[].forEach.call(w.options,function(o){lab[o.value]=o.text});"
            "function f(){var k=(p?p.value:'')+'|'+s.value,ok=X.d[k],cur=w.value;w.innerHTML='';"
            "X.b.forEach(function(v,i){if(lab[v]&&(!ok||ok.indexOf(i)>=0)){var o=document.createElement('option');o.value=v;o.text=lab[v];w.appendChild(o)}});"
            "if(!w.options.length){var o=document.createElement('option');o.value='';o.text='No open times for this choice. Try another, or the waitlist below.';w.appendChild(o)}"
            "if(cur)w.value=cur;if(!w.value&&w.options.length)w.selectedIndex=0}"
            "s.addEventListener('change',f);if(p)p.addEventListener('change',f);f()})();</script>")


def _bb_book_extras(sid, shop, h):
    st = _bb_staff(shop)
    if st and "name='staff'" not in h:
        sel = ("<p><b>Who would you like?</b></p><select name='staff'><option value=''>Anyone available</option>" +
               "".join("<option value='" + s["id"] + "'>" + str(escape(s.get("name", ""))) + "</option>" for s in st) + "</select>")
        i = h.find("<select name='service'")
        if i >= 0:
            h = h[:i] + sel + h[i:]
    if "name='note'" not in h:
        i = h.find("action='/book/")
        j = h.find("<div style='background:#fff6e5", i) if i >= 0 else -1
        if j < 0 and i >= 0:
            j = h.find("<button", i)
        if j >= 0:
            h = h[:j] + "<textarea name='note' rows='2' maxlength='300' placeholder='Anything the business should know? (optional)'></textarea>" + h[j:]
    if shop.get("walkins") and "id='bbline'" not in h:
        n = len(_bb_q_wait(shop))
        btn = ("<a id='bbline' href='/line/" + sid + "' style='display:block;text-align:center;padding:12px;margin:10px 0;border:2px solid #1faa59;color:#1faa59;"
               "border-radius:10px;text-decoration:none;font-weight:700'>&#128694; Walking in? Join the line (" + str(n) + " waiting)</a>")
        i = h.find("<div id='bbpage'>")
        i = h.find("</div>", i) + 6 if i >= 0 else h.find("</h1>") + 5
        h = h[:i] + btn + h[i:]
    return h


@app.after_request
def _bb_v3_page(resp):
    try:
        if request.method != "GET" or resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        p = request.path.strip("/").split("/")
        if len(p) == 2 and p[0] == "b":
            shop = load().get(p[1])
            if shop:
                resp.set_data(_bb_book_extras(p[1], shop, resp.get_data(as_text=True)))
        elif len(p) == 2 and p[0] == "d":
            h = resp.get_data(as_text=True)
            shop = load().get(p[1])
            if shop and "total bookings" in h and "id='bbclients'" not in h:
                add = _bb_owner_cards(p[1], shop)
                i = h.find("id='bbstats'")
                i = h.find("<div class='card' id='bbstats'") if i >= 0 else -1
                if i < 0:
                    i = h.find("total bookings</div>")
                    i = i + len("total bookings</div>") if i >= 0 else -1
                h = h[:i] + add + h[i:] if i >= 0 else h + add
                resp.set_data(h)
        elif len(p) == 3 and p[0] == "m":
            shop = load().get(p[1]) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == p[2]), None)
            h = resp.get_data(as_text=True)
            if b and "id='bbwith'" not in h:
                bits = ""
                if b.get("staff") and _bb_staff_name(shop, b["staff"]):
                    bits += "<b>With:</b> " + str(escape(_bb_staff_name(shop, b["staff"]))) + "<br>"
                if b.get("note"):
                    bits += "<b>Your note:</b> " + str(escape(b["note"]))
                if bits:
                    i = h.find("</h1>")
                    i = i + 5 if i >= 0 else 0
                    resp.set_data(h[:i] + "<p id='bbwith'>" + bits + "</p>" + h[i:])
    except Exception as ex:
        print("v3 page:", ex)
    return resp


def _bb_owner_cards(sid, shop):
    e = lambda s: str(escape(s))
    out = ("<a id='bbclients' class='card' href='/clients/" + sid + "' style='display:block;text-decoration:none;font-weight:700'>&#128101; Clients, notes &amp; repeat bookings &rarr;</a>")
    st = _bb_staff(shop)
    if st:
        now = _bb_local_now(shop)
        end = now + timedelta(days=7)
        rows = ""
        for s in st:
            bl = sorted([b for b in shop.get("bookings", []) if _bb_b_staff(shop, b, st) == s["id"] and not _bb_is_cxl(b)
                         and _bb_pdt(b.get("when")) and now - timedelta(hours=1) <= _bb_pdt(b["when"]) <= end], key=lambda b: b["when"])
            rows += "<p style='margin:10px 0 4px'><b>" + e(s.get("name", "")) + "</b> (" + str(len(bl)) + ")</p>"
            rows += "".join("<div style='font-size:14px;padding:4px 0;border-bottom:1px solid #eef'>" + e(_bb_fmt(b["when"])) + " &middot; " + e(b.get("name", "")) +
                            " &middot; " + e(b.get("service", "")) + ("<br><i>&#128221; " + e(b["note"]) + "</i>" if b.get("note") else "") + "</div>" for b in bl) or "<div style='font-size:13px;color:#889'>Nothing booked</div>"
        out += "<div class='card' id='bbstaffcard'><b>&#128197; Next 7 days by staff</b>" + rows + "</div>"
    if shop.get("walkins"):
        q = _bb_q_wait(shop)
        btn = "padding:6px 10px;margin:2px;border-radius:8px;border:1px solid #1a6dff;background:#fff;color:#1a6dff;font-weight:700"
        rows = "".join("<form method='post' action='/line/" + sid + "/act' style='display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:6px 0'>"
                       "<input type='hidden' name='q' value='" + x["id"] + "'><span style='flex:1'><b>" + str(i + 1) + ". " + e(x.get("name", "")) + "</b>" +
                       (" &#128227; called" if x.get("status") == "called" else "") + "</span>"
                       "<button name='a' value='call' style='" + btn + ";width:auto'>Call</button><button name='a' value='done' style='" + btn + ";width:auto'>Done</button>"
                       "<button name='a' value='rm' style='" + btn + ";width:auto;color:#e23b3b;border-color:#e23b3b'>Remove</button></form>" for i, x in enumerate(q))
        out += ("<div class='card' id='bblinecard'><b>&#128694; Walk-in line (" + str(len(q)) + ")</b>" + (rows or "<p style='font-size:13px;color:#889'>Nobody waiting.</p>") +
                "<a href='/line/" + sid + "' style='font-size:13px'>Open the line page</a></div>")
    return out


@app.route("/clients/<sid>", methods=["GET", "POST"])
def bb_clients(sid):
    import secrets as _sec
    d = load()
    shop = d.get(sid)
    if not shop:
        return S + "<h1>Not found</h1>", 404
    if not _bb_sess.get("own_" + sid):
        return redirect("/d/" + sid)
    e = lambda s: str(escape(s))
    msg = ""
    f = request.form
    if request.method == "POST" and f.get("a") == "note":
        cn = shop.get("cnotes") or {}
        k = (f.get("k") or "").strip().lower()[:200]
        if k:
            cn[k] = (f.get("note") or "").strip()[:500]
            shop["cnotes"] = cn
            save(d)
            msg = "Note saved."
    elif request.method == "POST" and f.get("a") == "repeat":
        msg = _bb_make_repeats(sid, shop, f)
        save(d)
    now = _bb_local_now(shop)
    cl = {}
    for b in shop.get("bookings", []):
        k = (b.get("email") or b.get("phone") or b.get("name") or "").strip().lower()
        if not k:
            continue
        c = cl.setdefault(k, {"name": b.get("name", ""), "email": b.get("email", ""), "phone": b.get("phone", ""), "n": 0, "spent": 0.0, "last": "", "next": "", "ns": 0, "cx": 0, "svc": {}})
        dt = _bb_pdt(b.get("when"))
        if _bb_is_cxl(b):
            c["cx"] += 1
            continue
        if b.get("noshow") or str(b.get("status", "")).lower() in ("noshow", "no-show", "no_show"):
            c["ns"] += 1
        if dt and dt < now:
            c["n"] += 1
            c["last"] = max(c["last"], b["when"])
        elif dt:
            c["next"] = min(c["next"] or b["when"], b["when"])
        try:
            c["spent"] += float(b.get("fee") or 0)
        except Exception:
            pass
        sv = b.get("service") or ""
        c["svc"][sv] = c["svc"].get(sv, 0) + 1
    st = _bb_staff(shop)
    so = "".join("<option>" + e(n) + "</option>" for n in (shop.get("services") or {}).keys())
    sto = ("<select name='staff'>" + "".join("<option value='" + s["id"] + "'>" + e(s.get("name", "")) + "</option>" for s in st) + "</select>") if st else ""
    cards = ""
    for k, c in sorted(cl.items(), key=lambda kv: kv[1]["last"] or kv[1]["next"], reverse=True):
        fav = max(c["svc"].items(), key=lambda x: x[1])[0] if c["svc"] else ""
        note = (shop.get("cnotes") or {}).get(k, "")
        cards += ("<div class='card'><b style='font-size:18px'>" + e(c["name"]) + "</b><br>" +
                  (e(c["email"]) + "<br>" if c["email"] else "") + (e(c["phone"]) + "<br>" if c["phone"] else "") +
                  "<span style='font-size:14px'>Visits: <b>" + str(c["n"]) + "</b> &middot; Spent: <b>$%.0f</b>" % c["spent"] +
                  (" &middot; No-shows: <b style='color:#e23b3b'>" + str(c["ns"]) + "</b>" if c["ns"] else "") +
                  (" &middot; Cancels: " + str(c["cx"]) if c["cx"] else "") + "<br>" +
                  ("Last visit: " + e(_bb_fmt(c["last"])) + "<br>" if c["last"] else "") +
                  ("Next: <b>" + e(_bb_fmt(c["next"])) + "</b><br>" if c["next"] else "") +
                  ("Usually: " + e(fav) + "<br>" if fav else "") + "</span>"
                  "<form method='post' style='margin-top:8px'><input type='hidden' name='a' value='note'><input type='hidden' name='k' value='" + e(k) + "'>"
                  "<textarea name='note' rows='2' placeholder='Private note (only you see this)'>" + e(note) + "</textarea><button style='width:auto'>Save note</button></form>" +
                  ("<details style='margin-top:6px'><summary style='font-weight:700;color:#1a6dff'>&#128257; Set up repeat bookings</summary>"
                   "<form method='post'><input type='hidden' name='a' value='repeat'><input type='hidden' name='k' value='" + e(k) + "'>"
                   "<p>First appointment</p><input type='datetime-local' name='start' required><p>Service</p><select name='service'>" + so + "</select>" + sto +
                   "<p>Repeat every</p><select name='every'><option value='1'>1 week</option><option value='2' selected>2 weeks</option><option value='3'>3 weeks</option><option value='4'>4 weeks</option><option value='6'>6 weeks</option></select>"
                   "<p>How many appointments</p><select name='count'>" + "".join("<option" + (" selected" if i == 6 else "") + ">" + str(i) + "</option>" for i in range(2, 13)) + "</select>"
                   "<button>Book them</button></form></details>" if c["email"] else "") + "</div>")
    return (S + "<p><a href='/d/" + sid + "'>&larr; Back to dashboard</a></p><h1>&#128101; Clients</h1><p>" + str(len(cl)) + " customers</p>" +
            ("<div class='card' style='background:#e6f7ee'>" + e(msg) + "</div>" if msg else "") + (cards or "<p>No customers yet.</p>"))


def _bb_make_repeats(sid, shop, f):
    import secrets as _sec
    k = (f.get("k") or "").strip().lower()
    src = next((b for b in reversed(shop.get("bookings", [])) if (b.get("email") or b.get("phone") or b.get("name") or "").strip().lower() == k), None)
    st0 = _bb_pdt(f.get("start", ""))
    if not src or not st0:
        return "Pick a start date and time."
    try:
        every, count = int(f.get("every") or 2), min(12, max(2, int(f.get("count") or 6)))
    except Exception:
        return "Pick how often and how many."
    svc = f.get("service") or src.get("service", "")
    who = f.get("staff", "")
    made, skipped = [], []
    for i in range(count):
        dt = st0 + timedelta(weeks=every * i)
        w = dt.strftime(_BB_F)
        ok = True
        try:
            ok = not _bb_blocked(shop, w)
        except Exception:
            pass
        pick = None
        if ok:
            if _bb_staff(shop):
                pick = _bb_free_staff(shop, dt, svc, who)
                ok = bool(pick)
            else:
                ok = _bb_range_ok(shop, dt, _bb_len(shop, svc), None, bool(_bb_dur(shop, svc)))
        if not ok:
            skipped.append(w)
            continue
        b = {"name": src.get("name", ""), "phone": src.get("phone", ""), "email": src.get("email", ""), "service": svc, "when": w,
             "fee": 0, "rt": _sec.token_urlsafe(8), "repeat": True, "paid": False}
        if pick:
            b["staff"] = pick
        shop["bookings"].append(b)
        made.append(b)
    if made and src.get("email"):
        try:
            host = request.host_url
            notify("Your repeat appointments at " + shop.get("name", ""),
                   "Hi " + src.get("name", "") + ",\n\n" + shop.get("name", "") + " booked these for you:\n\n" +
                   "\n".join("- " + _bb_fmt(b["when"]) + " (" + svc + ")  manage: " + host + "m/" + sid + "/" + b["rt"] for b in made) +
                   "\n\nPayment is at the shop. Use the links to cancel or reschedule any of them.", src["email"])
        except Exception as ex:
            print("repeat mail:", ex)
    return ("Booked " + str(len(made)) + " appointments." + (" Skipped (already taken): " + ", ".join(_bb_fmt(x) for x in skipped) if skipped else ""))


def _bb_q_wait(shop):
    today = _bb_local_now(shop).strftime("%Y-%m-%d")
    return [x for x in shop.get("queue", []) if x.get("status") in ("wait", "called") and x.get("day") == today]


@app.route("/line/<sid>", methods=["GET", "POST"])
def bb_line(sid):
    import secrets as _sec
    d = load()
    shop = d.get(sid)
    if not shop or not shop.get("walkins"):
        return S + "<h1>This business isn't taking walk-ins online right now</h1><a href='/b/" + sid + "'>Book an appointment instead</a>", 404
    e = lambda s: str(escape(s))
    q = _bb_q_wait(shop)
    if request.method == "POST":
        nm = (request.form.get("name") or "").strip()[:60]
        if not nm:
            return redirect("/line/" + sid)
        if len(q) >= 50:
            return S + "<h1>The line is full right now</h1><p>Please try again a bit later.</p>"
        x = {"id": _sec.token_urlsafe(6), "name": nm, "phone": (request.form.get("phone") or "").strip()[:30],
             "email": (request.form.get("email") or "").strip()[:200], "status": "wait",
             "day": _bb_local_now(shop).strftime("%Y-%m-%d"), "ts": _bb_local_now(shop).strftime(_BB_F)}
        today = x["day"]
        shop["queue"] = [y for y in shop.get("queue", []) if y.get("day") == today] + [x]
        save(d)
        try:
            notify("Walk-in joined the line at " + shop.get("name", ""), nm + " joined the line. " + str(len(q) + 1) + " waiting now.", shop.get("email") or None)
        except Exception:
            pass
        return redirect("/line/" + sid + "/" + x["id"])
    avg = _bb_avg_len(shop)
    return (S + "<h1>&#128694; " + e(shop.get("name", "")) + "</h1><p style='font-size:20px'><b>" + str(len(q)) + "</b> waiting &middot; about <b>" + str(len(q) * avg) + " min</b></p>"
            "<form method='post'><input name='name' placeholder='Your name' required><input name='phone' placeholder='Phone (optional)'>"
            "<input name='email' type='email' placeholder='Email (optional, we tell you when it is your turn)'><button>Join the line</button></form>"
            "<p><a href='/b/" + sid + "'>Or book an appointment</a></p>")


def _bb_avg_len(shop):
    ls = [_bb_len(shop, n) for n in (shop.get("services") or {}).keys()] or [_bb_step(shop)]
    per = max(1, len(_bb_staff(shop)))
    return max(5, int(sum(ls) / len(ls) / per))


@app.route("/line/<sid>/<qid>")
def bb_line_me(sid, qid):
    shop = load().get(sid) or {}
    e = lambda s: str(escape(s))
    q = _bb_q_wait(shop)
    me = next((x for x in shop.get("queue", []) if x.get("id") == qid), None)
    if not me:
        return S + "<h1>We couldn't find your spot</h1><a href='/line/" + sid + "'>Join the line</a>", 404
    ref = "<meta http-equiv='refresh' content='30'>"
    if me.get("status") == "called":
        return S + ref + "<h1>&#128227; It's your turn!</h1><p>Please head in to " + e(shop.get("name", "")) + " now.</p>"
    if me.get("status") != "wait":
        return S + "<h1>Thanks for coming in!</h1><p>You're no longer in the line.</p><a href='/b/" + sid + "'>Book your next visit</a>"
    pos = [x["id"] for x in q].index(qid) + 1 if qid in [x["id"] for x in q] else 1
    return (S + ref + "<h1>You're #" + str(pos) + " in line</h1><p>at <b>" + e(shop.get("name", "")) + "</b></p><p>About <b>" + str((pos - 1) * _bb_avg_len(shop)) +
            " min</b> wait. This page updates by itself" + (", and we'll email you when it's your turn" if me.get("email") else "") + ".</p>"
            "<p style='font-size:13px;color:#667'>Keep this page open or bookmark it.</p>")


@app.route("/line/<sid>/act", methods=["POST"])
def bb_line_act(sid):
    d = load()
    shop = d.get(sid)
    if not shop or not _bb_sess.get("own_" + sid):
        return redirect("/d/" + sid)
    qid, a = request.form.get("q", ""), request.form.get("a", "")
    x = next((y for y in shop.get("queue", []) if y.get("id") == qid), None)
    if x:
        if a == "call":
            x["status"] = "called"
            if x.get("email"):
                try:
                    notify("It's your turn at " + shop.get("name", ""), "Hi " + x.get("name", "") + ", it's your turn! Please head in to " + shop.get("name", "") + " now.", x["email"])
                except Exception:
                    pass
        elif a in ("done", "rm"):
            x["status"] = a
        save(d)
    return redirect("/d/" + sid)


_bb_run_reminders_v3 = _bb_run_reminders


def _bb_run_reminders(host):
    n = _bb_run_reminders_v3(host)
    try:
        d = load()
        due = []
        for sid, shop in d.items():
            if not isinstance(shop, dict):
                continue
            rd = int(shop.get("rebook_days") or 0)
            if rd <= 0:
                continue
            now = _bb_local_now(shop)
            fut = {(b.get("email") or "").lower() for b in shop.get("bookings", []) if (_bb_pdt(b.get("when")) or now) > now and not _bb_is_cxl(b)}
            for b in shop.get("bookings", []):
                dt = _bb_pdt(b.get("when"))
                em = (b.get("email") or "").lower()
                if not dt or not em or b.get("rebook_sent") or _bb_is_cxl(b) or em in fut or b.get("noshow"):
                    continue
                if timedelta(days=rd) <= now - dt <= timedelta(days=rd + 3):
                    b["rebook_sent"] = True
                    fut.add(em)
                    due.append((sid, shop, dict(b)))
        if due:
            save(d)
            for sid, shop, b in due:
                try:
                    notify("Time for your next " + (b.get("service") or "visit") + " at " + shop.get("name", "") + "?",
                           "Hi " + b.get("name", "") + ",\n\nIt's been a little while since your last " + (b.get("service") or "visit") + " at " + shop.get("name", "") +
                           ". Ready for the next one?\n\nBook in one tap: " + host + "b/" + sid + "\n\nMahalo!", b["email"])
                except Exception as ex:
                    print("rebook mail:", ex)
        n += len(due)
    except Exception as ex:
        print("rebook:", ex)
    return n
# ===== END BB UPGRADE 2 =====


# ===== BB UPGRADE 3: directions =====
def _bb_dir_url(shop):
    from urllib.parse import quote as _q
    a = (shop or {}).get("addr", "").strip()
    if a:
        return "https://www.google.com/maps/dir/?api=1&destination=" + _q(a)
    if shop and shop.get("lat") and shop.get("lng"):
        return "https://www.google.com/maps/dir/?api=1&destination=" + _q(str(shop["lat"]) + "," + str(shop["lng"]))
    return ""


def _bb_dir_btn(shop):
    u = _bb_dir_url(shop)
    if not u:
        return ""
    return ("<a id='bbdir' href='" + str(escape(u)) + "' target='_blank' rel='noopener' style='display:block;text-align:center;padding:14px;margin:12px 0;"
            "background:#1a6dff;color:#fff;border-radius:12px;text-decoration:none;font-weight:800;font-size:17px'>&#128205; Get directions</a>"
            + ("<p style='text-align:center;font-size:13px;color:#556;margin:-6px 0 10px'>" + str(escape(shop.get("addr", ""))) + "</p>" if shop.get("addr") else ""))


@app.after_request
def _bb_dir_page(resp):
    try:
        if resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        h = resp.get_data(as_text=True)
        if "id='bbdir'" in h:
            return resp
        p = request.path.strip("/").split("/")
        sid = None
        if len(p) == 3 and p[0] == "m":
            sid = p[1]
        elif len(p) == 2 and p[0] in ("book", "paid") and ("booked" in h.lower() or "you're all set" in h.lower()):
            sid = p[1]
        elif len(p) == 3 and p[0] == "line" and "your turn" in h.lower():
            sid = p[1]
        if not sid:
            return resp
        btn = _bb_dir_btn(load().get(sid) or {})
        if not btn:
            return resp
        i = h.find("</p>", h.find("id='bbwith'")) + 4 if "id='bbwith'" in h else -1
        if i < 4:
            i = h.find("</h1>")
            i = i + 5 if i >= 0 else 0
        resp.set_data(h[:i] + btn + h[i:])
    except Exception as ex:
        print("dir page:", ex)
    return resp


_bb_notify_dir = notify


def notify(subject, body, to=None):
    try:
        import re as _re
        m_ = _re.search(r"/m/([A-Za-z0-9_-]+)/", body or "")
        if m_ and "google.com/maps/dir" not in body:
            shop = load().get(m_.group(1)) or {}
            u = _bb_dir_url(shop)
            if u and (to or "").lower() != (shop.get("email") or "").lower():
                if "in about 2 hours" in body:
                    body = body + "\n\nLeaving soon? Get directions: " + u
                else:
                    body = body + "\n\nGet directions: " + u
    except Exception as ex:
        print("dir mail:", ex)
    return _bb_notify_dir(subject, body, to)
# ===== END BB UPGRADE 3 =====


# ===== BB UPGRADE 4: I come to you (mobile businesses) =====
_BB_GEO = {}
_BB_TRL = {}


def _bb_where(shop):
    w = (shop or {}).get("where") or "shop"
    return w if w in ("shop", "mobile", "both", "online") else "shop"


def _bb_geocode(addr):
    a = " ".join(str(addr or "").split()).strip()[:200]
    if len(a) < 5:
        return None
    k = a.lower()
    if k in _BB_GEO:
        return _BB_GEO[k]
    q = a
    toks = k.replace(",", " ").split()
    if "hi" not in toks[-3:] and "hawaii" not in k:
        q = a + ", HI"
    res = None
    try:
        import urllib.request, urllib.parse, json
        u = ("https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?benchmark=Public_AR_Current&format=json&address=" + urllib.parse.quote(q))
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "business-bookie/1.0"}), timeout=8)
        mt = json.loads(r.read().decode()).get("result", {}).get("addressMatches", [])
        if mt:
            c = mt[0]["coordinates"]
            res = (float(c["y"]), float(c["x"]))
    except Exception as ex:
        print("geocode:", ex)
        return None
    if len(_BB_GEO) > 2000:
        _BB_GEO.clear()
    _BB_GEO[k] = res
    return res


def _bb_miles(p, q):
    import math
    if not p or not q:
        return None
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def _bb_drive_min(p, q, when=None):
    d = _bb_miles(p, q)
    if d is None:
        return None
    if d < 0.05:
        return 0
    rush = bool(when) and when.weekday() < 5 and (6 <= when.hour < 9 or 15 <= when.hour + when.minute / 60.0 < 18.5)
    road = d * 1.3
    mph = 25.0 + min(20.0, road)
    if rush:
        mph *= 0.65
    mins = road / mph * 60 + 4
    return int(-(-mins // 5) * 5)


def _bb_shop_loc(shop):
    try:
        if shop.get("lat") and shop.get("lng"):
            return (float(shop["lat"]), float(shop["lng"]))
    except Exception:
        pass
    if shop.get("addr"):
        return _bb_geocode(shop["addr"])
    if shop.get("base_ll"):
        return tuple(shop["base_ll"])
    return None


def _bb_base_loc(shop):
    if shop.get("base_ll"):
        return tuple(shop["base_ll"])
    if shop.get("base"):
        return _bb_geocode(shop["base"])
    return _bb_shop_loc(shop)


def _bb_b_loc(shop, b):
    if b.get("at") == "home":
        if b.get("lat") is not None and b.get("lng") is not None:
            return (float(b["lat"]), float(b["lng"]))
        return None
    return _bb_shop_loc(shop)


def _bb_travel_ok(shop, st_dt, ln, at, loc, staff_id="", skip_rt=None):
    pad = max(0, min(120, int(shop.get("tpad") or 10)))
    en = st_dt + timedelta(minutes=ln)
    st = _bb_staff(shop) if "_bb_staff" in globals() else []
    prev = nxt = None
    for b in shop.get("bookings", []):
        if _bb_is_cxl(b) or (skip_rt and b.get("rt") == skip_rt):
            continue
        if st and staff_id and _bb_b_staff(shop, b, st) != staff_id:
            continue
        bs = _bb_pdt(b.get("when"))
        if not bs or bs.date() != st_dt.date():
            continue
        be = bs + timedelta(minutes=_bb_len(shop, b.get("service")))
        if be <= st_dt and (prev is None or be > prev[1]):
            prev = (b, be)
        if bs >= en and (nxt is None or bs < nxt[1]):
            nxt = (b, bs)
    for side in (prev, nxt):
        if not side:
            continue
        b, t = side
        b_at = b.get("at") or "shop"
        if b_at == "shop" and at == "shop":
            continue
        bl = _bb_b_loc(shop, b)
        if bl and loc:
            need = (_bb_drive_min(bl, loc, st_dt) or 0) + pad
        else:
            need = pad + 15
        gap = (st_dt - t).total_seconds() / 60 if side is prev else (t - en).total_seconds() / 60
        if gap < need:
            return False
    return True


def _bb_ok_slots(shop, svc, staff, at, loc):
    out = []
    for v, lab in _bb_slots_for(shop, svc, staff):
        try:
            if _bb_blocked(shop, v):
                continue
        except Exception:
            pass
        dt = _bb_pdt(v)
        who = staff
        if _bb_staff(shop) and not staff:
            who = next((s["id"] for s in _bb_staff(shop) if _bb_as_staff(s["id"], lambda: _bb_range_ok(shop, dt, _bb_len(shop, svc), None, bool(_bb_dur(shop, svc))))
                        and _bb_travel_ok(shop, dt, _bb_len(shop, svc), at, loc, s["id"])), None)
            if who:
                out.append((v, lab))
            continue
        if _bb_travel_ok(shop, dt, _bb_len(shop, svc), at, loc, who or ""):
            out.append((v, lab))
    return out


def _bb_hidden(skip=("when",)):
    return "".join("<input type='hidden' name='" + str(escape(k)) + "' value='" + str(escape(v)) + "'>"
                   for k, vs in request.form.lists() for v in vs if k not in skip)


@app.before_request
def _bb_v4_before():
    try:
        from flask import g
        p = request.path.strip("/").split("/")
        if len(p) == 3 and p[0] == "m" and request.method == "GET":
            shop = load().get(p[1]) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == p[2]), None)
            if b and b.get("at") == "home":
                g.bb_nodir = True
            return None
        if not (request.method == "POST" and len(p) == 2 and p[0] == "book"):
            return None
        d = load()
        shop = d.get(p[1])
        if not shop or _bb_where(shop) in ("shop", "online"):
            return None
        f = request.form
        wh = _bb_where(shop)
        at = "home" if wh == "mobile" else ("home" if f.get("at") == "home" else "shop")
        svc = f.get("service")
        st_dt = _bb_pdt(f.get("when", ""))
        back = "<a href='/b/" + p[1] + "'>Back</a>"
        x = {"at": at}
        loc = None
        if at == "home":
            g.bb_nodir = True
            ca = " ".join((f.get("caddr") or "").split())[:200]
            if len(ca) < 5:
                return S + "<h1>Please enter your address</h1><p>Tell us where to come for your appointment.</p>" + back
            loc = _bb_geocode(ca)
            x.update({"caddr": ca, "geo_ok": bool(loc)})
            if loc:
                x["lat"], x["lng"] = round(loc[0], 6), round(loc[1], 6)
                base = _bb_base_loc(shop)
                rad = float(shop.get("radius") or 0)
                if base and rad > 0 and _bb_miles(base, loc) > rad:
                    return (S + "<h1>Sorry, that's outside our service area</h1><p>" + str(escape(shop.get("name", ""))) + " serves " +
                            str(escape(shop.get("area") or ("within " + str(int(rad)) + " miles"))) + ".</p>" + back)
        else:
            loc = _bb_shop_loc(shop)
        if st_dt:
            who = g.get("bb_staff") or ""
            if not _bb_travel_ok(shop, st_dt, _bb_len(shop, svc), at, loc, who):
                alts = _bb_ok_slots(shop, svc, who, at, loc)[:60]
                opts = "".join("<option value='" + str(escape(v)) + "'>" + str(escape(lab)) + "</option>" for v, lab in alts)
                return (S + "<h1>Not enough drive time</h1><p>That time is too close to another appointment across town. "
                        "You have <b>not</b> been charged.</p>" + ("<p>These times work for your address:</p><form method='post' action='/book/" + p[1] + "'>" +
                        _bb_hidden() + "<select name='when' required>" + opts + "</select><button>Book this time</button></form>" if alts else "<p>No other open times fit right now.</p>") + back)
        key = _bb_pkey(f.get("when"), f.get("email"))
        pend = shop.get("pend") or {}
        pe = pend.get(key) or {"staff": "", "note": ""}
        pe["x"] = x
        pend[key] = pe
        shop["pend"] = pend
        save(d)
    except Exception as e:
        print("v4 before:", e)
    return None


_bb_save_v4 = save


def save(d):
    try:
        for v in d.values():
            if not isinstance(v, dict) or not v.get("pend"):
                continue
            for b in v.get("bookings", []):
                pe = v["pend"].get(_bb_pkey(b.get("when"), b.get("email")))
                if pe and pe.get("x") and not b.get("at"):
                    b.update(pe.pop("x"))
            for k in [k for k, pe in v["pend"].items() if not pe.get("staff") and not pe.get("note") and not pe.get("x")]:
                v["pend"].pop(k, None)
    except Exception as e:
        print("v4 save:", e)
    return _bb_save_v4(d)


def _bb_cust_dir(b):
    from urllib.parse import quote as _q
    if b.get("lat") is not None and b.get("lng") is not None:
        return "https://www.google.com/maps/dir/?api=1&destination=" + _q(str(b["lat"]) + "," + str(b["lng"]))
    if b.get("caddr"):
        return "https://www.google.com/maps/dir/?api=1&destination=" + _q(b["caddr"])
    return ""


_bb_dir_url_v1 = _bb_dir_url


def _bb_dir_url(shop):
    if _bb_where(shop) in ("mobile", "online") or _BB_CTX.get("nodir") or _bb_gv("bb_nodir"):
        return ""
    return _bb_dir_url_v1(shop)


_bb_notify_v4 = notify


def notify(subject, body, to=None):
    try:
        import re as _re
        m_ = _re.search(r"/m/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", body or "")
        if m_:
            shop = load().get(m_.group(1)) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == m_.group(2)), None)
            if b and b.get("at") == "home":
                if "Your address:" not in body and b.get("caddr"):
                    body += "\n\nWe'll come to: " + b["caddr"]
                _BB_CTX["nodir"] = True
        p = request.path.strip("/").split("/")
        if len(p) >= 2 and p[0] in ("book", "paid") and "booking" in (subject or "").lower():
            shop = load().get(p[1]) or {}
            b = (shop.get("bookings") or [None])[-1]
            if b and b.get("at") == "home" and b.get("caddr") and (to or "").lower() != (b.get("email") or "").lower() and "Customer address:" not in body:
                body += "\n\nHOUSE CALL\nCustomer address: " + b["caddr"] + ("\nDirections to customer: " + _bb_cust_dir(b) if _bb_cust_dir(b) else "") + \
                        ("" if b.get("geo_ok") else "\n(We couldn't find this address on the map - double-check it with the customer.)")
    except Exception:
        pass
    try:
        return _bb_notify_v4(subject, body, to)
    finally:
        _BB_CTX["nodir"] = False


def _bb_where_form(shop):
    e = lambda s: str(escape(s))
    wh = _bb_where(shop)
    op = "".join("<option value='" + k + "'" + (" selected" if wh == k else "") + ">" + lab + "</option>" for k, lab in
                 (("shop", "Customers come to me (my address)"), ("mobile", "I go to the customer (house calls)"), ("both", "Both - customer picks"), ("online", "Online / video call (no address needed)")))
    warn = ("<p style='color:#b37400;font-size:13px'>&#9888; We couldn't find your home base on the map. Check the address.</p>"
            if shop.get("base") and not shop.get("base_ll") else "")
    return ("<h3>Where do appointments happen?</h3><select name='where'>" + op + "</select>"
            "<p style='font-size:13px;color:#556'>If customers come to you, your business address is required. For house calls you can leave it blank "
            "so your home stays private.</p>"
            "<p>Area you serve (shown to customers)</p><input name='area' maxlength='120' placeholder='Honolulu, Kailua, Kaneohe' value='" + e(shop.get("area", "")) + "'>"
            "<p>Home base address (private, used for drive times)</p><input name='base' maxlength='200' placeholder='Where you start your day' value='" + e(shop.get("base", "")) + "'>" + warn +
            "<p>Farthest you'll drive (miles, 0 = no limit)</p><input type='number' name='radius' min='0' max='200' value='" + e(str(int(float(shop.get("radius") or 0)))) + "'>"
            "<p>Extra minutes between house calls (parking, setup)</p><input type='number' name='tpad' min='0' max='120' value='" + e(str(int(shop.get("tpad") or 10))) + "'>")


_bb_bphone_in_old7 = _bb_bphone_in


def _bb_bphone_in(shop):
    h = _bb_bphone_in_old7(shop)
    if isinstance(shop, dict) and "services" in shop and "<h3>Staff</h3>" in h and "name='where'" not in h:
        i = h.find("<h3>Staff</h3>")
        h = h[:i] + _bb_where_form(shop) + h[i:]
    return h


def _bb_v4_edit_check():
    try:
        p = request.path.strip("/").split("/")
        if request.method == "POST" and len(p) == 2 and p[0] == "edit" and request.form.get("bb_hours") == "1" and "where" in request.form:
            if not _bb_sess.get("own_" + p[1]):
                return None
            f = request.form
            wh = f.get("where") if f.get("where") in ("shop", "mobile", "both", "online") else "shop"
            if wh not in ("mobile", "online") and not (f.get("addr") or "").strip():
                return (S + "<h1>Business address needed</h1><p>Customers come to you, so they need your address to find you. "
                        "Add it, or choose \"I go to the customer\" if you only do house calls.</p><a href='javascript:history.back()'>Go back</a>")
            d = load()
            shop = d.get(p[1])
            if not shop:
                return None
            shop["where"] = wh
            shop["area"] = (f.get("area") or "").strip()[:120]
            base = " ".join((f.get("base") or "").split())[:200]
            if base != shop.get("base") or not shop.get("base_ll"):
                ll = _bb_geocode(base) if base else None
                if ll:
                    shop["base_ll"] = [round(ll[0], 6), round(ll[1], 6)]
                else:
                    shop.pop("base_ll", None)
            shop["base"] = base
            for k, mx in (("radius", 200), ("tpad", 120)):
                v = (f.get(k) or "0").strip()
                shop[k] = max(0, min(mx, int(v))) if v.isdigit() else (10 if k == "tpad" else 0)
            save(d)
    except Exception as e:
        print("v4 edit:", e)
    return None


app.before_request_funcs.setdefault(None, []).insert(0, _bb_v4_edit_check)


def _bb_v4_create_check():
    try:
        if request.method == "POST" and request.path.rstrip("/") == "/create" and "where" in request.form:
            if request.form.get("where") not in ("mobile", "online") and not (request.form.get("addr") or "").strip():
                return (S + "<h1>Business address needed</h1><p>Customers will come to you, so add your business address. "
                        "If you only do house calls, choose \"I go to the customer\".</p><a href='javascript:history.back()'>Go back</a>")
    except Exception as e:
        print("v4 create:", e)
    return None


app.before_request_funcs.setdefault(None, []).insert(0, _bb_v4_create_check)


@app.after_request
def _bb_v4_after(resp):
    try:
        p = request.path.strip("/").split("/")
        if request.method == "POST" and request.path.rstrip("/") == "/create" and resp.status_code in (301, 302, 303) and request.form.get("where"):
            loc = resp.headers.get("Location", "")
            sid = loc.rstrip("/").split("/")[-1].split("?")[0]
            d = load()
            if sid in d and request.form.get("where") in ("shop", "mobile", "both", "online"):
                d[sid]["where"] = request.form.get("where")
                save(d)
            return resp
        if resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        if request.method == "POST" and request.path.rstrip("/") == "/setup":
            h = resp.get_data(as_text=True)
            i = h.find("<input name='addr'")
            if i >= 0 and "name='where'" not in h:
                sel = ("<p><b>Where do appointments happen?</b></p><select name='where' id='bbwhere' onchange=\"var a=document.querySelector('input[name=addr]');"
                       "if(a){a.required=this.value!=='mobile'&&this.value!=='online';a.placeholder=(this.value==='mobile'||this.value==='online')?'Business address (optional for house calls)':'Business address (required)'}\">"
                       "<option value='shop'>Customers come to me</option><option value='mobile'>I go to the customer (house calls)</option><option value='both'>Both</option><option value='online'>Online / video call</option></select>")
                h = h[:i] + sel + h[i:].replace("<input name='addr' placeholder='Business address'", "<input name='addr' required placeholder='Business address (required)'", 1)
                resp.set_data(h)
            return resp
        if request.method != "GET":
            return resp
        if len(p) == 2 and p[0] == "b":
            shop = load().get(p[1])
            if not shop or _bb_where(shop) in ("shop", "online"):
                return resp
            h = resp.get_data(as_text=True)
            if "name='caddr'" in h:
                return resp
            wh = _bb_where(shop)
            inp = "<input name='caddr' id='bbcaddr' autocomplete='street-address' placeholder='Your address (street, city)'" + (" required" if wh == "mobile" else "") + ">"
            if wh == "mobile":
                blk = "<p><b>&#128663; Where should we come?</b></p>" + inp
            else:
                blk = ("<p><b>Where would you like your appointment?</b></p><label style='display:flex;gap:8px;align-items:center'><input type='radio' name='at' value='shop' checked style='width:auto'> At the shop</label>"
                       "<label style='display:flex;gap:8px;align-items:center'><input type='radio' name='at' value='home' style='width:auto'> Come to me</label><div id='bbcaddrbox' style='display:none'>" + inp + "</div>")
            blk += "<div id='bbtravelmsg' style='font-size:13px;color:#556;margin:4px 0'></div>"
            i = h.find("<select name='service'")
            if i < 0:
                return resp
            h = h[:i] + blk + h[i:]
            js = ("<script>(function(){var a=document.getElementById('bbcaddr'),w=document.querySelector('select[name=when]'),s=document.querySelector('select[name=service]'),m=document.getElementById('bbtravelmsg');"
                  "if(!a||!w||!s)return;var box=document.getElementById('bbcaddrbox');function home(){var r=document.querySelector('input[name=at]:checked');return !r||r.value==='home'}"
                  "[].forEach.call(document.querySelectorAll('input[name=at]'),function(r){r.addEventListener('change',function(){if(box)box.style.display=home()?'block':'none';a.required=home();if(home())go();})});"
                  "var t=null;function go(){if(!home()||a.value.trim().length<6)return;var p=document.querySelector('select[name=staff]');m.textContent='Checking drive time to your address...';"
                  "fetch('/travel/" + p[1] + "?a='+encodeURIComponent(a.value)+'&svc='+encodeURIComponent(s.value)+'&staff='+encodeURIComponent(p?p.value:'')).then(function(r){return r.json()}).then(function(j){"
                  "if(j.out){m.textContent=j.msg;w.innerHTML='';return}var cur=w.value;w.innerHTML='';j.ok.forEach(function(x){var o=document.createElement('option');o.value=x[0];o.text=x[1];w.appendChild(o)});"
                  "if(!j.ok.length){var o=document.createElement('option');o.value='';o.text='No open times fit your address. Try the waitlist below.';w.appendChild(o)}"
                  "if(cur)w.value=cur;if(!w.value&&w.options.length)w.selectedIndex=0;m.textContent=j.msg||''}).catch(function(){m.textContent=''})}"
                  "a.addEventListener('change',go);a.addEventListener('input',function(){clearTimeout(t);t=setTimeout(go,900)});"
                  "s.addEventListener('change',function(){setTimeout(go,50)});var p0=document.querySelector('select[name=staff]');if(p0)p0.addEventListener('change',function(){setTimeout(go,50)})})();</script>")
            resp.set_data(h + js)
        elif len(p) == 3 and p[0] == "m":
            shop = load().get(p[1]) or {}
            b = next((x for x in shop.get("bookings", []) if x.get("rt") == p[2]), None)
            h = resp.get_data(as_text=True)
            if b and b.get("at") == "home" and b.get("caddr") and "id='bbhome'" not in h:
                i = h.find("</h1>")
                i = i + 5 if i >= 0 else 0
                resp.set_data(h[:i] + "<p id='bbhome'>&#128663; <b>House call.</b> We'll come to: " + str(escape(b["caddr"])) + "</p>" + h[i:])
        elif len(p) == 2 and p[0] == "d":
            shop = load().get(p[1]) or {}
            h = resp.get_data(as_text=True)
            if _bb_where(shop) not in ("shop", "online") and "total bookings" in h and "id='bbroute'" not in h:
                card = _bb_route_card(shop)
                i = h.find("total bookings</div>")
                i = i + len("total bookings</div>") if i >= 0 else -1
                h = h[:i] + card + h[i:] if i >= 0 else h + card
                resp.set_data(h)
    except Exception as ex:
        print("v4 after:", ex)
    return resp


def _bb_route_card(shop):
    from urllib.parse import quote as _q
    e = lambda s: str(escape(s))
    now = _bb_local_now(shop)
    days = {}
    for b in shop.get("bookings", []):
        dt = _bb_pdt(b.get("when"))
        if not dt or _bb_is_cxl(b) or dt < now - timedelta(hours=2) or dt > now + timedelta(days=3):
            continue
        days.setdefault(dt.date(), []).append((dt, b))
    out = "<div class='card' id='bbroute'><b>&#128663; House calls (next 3 days)</b>"
    if not days:
        return out + "<p style='font-size:13px;color:#889'>No house calls coming up.</p></div>"
    for day in sorted(days):
        jobs = sorted(days[day], key=lambda x: x[0])
        out += "<p style='margin:10px 0 4px'><b>" + day.strftime("%a %b %d") + "</b></p>"
        prev = _bb_base_loc(shop)
        stops = []
        for dt, b in jobs:
            loc = _bb_b_loc(shop, b)
            dm = _bb_drive_min(prev, loc, dt) if prev and loc else None
            where_txt = b.get("caddr") if b.get("at") == "home" else "At the shop"
            link = _bb_cust_dir(b) if b.get("at") == "home" else ""
            out += ("<div style='font-size:14px;padding:5px 0;border-bottom:1px solid #eef'>" + ("<span style='color:#889'>&#8595; about " + str(dm) + " min drive</span><br>" if dm else "") +
                    "<b>" + dt.strftime("%I:%M %p").lstrip("0") + "</b> &middot; " + e(b.get("name", "")) + " &middot; " + e(b.get("service", "")) + "<br>" + e(where_txt or "") +
                    (" <a href='" + e(link) + "' target='_blank' rel='noopener'>Directions</a>" if link else "") + "</div>")
            if loc:
                prev = loc
            if b.get("at") == "home" and (b.get("caddr") or b.get("lat")):
                stops.append(str(b["lat"]) + "," + str(b["lng"]) if b.get("lat") is not None else b["caddr"])
        if stops:
            u = "https://www.google.com/maps/dir/?api=1&destination=" + _q(stops[-1]) + ("&waypoints=" + _q("|".join(stops[:-1][:9])) if len(stops) > 1 else "")
            out += "<a href='" + e(u) + "' target='_blank' rel='noopener' style='display:inline-block;margin-top:6px;font-weight:700'>&#128506; Open this day's route in Google Maps</a>"
    return out + "<p style='font-size:12px;color:#889;margin-top:8px'>Drive times are estimates.</p></div>"


@app.route("/travel/<sid>")
def bb_travel(sid):
    import json, time as _t
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    now = _t.time()
    hits = [x for x in _BB_TRL.get(ip, []) if now - x < 60]
    if len(hits) >= 30:
        return app.response_class(json.dumps({"ok": [], "out": True, "msg": "Too many checks, wait a minute."}), mimetype="application/json")
    _BB_TRL[ip] = hits + [now]
    shop = load().get(sid) or {}
    if not shop or _bb_where(shop) in ("shop", "online"):
        return app.response_class(json.dumps({"ok": [], "out": False, "msg": ""}), mimetype="application/json")
    loc = _bb_geocode(request.args.get("a", ""))
    msg = ""
    if not loc:
        msg = "We couldn't find that address on the map, so times aren't adjusted for driving. Double-check it."
    else:
        base = _bb_base_loc(shop)
        rad = float(shop.get("radius") or 0)
        if base and rad > 0 and _bb_miles(base, loc) > rad:
            return app.response_class(json.dumps({"ok": [], "out": True, "msg": "Sorry, that address is outside our service area" +
                                                  (" (" + shop["area"] + ")" if shop.get("area") else "") + "."}), mimetype="application/json")
        msg = "Times below leave room to drive to you."
    ok = _bb_ok_slots(shop, request.args.get("svc") or None, request.args.get("staff", ""), "home", loc)
    return app.response_class(json.dumps({"ok": ok, "out": False, "msg": msg}), mimetype="application/json")


_bb_page_extras_v4 = _bb_page_extras


def _bb_page_extras(sid, shop):
    out = _bb_page_extras_v4(sid, shop)
    if _bb_where(shop) not in ("shop", "online"):
        out = ("<p style='font-weight:700;color:#1faa59'>&#128663; " + ("We come to you" if _bb_where(shop) == "mobile" else "Visit us, or we come to you") +
               (" &middot; Serving " + str(escape(shop["area"])) if shop.get("area") else "") + "</p>") + out
    return out


_bb_run_reminders_v4 = _bb_run_reminders


def _bb_run_reminders(host):
    n = _bb_run_reminders_v4(host)
    try:
        d = load()
        due = []
        for sid, shop in d.items():
            if not isinstance(shop, dict) or _bb_where(shop) in ("shop", "online"):
                continue
            now = _bb_local_now(shop)
            for b in shop.get("bookings", []):
                dt = _bb_pdt(b.get("when"))
                if not dt or b.get("at") != "home" or b.get("lv_sent") or _bb_is_cxl(b):
                    continue
                if timedelta(0) < dt - now <= timedelta(minutes=90):
                    prevs = [(_bb_pdt(x["when"]), x) for x in shop.get("bookings", []) if x is not b and not _bb_is_cxl(x) and _bb_pdt(x.get("when"))
                             and _bb_pdt(x["when"]).date() == dt.date() and _bb_pdt(x["when"]) < dt]
                    src = _bb_b_loc(shop, max(prevs, key=lambda z: z[0])[1]) if prevs else _bb_base_loc(shop)
                    dm = _bb_drive_min(src, _bb_b_loc(shop, b), now)
                    b["lv_sent"] = True
                    due.append((shop, dict(b), dt, dm))
        if due:
            save(d)
            for shop, b, dt, dm in due:
                leave = (dt - timedelta(minutes=(dm or 15) + 5)).strftime("%I:%M %p").lstrip("0")
                try:
                    notify("Next house call: " + b.get("name", "") + " at " + dt.strftime("%I:%M %p").lstrip("0"),
                           b.get("service", "") + " for " + b.get("name", "") + " at " + dt.strftime("%I:%M %p").lstrip("0") + "\nAddress: " + b.get("caddr", "") +
                           ("\nAbout " + str(dm) + " min drive. Leave by " + leave + "." if dm is not None else "\nLeave by " + leave + " (drive time unknown).") +
                           ("\nDirections: " + _bb_cust_dir(b) if _bb_cust_dir(b) else "") + ("\nCall: " + b["phone"] if b.get("phone") else ""),
                           shop.get("email") or None)
                except Exception as ex:
                    print("leave-by mail:", ex)
        n += len(due)
    except Exception as ex:
        print("leave-by:", ex)
    return n
# ===== END BB UPGRADE 4 =====


# ===== BB UPGRADE 5: address check + online/video mode =====
def _bb_needs_addr(shop):
    return isinstance(shop, dict) and _bb_where(shop) in ("shop", "both") and not (shop.get("addr") or "").strip()


def _bb_meet(shop):
    u = (shop or {}).get("meet") or ""
    return u if u.startswith("https://") else ""


def _bb_v5_edit():
    try:
        p = request.path.strip("/").split("/")
        if request.method == "POST" and len(p) == 2 and p[0] == "edit" and request.form.get("bb_hours") == "1" and "where" in request.form:
            if not _bb_sess.get("own_" + p[1]):
                return None
            u = " ".join((request.form.get("meet") or "").split())[:300]
            if request.form.get("where") == "online" and not u.startswith("https://"):
                return (S + "<h1>Video call link needed</h1><p>For online appointments, paste your Zoom, Google Meet or other video link "
                        "(it starts with https://). Customers get it in their confirmation and reminders.</p><a href='javascript:history.back()'>Go back</a>")
            if u and not u.startswith("https://"):
                return S + "<h1>That link doesn't look right</h1><p>Video links start with https://</p><a href='javascript:history.back()'>Go back</a>"
            d = load()
            shop = d.get(p[1])
            if shop is not None and shop.get("meet", "") != u:
                shop["meet"] = u
                save(d)
    except Exception as e:
        print("v5 edit:", e)
    return None


app.before_request_funcs.setdefault(None, []).insert(0, _bb_v5_edit)


def _bb_v5_create():
    try:
        if request.method == "POST" and request.path.rstrip("/") == "/create" and request.form.get("where") == "online":
            u = (request.form.get("meet") or "").strip()
            if u and not u.startswith("https://"):
                return S + "<h1>That video link doesn't look right</h1><p>Video links start with https://</p><a href='javascript:history.back()'>Go back</a>"
    except Exception as e:
        print("v5 create:", e)
    return None


app.before_request_funcs.setdefault(None, []).insert(0, _bb_v5_create)

_bb_where_form_v5 = _bb_where_form


def _bb_where_form(shop):
    return (_bb_where_form_v5(shop) +
            "<p>Video call link (for online appointments)</p><input name='meet' maxlength='300' placeholder='https://zoom.us/j/... or https://meet.google.com/...' value='" +
            str(escape(shop.get("meet", ""))) + "'>")


_bb_listed_v5 = _bb_listed


def _bb_listed(v):
    if _bb_needs_addr(v):
        return False
    if isinstance(v, dict) and _bb_where(v) == "online" and not _bb_meet(v):
        return False
    return _bb_listed_v5(v)


_bb_page_extras_v5 = _bb_page_extras


def _bb_page_extras(sid, shop):
    out = _bb_page_extras_v5(sid, shop)
    if _bb_where(shop) == "online":
        out = "<p style='font-weight:700;color:#1a6dff'>&#128187; Online appointment &middot; you'll get a video call link after booking</p>" + out
    return out


_bb_notify_v5 = notify


def notify(subject, body, to=None):
    try:
        import re as _re
        m_ = _re.search(r"/m/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)", body or "")
        if m_:
            shop = load().get(m_.group(1)) or {}
            if _bb_where(shop) == "online" and _bb_meet(shop) and _bb_meet(shop) not in body and (to or "").lower() != (shop.get("email") or "").lower():
                body += "\n\nThis is an online appointment. Join your video call here:\n" + _bb_meet(shop)
    except Exception:
        pass
    return _bb_notify_v5(subject, body, to)


@app.after_request
def _bb_v5_after(resp):
    try:
        p = request.path.strip("/").split("/")
        if request.method == "POST" and request.path.rstrip("/") == "/create" and resp.status_code in (301, 302, 303) and request.form.get("where") == "online":
            sid = resp.headers.get("Location", "").rstrip("/").split("/")[-1].split("?")[0]
            d = load()
            if sid in d:
                d[sid]["where"] = "online"
                u = (request.form.get("meet") or "").strip()
                if u.startswith("https://"):
                    d[sid]["meet"] = u[:300]
                save(d)
            return resp
        if resp.status_code != 200 or resp.mimetype != "text/html":
            return resp
        if request.method == "POST" and request.path.rstrip("/") == "/setup":
            h = resp.get_data(as_text=True)
            i = h.find("<input name='addr'")
            i = h.find(">", i) + 1 if i >= 0 else -1
            if i > 0 and "name='meet'" not in h:
                h = h[:i] + ("<input name='meet' id='bbmeet' style='display:none' placeholder='Video call link (https://zoom.us/... or https://meet.google.com/...)'>"
                             "<script>document.addEventListener('DOMContentLoaded',function(){var s=document.getElementById('bbwhere'),m=document.getElementById('bbmeet');"
                             "if(!s||!m)return;function f(){m.style.display=s.value==='online'?'block':'none'}s.addEventListener('change',f);f()});</script>") + h[i:]
                resp.set_data(h)
            return resp
        if request.method != "GET":
            return resp
        if len(p) == 3 and p[0] == "m":
            shop = load().get(p[1]) or {}
            h = resp.get_data(as_text=True)
            if _bb_where(shop) == "online" and _bb_meet(shop) and "id='bbmeet'" not in h:
                btn = ("<a id='bbmeet' href='" + str(escape(_bb_meet(shop))) + "' target='_blank' rel='noopener' style='display:block;text-align:center;padding:14px;margin:12px 0;"
                       "background:#1a6dff;color:#fff;border-radius:12px;text-decoration:none;font-weight:800;font-size:17px'>&#128187; Join video call</a>"
                       "<p style='text-align:center;font-size:13px;color:#556;margin:-6px 0 10px'>Open this link at your appointment time.</p>")
                i = h.find("</h1>")
                i = i + 5 if i >= 0 else 0
                resp.set_data(h[:i] + btn + h[i:])
        elif len(p) == 2 and p[0] == "d":
            shop = load().get(p[1]) or {}
            h = resp.get_data(as_text=True)
            if "total bookings" in h and "id='bbwarn'" not in h:
                msg = ""
                if _bb_needs_addr(shop):
                    msg = ("<b>&#9888; Customers can't find you.</b> Add your business address so customers get directions. "
                           "Your business is hidden from the directory until you do. If you only do house calls or online appointments, change "
                           "\"Where do appointments happen?\" instead.")
                elif _bb_where(shop) == "online" and not _bb_meet(shop):
                    msg = "<b>&#9888; Add your video call link.</b> Online customers need it to join. Your business is hidden from the directory until you add it."
                if msg:
                    card = ("<div class='card' id='bbwarn' style='background:#fff3cd;border-left:6px solid #f0a500'>" + msg +
                            "<br><a href='/edit/" + p[1] + "' style='display:inline-block;margin-top:8px;font-weight:700'>&#9999;&#65039; Fix it now</a></div>")
                    i = h.find("<div class='wrap'>")
                    i = i + len("<div class='wrap'>") if i >= 0 else h.find("total bookings")
                    if i < 0:
                        i = 0
                    elif "<div class='wrap'>" not in h:
                        i = h.rfind("<div", 0, i)
                    resp.set_data(h[:i] + card + h[i:])
        elif p and p[0] == "mine":
            h = resp.get_data(as_text=True)
            d = load()
            for sid, v in d.items():
                if not isinstance(v, dict):
                    continue
                lab = ""
                if _bb_needs_addr(v):
                    lab = "&#9888; Needs business address"
                elif _bb_where(v) == "online" and not _bb_meet(v):
                    lab = "&#9888; Needs video call link"
                if not lab:
                    continue
                i = h.find("href='/d/" + sid + "?")
                if i < 0:
                    i = h.find("href='/d/" + sid + "'")
                if i < 0:
                    continue
                j = h.find("</a>", i)
                seg = h[i:j]
                if "Needs payments connected" in seg:
                    h = h[:i] + seg.replace("Needs payments connected", lab, 1) + h[j:]
            resp.set_data(h)
    except Exception as ex:
        print("v5 after:", ex)
    return resp
# ===== END BB UPGRADE 5 =====


# ===== BB UPGRADE 6: Mapbox live traffic =====
_BB_MBX = {"cache": {}, "day": "", "n": 0, "fail": 0}
_bb_drive_min_est = _bb_drive_min


def _bb_mapbox_min(p, q, when=None):
    import os, json, time as _t, urllib.request, urllib.error
    tok = os.environ.get("MAPBOX_TOKEN", "").strip()
    if not tok or not p or not q:
        return None
    if _BB_MBX["fail"] >= 3 and _t.time() - _BB_MBX.get("fail_t", 0) < 600:
        return None
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if _BB_MBX["day"] != today:
        _BB_MBX.update({"day": today, "n": 0})
    now_l = datetime.utcnow() - timedelta(hours=10)
    future = bool(when) and when > now_l + timedelta(minutes=20)
    slot = when.strftime("%Y-%m-%dT%H") if future else "now-" + str(int(_t.time() // 900))
    key = (round(p[0], 4), round(p[1], 4), round(q[0], 4), round(q[1], 4), slot)
    hit = _BB_MBX["cache"].get(key)
    if hit and _t.time() - hit[1] < (21600 if future else 900):
        return hit[0]
    if _BB_MBX["n"] >= 2500:
        return None
    u = ("https://api.mapbox.com/directions/v5/mapbox/driving-traffic/%.6f,%.6f;%.6f,%.6f?overview=false&access_token=%s" % (p[1], p[0], q[1], q[0], tok))
    if future:
        u += "&depart_at=" + when.strftime("%Y-%m-%dT%H:%M")
    try:
        _BB_MBX["n"] += 1
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "business-bookie/1.0"}), timeout=6)
        js = json.loads(r.read().decode())
        sec = float(js["routes"][0]["duration"])
        mins = int(-(-(sec / 60.0 + 3) // 5) * 5)
        if len(_BB_MBX["cache"]) > 5000:
            _BB_MBX["cache"].clear()
        _BB_MBX["cache"][key] = (mins, _t.time())
        _BB_MBX["fail"] = 0
        return mins
    except urllib.error.HTTPError as ex:
        print("mapbox http:", ex.code)
        return None
    except Exception as ex:
        _BB_MBX["fail"] += 1
        _BB_MBX["fail_t"] = _t.time()
        print("mapbox:", ex)
        return None


def _bb_drive_min(p, q, when=None):
    d = _bb_miles(p, q)
    if d is None:
        return None
    if d < 0.05:
        return 0
    if _BB_CTX.get("live") and not _BB_CTX.get("nolive"):
        m = _bb_mapbox_min(p, q, when)
        if m is not None:
            return m
    return _bb_drive_min_est(p, q, when)


def _bb_live(fn):
    def w(*a, **k):
        old = _BB_CTX.get("live")
        _BB_CTX["live"] = True
        try:
            return fn(*a, **k)
        finally:
            _BB_CTX["live"] = old
    return w


def _bb_nolive(fn):
    def w(*a, **k):
        old = _BB_CTX.get("nolive")
        _BB_CTX["nolive"] = True
        try:
            return fn(*a, **k)
        finally:
            _BB_CTX["nolive"] = old
    return w


_bb_ok_slots = _bb_nolive(_bb_ok_slots)
_bb_route_card = _bb_live(_bb_route_card)
_bb_run_reminders = _bb_live(_bb_run_reminders)


def _bb_v6_live_on():
    try:
        p = request.path.strip("/").split("/")
        if request.method == "POST" and len(p) == 2 and p[0] == "book":
            _BB_CTX["live"] = True
    except Exception:
        pass
    return None


app.before_request_funcs.setdefault(None, []).insert(0, _bb_v6_live_on)


@app.teardown_request
def _bb_v6_live_off(exc=None):
    _BB_CTX["live"] = False
    _BB_CTX["nolive"] = False


@app.route("/traffic/check")
def bb_traffic_check():
    import os
    if not os.environ.get("MAPBOX_TOKEN"):
        return app.response_class("mapbox: no token set\n", mimetype="text/plain")
    a, b = (21.3972, -157.7394), (21.3351, -158.0861)
    now_l = datetime.utcnow() - timedelta(hours=10)
    t5 = (now_l + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
    while t5.weekday() >= 5:
        t5 += timedelta(days=1)
    live = _bb_mapbox_min(a, b, None)
    pred = _bb_mapbox_min(a, b, t5)
    est = _bb_drive_min_est(a, b, t5)
    return app.response_class("Kailua -> Kapolei\nlive traffic now: %s min\npredicted %s: %s min\nold estimate at 5pm: %s min\nlookups today: %d\n" %
                              (live, t5.strftime("%a %I:%M %p"), pred, est, _BB_MBX["n"]), mimetype="text/plain")
# ===== END BB UPGRADE 6 =====


# ===== BB MANIFEST EXTRAS =====
@app.after_request
def _bb_manifest_extras(resp):
    try:
        if request.path.rstrip("/") in ("/manifest.json", "/manifest.webmanifest") and resp.status_code == 200:
            import json as _j
            m = _j.loads(resp.get_data(as_text=True))
            m.setdefault("id", "/")
            m.setdefault("orientation", "portrait")
            m.setdefault("lang", "en-US")
            m.setdefault("dir", "ltr")
            m.setdefault("categories", ["business", "productivity", "lifestyle"])
            m.setdefault("display_override", ["standalone", "minimal-ui"])
            resp.set_data(_j.dumps(m))
    except Exception as e:
        print("manifest extras:", e)
    return resp
# ===== END BB MANIFEST EXTRAS =====


# ===== BB OFFLINE =====
_BB_SWJS = r"""
// ===== BB OFFLINE =====
var BB_CACHE='bb-offline-v1';
self.addEventListener('install',function(e){e.waitUntil(caches.open(BB_CACHE).then(function(c){return Promise.all(['/offline','/manifest.json'].map(function(u){return c.add(u).catch(function(){})}))}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k.indexOf('bb-offline-')===0&&k!==BB_CACHE}).map(function(k){return caches.delete(k)}))}))});
self.addEventListener('fetch',function(e){var r=e.request;if(r.method!=='GET'||r.mode!=='navigate')return;e.respondWith(fetch(r).catch(function(){return caches.match('/offline').then(function(x){return x||new Response('You are offline. Check your connection and try again.',{headers:{'Content-Type':'text/plain'}})})}))});
// ===== END BB OFFLINE =====
"""


@app.route("/offline")
def bb_offline_page():
    return (S + "<div style='text-align:center;padding:40px 16px'><div style='font-size:56px'>&#128246;</div>"
            "<h1>You're offline</h1><p>Business-Bookie needs an internet connection. Check your Wi-Fi or data, then try again.</p>"
            "<button onclick='location.reload()' style='padding:14px 28px;font-size:17px;font-weight:800;border:0;border-radius:12px;background:#1a6dff;color:#fff'>Try again</button></div>")


@app.after_request
def _bb_offline_sw(resp):
    try:
        if request.path.endswith("sw.js") and resp.status_code == 200:
            js = resp.get_data(as_text=True)
            if "BB OFFLINE" not in js:
                resp.set_data(js + "\n" + _BB_SWJS)
    except Exception as e:
        print("offline sw:", e)
    return resp
# ===== END BB OFFLINE =====


# ===== BB UPGRADE 7: customer page (all my bookings) =====
def _bb_hub_when(w):
    try:
        t = datetime.strptime(w, "%Y-%m-%d %H:%M")
        return t.strftime("%a %b %d").replace(" 0", " ") + " at " + t.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return w or ""


def _bb_hub_find(shop, rt):
    for k in ("bookings", "cancelled"):
        for b in shop.get(k, []) or []:
            if isinstance(b, dict) and b.get("rt") == rt:
                return b
    return None


@app.route("/my/<sid>/<rt>")
def bb_my_page(sid, rt):
    d = load()
    shop = d.get(sid)
    if not isinstance(shop, dict) or not rt:
        return S + "<h1>Not found</h1>", 404
    me = _bb_hub_find(shop, rt)
    if me is None:
        return S + "<h1>Not found</h1><p>This link doesn't match a booking.</p>", 404
    em = (me.get("email") or "").strip().lower()
    mine = [b for b in shop.get("bookings", []) if isinstance(b, dict) and b.get("rt") and
            (b.get("rt") == rt or (em and (b.get("email") or "").strip().lower() == em))]
    try:
        now = _bb_local_now(shop).strftime("%Y-%m-%d %H:%M")
    except Exception:
        now = (datetime.utcnow() - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M")
    up = sorted([b for b in mine if (b.get("when") or "") >= now], key=lambda b: b.get("when") or "")
    past = sorted([b for b in mine if (b.get("when") or "") < now], key=lambda b: b.get("when") or "", reverse=True)
    nm = str(escape(shop.get("name", "")))
    base = _bb_base()
    btn = "display:block;text-align:center;padding:13px;margin:8px 0;border-radius:12px;text-decoration:none;font-weight:800"
    h = "<h1>Your bookings at " + nm + "</h1>"
    if me.get("name"):
        h += "<p>Hi " + str(escape(me.get("name", "").split(" ")[0])) + "! Everything you have booked here is on this page. No login needed.</p>"
    if up:
        h += "<h3>Coming up</h3>"
        for b in up:
            who = ""
            try:
                sn = _bb_staff_name(shop, b.get("staff")) if b.get("staff") else ""
                who = (" with " + str(escape(sn))) if sn else ""
            except Exception:
                pass
            h += ("<div class='card' style='margin:8px 0'><b>" + str(escape(b.get("service", ""))) + "</b>" + who +
                  "<div style='font-size:17px;margin:4px 0'>&#128197; " + str(escape(_bb_hub_when(b.get("when", "")))) + "</div>"
                  "<a href='/m/" + sid + "/" + str(escape(b["rt"])) + "' style='" + btn + ";background:#1a6dff;color:#fff'>View, directions, reschedule or cancel</a></div>")
    else:
        h += "<p>You don't have any upcoming bookings here right now.</p>"
    h += "<a href='/b/" + sid + "' style='" + btn + ";border:2px solid #1a6dff;color:#1a6dff'>&#10133; Book another appointment</a>"
    if past:
        h += "<p style='color:#556;font-size:14px'>Past visits here: " + str(len(past)) + " (last: " + str(escape(_bb_hub_when(past[0].get("when", "")))) + ")</p>"
    try:
        import segno
        mu = base + "/my/" + sid + "/" + rt
        bu = base + "/b/" + sid
        mi = segno.make(mu, error="m").png_data_uri(scale=8, border=2)
        bi = segno.make(bu, error="m").png_data_uri(scale=8, border=2)
        fn = "".join(c for c in shop.get("name", "") if c.isalnum()) or "booking"
        qs = "width:200px;max-width:80%;image-rendering:pixelated"
        h += ("<div class='card' style='text-align:center;margin-top:14px'><b>&#128273; Your personal QR code</b>"
              "<p style='font-size:14px;color:#556;margin:4px 0'>Screenshot or save it. Scan it any time to come back to this page.</p>"
              "<img src='" + mi + "' alt='Your QR code' style='" + qs + "'><br>"
              "<a href='" + mi + "' download='" + fn + "-my-bookings.png' style='font-weight:700'>&#11015;&#65039; Save my QR</a>"
              "<p style='font-size:12px;color:#889;margin:6px 0 0'>Keep this private. Anyone with it can see your bookings here.</p></div>"
              "<div class='card' style='text-align:center;margin-top:14px'><b>&#128241; " + nm + "'s booking QR</b>"
              "<p style='font-size:14px;color:#556;margin:4px 0'>Share it with a friend, or scan it to book again.</p>"
              "<img src='" + bi + "' alt='Booking QR code' style='" + qs + "'><br>"
              "<a href='" + bi + "' download='" + fn + "-book.png' style='font-weight:700'>&#11015;&#65039; Save booking QR</a></div>")
    except Exception as e:
        print("hub qr:", e)
    try:
        h += _bb_push_box(sid, rt, "customer")
    except Exception:
        pass
    return S + h


def bb_qr_customer(sid, rt):
    d = load()
    if sid not in d or _bb_hub_find(d[sid], rt) is None:
        return S + "<h1>Booking not found</h1>", 404
    return bb_my_page(sid, rt)


app.view_functions["bb_qr_customer"] = bb_qr_customer


@app.after_request
def _bb_hub_link(resp):
    try:
        p = request.path.strip("/").split("/")
        if request.method == "GET" and len(p) == 3 and p[0] == "m" and resp.status_code == 200 and resp.mimetype == "text/html":
            h = resp.get_data(as_text=True)
            if "<h1>Your booking</h1>" in h and "id='bbhub'" not in h:
                a = ("<a id='bbhub' href='/my/" + p[1] + "/" + p[2] + "' style='display:block;text-align:center;padding:13px;margin:12px 0;"
                     "border:2px solid #1a6dff;border-radius:12px;text-decoration:none;font-weight:800'>&#128203; All my bookings + my QR code</a>")
                i = h.rfind("</body>")
                resp.set_data(h[:i] + a + h[i:] if i >= 0 else h + a)
        elif request.method == "GET" and len(p) == 2 and p[0] == "b" and resp.status_code == 200 and resp.mimetype == "text/html":
            h = resp.get_data(as_text=True)
            if "id='bbappnote'" not in h and "<form" in h:
                n = ("<div id='bbappnote' style='display:none;background:#eef3ff;border-radius:10px;padding:10px 12px;margin:10px 0;font-size:15px'>"
                     "&#128241; <b>You're using the app.</b> After you book, tap <b>Turn on notifications</b> and you'll get reminders and updates "
                     "for this booking right on this phone.</div>"
                     "<script>try{if(window.matchMedia('(display-mode: standalone)').matches||navigator.standalone||"
                     "document.referrer.indexOf('android-app://')===0){document.getElementById('bbappnote').style.display='block'}}catch(e){}</script>")
                i = h.find("<form")
                resp.set_data(h[:i] + n + h[i:])
    except Exception as e:
        print("hub link:", e)
    return resp


_bb_push_for_v7 = _bb_push_for


def _bb_push_for(subject, body, to):
    try:
        import re as _re
        m_ = _re.search(r"https?://\S+/m/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+", body or "")
        if m_ and not (body or "").lstrip().startswith(m_.group(0)):
            body = m_.group(0) + " " + (body or "")
    except Exception:
        pass
    return _bb_push_for_v7(subject, body, to)
# ===== END BB UPGRADE 7 =====


# ===== BB ASSETLINKS =====
_BB_APP_PKG = "com.business_bookie.twa"
_BB_APP_SHA = [
    "B5:E5:2D:0C:65:DA:C1:90:A6:6A:38:0A:AF:41:F7:25:01:EA:B6:A1:58:33:24:00:E5:5A:5B:1C:92:7E:DA:02",
]


@app.route("/.well-known/assetlinks.json")
def bb_assetlinks():
    import json as _j
    data = [{"relation": ["delegate_permission/common.handle_all_urls"],
             "target": {"namespace": "android_app", "package_name": _BB_APP_PKG, "sha256_cert_fingerprints": _BB_APP_SHA}}]
    return app.response_class(_j.dumps(data), mimetype="application/json")
# ===== END BB ASSETLINKS =====





# ===== BB DELETE DATA =====
_BB_DEL_TXT = ("You can ask us to delete your account and all of your data at any time. Email "
               "<a href='mailto:infinitymichael29@gmail.com'>infinitymichael29@gmail.com</a> from the email on your account "
               "and ask us to delete it. We remove your business or booking records, including your name, email, phone number "
               "and appointment history, within 30 days.")


@app.route("/delete-data")
def bb_delete_data():
    return S + "<h1>Delete your Business-Bookie data</h1><p>" + _BB_DEL_TXT + "</p><p><a href='/privacy'>Back to Privacy Policy</a></p>"


@app.after_request
def _bb_privacy_delete(resp):
    try:
        if request.path.rstrip("/") == "/privacy" and resp.status_code == 200 and resp.mimetype == "text/html":
            h = resp.get_data(as_text=True)
            if "id='bbdel'" not in h:
                note = "<h3 id='bbdel'>Delete your data</h3><p>" + _BB_DEL_TXT + "</p>"
                i = h.rfind("</body>")
                resp.set_data(h[:i] + note + h[i:] if i >= 0 else h + note)
    except Exception as e:
        print("privacy delete:", e)
    return resp
# ===== END BB DELETE DATA =====


import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
