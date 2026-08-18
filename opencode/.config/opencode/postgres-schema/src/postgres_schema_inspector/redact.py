from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

PASSWORD_PARAM_RE = re.compile(r"(?i)(password=)[^\s&]+")


def redact_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return PASSWORD_PARAM_RE.sub(r"\1<redacted>", value)

    if not parsed.scheme or not parsed.netloc:
        return PASSWORD_PARAM_RE.sub(r"\1<redacted>", value)

    host = parsed.hostname or ""
    netloc = host
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    if parsed.username:
        netloc = f"{parsed.username}:<redacted>@{netloc}"
    query = PASSWORD_PARAM_RE.sub(r"\1<redacted>", parsed.query)
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, parsed.fragment))


def redact_text(value: object) -> str:
    text = str(value)
    text = re.sub(
        r"postgres(?:ql)?://[^\s'\"]+",
        lambda match: redact_url(match.group(0)),
        text,
    )
    return PASSWORD_PARAM_RE.sub(r"\1<redacted>", text)
