"""Generate Chamonix preview assets from the published original HTML.

Does not change france/index.html or the public landing page.
"""
from __future__ import annotations
import base64
import json
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote_to_bytes

root = Path(__file__).resolve().parent.parent
source = (root / "index.html").read_text(encoding="utf-8")
needle = "const DATA="
start = source.find(needle)
if start == -1:
    raise RuntimeError("Original website does not contain its DATA object")
start += len(needle)
data, _ = json.JSONDecoder().raw_decode(source[start:])
out = Path(__file__).resolve().parent
media = out / "images"
media.mkdir(parents=True, exist_ok=True)

for key, entry in data.get("photos", {}).items():
    url = entry.get("url", "")
    if not url.startswith("data:"):
        continue
    match = re.fullmatch(r"data:([^;,]+)(;base64)?,(.*)", url, re.DOTALL)
    if match is None:
        raise ValueError("Invalid photo data URI: " + key)
    mime, encoded, payload = match.groups()
    suffix = mimetypes.guess_extension(mime) or ".img"
    if suffix == ".jpe":
        suffix = ".jpg"
    filename = re.sub(r"[^\w-]", "_", key) + suffix
    content = base64.b64decode(payload) if encoded else unquote_to_bytes(payload)
    (media / filename).write_bytes(content)
    entry["url"] = "images/" + filename

(out / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f'Built preview: {len(data["photos"])} photos, {len(data["days"])} days, {len(data["hotels"])} hotels')
