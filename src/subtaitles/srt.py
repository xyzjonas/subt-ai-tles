from __future__ import annotations

import re

_markup_pattern = re.compile(r"<.*?>")
_whole_line_pattern = re.compile(r"^(<\w+>)(.*)(</\w+>)$", re.DOTALL)


def strip_srt_markup(text: str) -> str:
    return re.sub(_markup_pattern, "", text)


def reapply_whole_line_markup(raw: str, translation: str) -> str:
    match = _whole_line_pattern.match(raw.strip())
    if match:
        return f"{match.group(1)}{translation}{match.group(3)}"
    return translation
