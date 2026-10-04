"""Visual design: clinical teal and navy, Public Sans, plain hospital-signage cues."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&display=swap');
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp input, .stApp textarea, .stApp button p, .stApp td, .stApp th { font-family: 'Public Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1rem; max-width: 1180px; }

.hero { display:flex; gap:22px; align-items:center; padding:26px 30px; border-radius:8px; color:#fff;
        background: linear-gradient(115deg,#0b2e3f 0%,#0a6c74 68%,#2f9e75 100%); margin-bottom:16px; }
.hero-badge { flex:0 0 78px; height:78px; border-radius:50%; background:#fff; position:relative; }
.hero-badge:before, .hero-badge:after { content:""; position:absolute; background:#c92a2a; border-radius:3px;
        left:50%; top:50%; transform:translate(-50%,-50%); }
.hero-badge:before { width:42px; height:12px; } .hero-badge:after { width:12px; height:42px; }
.hero h1 { margin:0; font-size:2rem; font-weight:700; color:#fff; letter-spacing:-.3px; }
.hero .sub { font-size:1.02rem; color:#bfe8e4; margin:2px 0 8px; font-weight:500; }
.hero p { margin:0 0 10px; color:#e6f4f4; font-size:.96rem; line-height:1.55; max-width:760px; }
.tags span { display:inline-block; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.28);
        padding:3px 11px; border-radius:14px; font-size:.78rem; margin:0 6px 4px 0; }

.steps { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:4px 0 14px; }
.step { background:#fff; border:1px solid #d5e3e8; border-top:4px solid #0a6c74; border-radius:6px; padding:11px 13px; }
.step b { color:#0b2e3f; font-size:.92rem; } .step i { font-style:normal; color:#0a6c74; font-weight:700; margin-right:6px; }
.step div { color:#4c6470; font-size:.82rem; margin-top:3px; line-height:1.4; }

.card { background:#fff; border:1px solid #d5e3e8; border-radius:6px; padding:14px 16px; margin-bottom:12px; }
.card.muted { color:#5a7480; font-size:.9rem; }
.card h5 { margin:0 0 6px; color:#0b2e3f; font-size:1rem; }
.alert { background:#fff5f5; border:2px solid #e03131; color:#9c1c1c; padding:14px 18px; border-radius:6px; font-weight:500; margin-bottom:12px; }
.pill { display:inline-block; padding:2px 11px; border-radius:12px; font-size:.8rem; font-weight:600; }
.u-urgent { background:#ffe8cc; color:#c2410c; } .u-routine { background:#d3f9d8; color:#237a3b; }
.u-self_care { background:#e7f5ff; color:#1864ab; } .u-emergency { background:#ffe3e3; color:#c92a2a; }

.stTabs [data-baseweb="tab"] { font-weight:600; padding:10px 16px; }
.stTabs [aria-selected="true"] { color:#0a6c74; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #d5e3e8; }
.side-title { font-weight:700; font-size:1.05rem; color:#0b2e3f; margin-bottom:6px; }
.status { padding:7px 11px; border-radius:6px; font-size:.84rem; font-weight:500; margin:6px 0; }
.status.ok { background:#e6f7ee; color:#1f7a45; } .status.off { background:#fff4e0; color:#a15c00; }
.note { background:#fff9db; border-left:5px solid #f59f00; padding:8px 12px; font-size:.82rem; border-radius:4px; margin:8px 0; }
.tp-chip { background:#0b2e3f; color:#fff; padding:6px 12px; border-radius:4px; font-weight:600; font-size:.8rem; margin:4px 0 8px; }
.tp-step { border-left:4px solid #0a6c74; padding:4px 0 4px 10px; margin:8px 0; font-size:.84rem; }
.tp-step.error { border-color:#c92a2a; } .tp-step.alert { border-color:#e8590c; }
.tp-step.fallback, .tp-step.skipped { border-color:#adb5bd; }
.tp-step small { color:#5a7480; }
@media (max-width: 800px) { .steps { grid-template-columns:1fr 1fr; } .hero { flex-direction:column; align-items:flex-start; } }
</style>
"""


def hero() -> str:
    return """
<div class="hero"><div class="hero-badge"></div><div>
<h1>CareCompass AI</h1>
<div class="sub">Multi-agent care navigation and outreach for hospitals</div>
<p>Patients describe how they feel in English, Urdu or Roman Urdu. CareCompass checks for emergencies first,
suggests the right department and books a visit. Hospital staff get follow-up reminders and preventive-care
invitations drafted for them, and a person approves every message before it goes out.</p>
<div class="tags"><span>5 cooperating agents</span><span>English · اردو · Roman Urdu</span>
<span>Emergency check before any AI</span><span>Staff approve every message</span></div>
</div></div>"""


def steps() -> str:
    items = [("1", "Describe", "Say what you feel, who it is for and for how long."),
             ("2", "Safety and triage", "Emergency check first, then urgency and department."),
             ("3", "Book a visit", "Pick a time, confirm your details and give consent."),
             ("4", "Stay in care", "Staff approve reminders and prevention invitations.")]
    cards = "".join(f"<div class='step'><b><i>{n}</i>{t}</b><div>{d}</div></div>" for n, t, d in items)
    return f"<div class='steps'>{cards}</div>"
