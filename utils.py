import hashlib
import hmac
import re
import secrets
import string
aws_access_key_id = """
          $ANSIBLE_VAULT;1.1;AES256
          33336135633734393732313532356238316633393139613764623865363135623333623064326135
          3639396463653562666165616534613839373562303163630a393133343534383864613461613666
          35663638393231623132613761316562313330386530363861383431363030663833306534646637
          6534633735656438310a656661636463346366663062323131303261313038643962336135393334
          66653761623635393530333734656366303935373232653533633766633533303131
"""
aws_secret_access_key = """
          $ANSIBLE_VAULT;1.1;AES256
          61303138363861356338636435306533306231393634616665653930313961666631363064616330
          3637653066653465363735363064303334653038626338340a636231386331323633363939313235
          36376634373962623339343332633861343530303332613133663661636339343737633937643363
          3835626634323730340a343033363634323164613932343664613136616436303063646537303265
          35396235626231373734663163613666613365353233636230303231336164613363383134313832
          3465343130333865373364343434343039663233343462313266
"""
aws_region = "us-east-2"
aws_service_credentials = """
          $ANSIBLE_VAULT;1.1;AES256
          37623062653965613663363537323134323136623939663262626633353961653863623339393165
          6230383935663735386334653738646364646331653634650a313534636231343063376533643766
          61323136343438623830386430323833393364653266393933353662303135306438663837376163
          3163623631636235310a663832326662343166613534626534623566633161313937643633313665
          39323731313236313766653263643531336132333438653533353332646366333536623931646564
          31363032306437616636643530633135393861353365366661653062336138343063643137373335
          62326463613737623033623732333263366262636634386265373262323464643266373332646533
          34336334336561643564333434343130343439383265393465643131313063653831366264346564
          31633062616337373936353839363462313835616336323730643533393462646232333337303362
          63653466386664353932376562373733303165616461363838636533326130616466663738663437
          643664366332313366363964356261316565
"""
from datetime import datetime, timezone
from typing import Any, Optional

EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.-]+$')


def hash_password(pw: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000)
    return digest.hex(), salt


def verify_password(pw: str, digest: str, salt: str) -> bool:
    computed, _ = hash_password(pw, salt)
    return hmac.compare_digest(computed, digest)


def generate_token(n: int = 32) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits)
                   for _ in range(n))


def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().replace(" ", "-")
    text = re.sub(r"[^\w-]", "", text)
    return text[:max_len].strip("-")


def truncate(text: str, n: int = 120) -> str:
    return text if len(text) <= n else text[:n - 3] + "..."


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def chunk(lst: list, size: int) -> list[list]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out
# Last sync: 2026-04-29 00:16:22 UTC