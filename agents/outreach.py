"""Outreach agent: finds people eligible for a prevention program and drafts invitations."""
from utils import data, drafting

TEMPLATES = {
    "English": "Dear {name}, it is time for your {program} visit at our hospital. Reply YES and we will book a slot.",
    "Urdu (اردو)": "محترم {name}، {ur} جواب میں YES لکھیں، ہم وقت طے کر دیں گے۔",
    "Roman Urdu": "Mohtaram {name}, aap ka {program} ka waqt ho gaya hai. YES likhein, hum time book kar denge.",
}


def cohort(program: str) -> list[dict]:
    tag = data.load()["programs"][program]["tag"]
    return [p for p in data.load()["patients"] if tag in p["tags"]]


def draft(program: str, p: dict, lang: str):
    ur = data.load()["programs"][program]["ur"]
    base = TEMPLATES[lang].format(name="{name}", program=program.lower(), ur=ur)
    return drafting.rewrite(base, lang, p["name"])
