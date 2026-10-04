"""Follow-up agent: finds due follow-ups and drafts reminders for staff approval."""
import datetime as dt

from utils import data, drafting

TEMPLATES = {
    "English": "Dear {name}, a reminder for your follow-up ({reason}) on {date}. Please bring previous reports. Reply to reschedule.",
    "Urdu (اردو)": "محترم {name}، آپ کی فالو اپ وزٹ ({reason}) {date} کو ہے۔ براہ کرم پرانی رپورٹس ساتھ لائیں۔",
    "Roman Urdu": "Mohtaram {name}, aap ki follow-up visit ({reason}) {date} ko hai. Barah-e-karam purani reports sath layen.",
}


def due(within_days: int) -> list[dict]:
    today = dt.date.today()
    rows = [{**p, "due_date": str(today + dt.timedelta(days=p["followup_in_days"]))}
            for p in data.load()["patients"] if p["followup_in_days"] <= within_days]
    return sorted(rows, key=lambda r: r["due_date"])


def draft(p: dict, lang: str):
    base = TEMPLATES[lang].format(name="{name}", reason=p["reason"], date=p["due_date"])
    return drafting.rewrite(base, lang, p["name"])
