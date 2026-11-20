"""Daily permit alerts by WhatsApp (CallMeBot) and, optionally, email. Reads permits.xlsx (same columns as your file):
EMPLOYEE, STORE, COMPANY, BRAND, CIVIL ID, START DATE, EXPIRATION DATE."""
import os, smtplib, ssl, datetime as dt
import urllib.parse, urllib.request
from email.message import EmailMessage
from zoneinfo import ZoneInfo
from openpyxl import load_workbook

WARN_DAYS = 7

def to_date(v):
    if isinstance(v, dt.datetime): return v.date()
    if isinstance(v, dt.date): return v
    if isinstance(v, (int, float)): return dt.date(1899, 12, 30) + dt.timedelta(days=int(v))
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try: return dt.datetime.strptime(str(v).strip(), f).date()
        except ValueError: pass
    return None

def load(path="permits.xlsx"):
    ws = load_workbook(path, data_only=True).active
    out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or not r[0]: continue
        end = to_date(r[6])
        if end: out.append(dict(employee=str(r[0]).strip(), store=str(r[1] or "").strip(),
            company=str(r[2] or "").strip(), brand=str(r[3] or "").strip(), civil=str(r[4] or "").strip(), end=end))
    return out

def line(p):
    return f"- {p['employee']} | {p['store']} | {p['brand']} | Civil ID {p['civil']} | expires {p['end']}"

def main():
    tz = ZoneInfo(os.getenv("TZ_NAME", "Asia/Kuwait"))
    today = dt.date.fromisoformat(os.environ["TODAY"]) if os.getenv("TODAY") else dt.datetime.now(tz).date()
    permits = load()
    now = [p for p in permits if (p["end"] - today).days == 0]
    soon = [p for p in permits if (p["end"] - today).days == WARN_DAYS]
    if not now and not soon:
        print(f"{today}: nothing to send."); return
    parts = []
    if now:  parts += ["PERMITS EXPIRING TODAY:"] + [line(p) for p in now] + [""]
    if soon: parts += [f"PERMITS EXPIRING IN {WARN_DAYS} DAYS:"] + [line(p) for p in soon]
    text = "\n".join(parts)
    subject = f"Work permit alert: {len(now)} expiring today, {len(soon)} in {WARN_DAYS} days"
    if os.getenv("DRY_RUN"):
        print(subject, "\n" + text); return

    # WhatsApp: WHATSAPP_RECIPIENTS = "+965XXXXXXXX:apikey,+965YYYYYYYY:apikey2"
    for item in filter(None, (x.strip() for x in os.getenv("WHATSAPP_RECIPIENTS", "").split(","))):
        phone, key = item.rsplit(":", 1)
        url = "https://api.callmebot.com/whatsapp.php?" + urllib.parse.urlencode(
            {"phone": phone, "text": subject + "\n\n" + text, "apikey": key})
        with urllib.request.urlopen(url, timeout=30) as r:
            print(f"WhatsApp to {phone}: HTTP {r.status}")

    # Optional email (only if EMAIL_USER is set)
    if os.getenv("EMAIL_USER"):
        msg = EmailMessage()
        msg["Subject"], msg["From"], msg["To"] = subject, os.environ["EMAIL_USER"], os.environ["EMAIL_TO"]
        msg.set_content(text)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as sm:
            sm.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
            sm.send_message(msg, to_addrs=[a.strip() for a in msg["To"].split(",")])
        print("Email sent.")

if __name__ == "__main__":
    main()
