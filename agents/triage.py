"""Intake & triage agent. Routes and advises; never diagnoses or prescribes."""
import time

from utils import data, llm, safety, trace

LANGS = {"English": "English", "Urdu (اردو)": "Urdu (Urdu script)", "Roman Urdu": "Roman Urdu"}
URGENCIES = {"emergency", "urgent", "routine", "self_care"}

SYSTEM = """You are the intake and triage agent of a hospital care-navigation service in Pakistan.
Rules: never diagnose, never prescribe or name medicine doses, give only general protocol-style guidance,
and be honest when unsure. If symptoms may be life-threatening set urgency to "emergency".
Return JSON with exactly these keys:
urgency: one of emergency, urgent, routine, self_care
department: one of {depts}
summary: one factual sentence for the clinician (English)
advice: 2-3 short, kind sentences for the patient, written in {lang}
follow_up_question: one short question if key information is missing, else empty string"""


def _rules(text, d, note):
    t = text.lower()
    dept = next((k for k, words in d["keywords"].items() if any(w in t for w in words)), "General Medicine")
    return {"urgency": "routine", "department": dept, "summary": f"Patient reports: {text[:160]}",
            "advice": f"{note} I matched your message to a department using keywords. "
                      "Please choose a time below and a clinician will assess you.",
            "follow_up_question": ""}


def run(history: list[dict], lang: str) -> dict:
    d, text = data.load(), history[-1]["content"]

    t0 = time.perf_counter()
    flagged = safety.is_emergency(text)
    trace.add("2. Safety screen", "Rule engine (no AI)",
              f"Patient text checked against {len(safety.EMERGENCY_TERMS)} emergency terms (English, Roman Urdu, Urdu)",
              "EMERGENCY found - AI skipped, 1122 guidance shown" if flagged else "No red-flag terms found",
              trace.since(t0), "alert" if flagged else "ok")
    if flagged:
        return {"urgency": "emergency", "department": "Emergency", "source": "safety-screen",
                "summary": f"Possible emergency: {text[:160]}", "follow_up_question": "",
                "advice": f"This may be an emergency. Call {safety.EMERGENCY_LINE} now or go to the nearest "
                          "emergency department. Do not wait for an appointment."}

    t0 = time.perf_counter()
    if not llm.available():
        out = {**_rules(text, d, "Demo mode: no Gemini key is loaded."), "source": "rules"}
        trace.add("3. Triage", "Keyword rules (demo mode)", "Patient text and the department keyword table",
                  f"{out['department']} (routine)", trace.since(t0), "fallback")
        return out

    convo = "\n".join(f"{m['role']}: {m['content']}" for m in history[-8:])
    system = SYSTEM.format(depts=", ".join(d["departments"]), lang=LANGS[lang])
    try:
        out, raw = llm.generate_json(convo, system)
        out["urgency"] = out.get("urgency") if out.get("urgency") in URGENCIES else "routine"
        if out.get("department") not in d["departments"] + ["Emergency"]:
            out["department"] = "General Medicine"
        out.setdefault("follow_up_question", "")
        out["source"] = "gemini"
        trace.add("3. Triage", f"Gemini ({llm.model()})",
                  f"Last {min(len(history), 8)} chat turns, list of {len(d['departments'])} departments, safety rules in the system prompt",
                  f"{out['urgency']} - {out['department']}", trace.since(t0), "ok",
                  {"System prompt": system, "Conversation sent": convo, "Raw Gemini reply": raw})
    except Exception as exc:
        reason = llm.explain(exc)
        out = {**_rules(text, d, "The AI call failed, so I used backup rules."), "source": "rules (AI error)"}
        trace.add("3. Triage", f"Gemini ({llm.model()}) failed, rules used", "Same inputs as above",
                  f"{out['department']} (routine). Error: {reason}", trace.since(t0), "error")
    return out
