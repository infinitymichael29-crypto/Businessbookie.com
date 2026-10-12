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
    hrs = days + " | " + shop.get("open", "") + " - " + shop.get("close", "")
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


import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
