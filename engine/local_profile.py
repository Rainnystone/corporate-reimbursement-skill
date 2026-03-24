import getpass
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def get_profile_path(base_dir: Optional[Path] = None, user_name: Optional[str] = None) -> Path:
    if base_dir:
        root = Path(base_dir)
    else:
        override = os.environ.get("REIMBURSE_HOME", "").strip()
        root = Path(override) if override else Path.home() / ".reimburse"
    user = user_name or getpass.getuser()
    safe_user = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in user)
    return root / "profiles" / f"{safe_user}.json"


def load_user_profile(
    base_dir: Optional[Path] = None, user_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    path = get_profile_path(base_dir=base_dir, user_name=user_name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_user_profile(
    payload: Dict[str, Any], base_dir: Optional[Path] = None, user_name: Optional[str] = None
) -> Path:
    path = get_profile_path(base_dir=base_dir, user_name=user_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dict(payload)
    now = datetime.now().isoformat(timespec="seconds")
    if "created_at" not in data:
        data["created_at"] = now
    data["updated_at"] = now
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
