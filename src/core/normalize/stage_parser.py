"""Stage cell parsing primitives."""

from __future__ import annotations

import re


SPLIT_PATTERN = re.compile(r"[;\n]+")


def parse_stages(text: str) -> list[str]:
    """Split raw stage cell text into stage lines.

    M1 skeleton output is still textual lines.
    Structured conversion to `StageNormalized` is handled by normalization interface.
    """
    chunks = [part.strip() for part in SPLIT_PATTERN.split(text or "") if part.strip()]
    return chunks

