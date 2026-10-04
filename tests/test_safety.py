import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.safety import is_emergency  # noqa: E402


def test_emergency_detected():
    assert is_emergency("I have severe CHEST PAIN since morning")
    assert is_emergency("mujhe seene mein dard hai")


def test_routine_not_flagged():
    assert not is_emergency("I need a checkup for a skin rash")
