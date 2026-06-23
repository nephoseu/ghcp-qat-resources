import random
from uuid import uuid4

from faker import Faker

VALID_SEVERITIES = ("critical", "high", "medium", "low")
_fake = Faker()


def make_ticket(**overrides):
    marker = overrides.pop("marker", uuid4().hex[:8])
    payload = {
        "title": f"[lab3-{marker}] {_fake.sentence(nb_words=6).rstrip('.')}",
        "description": _fake.paragraph(nb_sentences=2),
        "severity": random.choice(VALID_SEVERITIES),
    }
    payload.update(overrides)
    return payload
