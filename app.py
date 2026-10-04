import pandas as pd
import streamlit as st

st.set_page_config(page_title="CareCompass AI", page_icon="🩺", layout="wide")

from agents import followup, orchestrator, outreach, scheduler  # noqa: E402
from agents.triage import LANGS  # noqa: E402
from ui import styles, tech_panel  # noqa: E402
from utils import audit, data, llm, safety  # noqa: E402

st.markdown(styles.CSS, unsafe_allow_html=True)
D = data.load()
for k, v in {"chat": [], "last": None, "appts": [], "approved": [], "drafts": {}, "booking": None}.items():
    st.session_state.setdefault(k, v)

EXAMPLES = ["My child has a fever and cough for two days", "I have a skin rash and itching",
            "Knee pain when I climb stairs", "I need an antenatal checkup", "I have severe chest pain"]

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown(f"<div class='side-title'>{D['hospital']}</div>", unsafe_allow_html=True)
    lang = st.selectbox("Patient language", list(LANGS))
    key, source = llm.key_info()
    if key:
        verified = " and verified" if st.session_state.get("llm_verified") else ""
        st.markdown(f"<div class='status ok'>Gemini key loaded{verified}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='status off'>Demo mode: no Gemini key found. {llm.status_hint()}</div>",
                    unsafe_allow_html=True)
    st.markdown(f"<div class='note'>Emergency? Call <b>{safety.EMERGENCY_LINE}</b>. CareCompass AI does not diagnose or "
                "prescribe. Clinicians make every clinical decision.</div>", unsafe_allow_html=True)
    st.divider()
    tech_panel.render()

# ---------------- header ----------------
st.markdown(styles.hero(), unsafe_allow_html=True)
tab_chat, tab_doc, tab_appt, tab_follow, tab_out, tab_dash = st.tabs(
    ["Patient assistant", "Our doctors", "Appointments", "Follow-up reminders", "Preventive outreach", "Operations dashboard"])

# ---------------- patient assistant ----------------
with tab_chat:
    st.markdown(styles.steps(), unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large")

    with left:
        with st.chat_message("assistant"):
            st.write("Assalam-o-Alaikum! I am the CareCompass assistant. Tell me what you are feeling or what you need: "
                     "the symptom, who it is for and how long it has lasted. I can suggest the right department and "
                     "book a visit. I cannot diagnose or prescribe.")
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    with right:
        st.markdown("**Try an example**")
        for ex in EXAMPLES:
            if st.button(ex, key=f"ex-{ex}", width="stretch"):
                st.session_state["pending"] = ex

        res = st.session_state.last
        st.markdown("**Your visit**")
        if not res:
            st.markdown("<div class='card muted'>Your suggested department and urgency will appear here after your first message.</div>",
                        unsafe_allow_html=True)
        elif res["urgency"] == "emergency":
            st.markdown(f"<div class='alert'>Possible emergency. Call {safety.EMERGENCY_LINE} or go to the nearest "
                        "emergency department now. Hospital staff are alerted in the audit log.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card'><h5>{res['department']}</h5>"
                        f"<span class='pill u-{res['urgency']}'>{res['urgency'].replace('_', ' ')}</span>"
                        f"<p style='margin:8px 0 0;font-size:.88rem;color:#4c6470'>Note for the clinician: {res['summary']}</p></div>",
                        unsafe_allow_html=True)
            if res["slots"]:
                with st.form("book"):
                    slot = st.selectbox("Available times", res["slots"], format_func=lambda s: s["label"])
                    name = st.text_input("Patient name")
                    phone = st.text_input("Phone number")
                    consent = st.checkbox("I agree to be contacted about this appointment and to share my symptom summary with the clinician.")
                    if st.form_submit_button("Confirm appointment", type="primary", width="stretch"):
                        if not (name.strip() and phone.strip() and consent):
                            st.error("Please enter your name and phone number and tick the consent box.")
                        else:
                            st.session_state.booking = scheduler.book(slot, name.strip(), phone.strip(), res["summary"], res["urgency"])
                            st.session_state.last["slots"] = scheduler.open_slots(res["department"])
                            st.rerun()
        b = st.session_state.booking
        if b:
            st.success(f"Booked {b['id']}: {b['doctor']}, {b['date']} at {b['time']}.")

    prompt = st.chat_input("Type your symptoms or question") or st.session_state.pop("pending", None)
    if prompt:
        st.session_state.booking = None
        st.session_state.chat.append({"role": "user", "content": prompt})
        r = orchestrator.handle(st.session_state.chat, lang)
        st.session_state.last = r
        reply = r["advice"] + (f"\n\n{r['follow_up_question']}" if r["follow_up_question"] else "")
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

# ---------------- doctors ----------------
with tab_doc:
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    st.subheader("Our doctors")
    st.caption(f"{len(D['doctors'])} doctors across {len(D['departments'])} departments. To book, describe your "
               "problem in the Patient assistant tab and pick a time.")
    dept = st.selectbox("Department", ["All departments"] + D["departments"])
    docs = [d for d in D["doctors"] if dept in ("All departments", d["department"])]
    cols = st.columns(2)
    for i, doc in enumerate(docs):
        nxt = next((s for s in scheduler.open_slots(doc["department"], limit=60) if s["doctor"] == doc["name"]), None)
        with cols[i % 2].container(border=True):
            st.markdown(f"**{doc['name']}**  \n{doc['department']}")
            st.caption(f"Clinic days: {', '.join(DAYS[d] for d in doc['days'])}  \nTimings: {', '.join(doc['times'])}")
            st.caption(f"Next available: {nxt['date']} at {nxt['time']}" if nxt else "No open slots in the next 10 days")

# ---------------- staff tabs ----------------
with tab_appt:
    st.subheader("Booked appointments")
    st.caption("Staff view. Appointments booked by patients appear here with the clinician note.")
    if st.session_state.appts:
        df = pd.DataFrame(st.session_state.appts)
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False), "appointments.csv", "text/csv")
    else:
        st.info("No appointments yet. Book one from the Patient assistant tab.")


def draft_flow(k, label, make, who):
    if st.button("Draft message", key=f"d-{k}"):
        text, src = make()
        st.session_state.drafts[k] = text
        audit.log(label, "draft created", f"{who} via {src}")
    if k in st.session_state.drafts:
        msg = st.text_area("Review and edit before approving", st.session_state.drafts[k], key=f"t-{k}")
        if st.button("Approve and send (simulated)", key=f"a-{k}", type="primary"):
            st.session_state.approved.append({"type": label, "to": who, "message": msg})
            audit.log(label, "approved by staff", who)
            st.success("Approved. In production this is where WhatsApp or SMS is connected.")


with tab_follow:
    st.subheader("Follow-ups due")
    st.caption("The follow-up agent lists patients who are due. You review each draft before anything is sent.")
    window = st.slider("Show follow-ups due within (days)", 0, 14, 5)
    rows = followup.due(window)
    if not rows:
        st.info("No follow-ups due in this window.")
    for p in rows:
        with st.expander(f"{p['name']} - {p['reason']} - due {p['due_date']}"):
            draft_flow(f"fu-{p['id']}", "Follow-up", lambda p=p: followup.draft(p, lang), p["id"])

with tab_out:
    st.subheader("Preventive outreach")
    st.caption("The outreach agent finds patients eligible for a prevention program and drafts invitations.")
    prog = st.selectbox("Program", list(D["programs"]))
    people = outreach.cohort(prog)
    st.write(f"**{len(people)}** eligible patients found.")
    for p in people:
        with st.expander(f"{p['name']} (age {p['age']})"):
            draft_flow(f"out-{prog}-{p['id']}", "Outreach", lambda p=p: outreach.draft(prog, p, lang), p["id"])

with tab_dash:
    st.subheader("Hospital overview")
    st.caption("This page is for hospital management. It counts what the assistant did in this session. "
               "Every number starts at 0 and grows as patients chat, book visits and staff approve messages.")
    log = audit.frame()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patient messages", sum(m["role"] == "user" for m in st.session_state.chat))
    c1.caption("Messages typed by patients")
    c2.metric("Emergencies escalated", int((log["level"] == "alert").sum()) if len(log) else 0)
    c2.caption("Chats with danger signs, sent to 1122 guidance")
    c3.metric("Appointments booked", len(st.session_state.appts))
    c3.caption("Visits confirmed by patients")
    c4.metric("Messages approved", len(st.session_state.approved))
    c4.caption("Reminders and invitations approved by staff")
    if st.session_state.appts:
        st.markdown("**Appointments by department**")
        st.bar_chart(pd.DataFrame(st.session_state.appts)["department"].value_counts())
    st.subheader("Activity log")
    st.caption("A time-stamped record of every action the agents took, kept for review. You can download it as a file.")
    if len(log):
        st.dataframe(log.iloc[::-1], width="stretch", hide_index=True)
        st.download_button("Download activity log", log.to_csv(index=False), "activity_log.csv", "text/csv")
    else:
        st.info("Nothing yet. Use the Patient assistant tab and actions will appear here.")