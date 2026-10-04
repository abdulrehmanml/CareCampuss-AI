"""Scheduling agent: finds open slots and books them with patient consent."""
import datetime as dt

import streamlit as st

from utils import audit, data, trace


def open_slots(department: str, days_ahead: int = 10, limit: int = 8) -> list[dict]:
    booked = {(a["doctor"], a["date"], a["time"]) for a in st.session_state.get("appts", [])}
    today, slots = dt.date.today(), []
    for doc in (x for x in data.load()["doctors"] if x["department"] == department):
        for i in range(1, days_ahead + 1):
            day = today + dt.timedelta(days=i)
            if day.weekday() in doc["days"]:
                for t in doc["times"]:
                    if (doc["name"], str(day), t) not in booked:
                        slots.append({"doctor": doc["name"], "department": department,
                                      "date": str(day), "time": t,
                                      "label": f"{day:%a %d %b}, {t} - {doc['name']}"})
    return sorted(slots, key=lambda s: (s["date"], s["time"]))[:limit]


def book(slot: dict, name: str, phone: str, summary: str, urgency: str) -> dict:
    appt = {"id": f"A-{len(st.session_state.get('appts', [])) + 1:03d}", "patient": name, "phone": phone,
            **{k: slot[k] for k in ("doctor", "department", "date", "time")},
            "urgency": urgency, "clinician_note": summary}
    st.session_state.setdefault("appts", []).append(appt)
    audit.log("Scheduler", "booked", f"{appt['id']} {appt['department']} {appt['date']} {appt['time']}")
    trace.add("5. Booking", "Scheduling agent",
              "Chosen slot, patient name and phone (kept in this app only, never sent to Gemini), consent ticked, triage summary",
              f"Appointment {appt['id']} saved and visible to staff", 0)
    return appt
