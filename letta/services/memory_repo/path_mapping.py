"""Helpers for mapping memory-repo markdown paths to block labels.

Special handling for skills:
- sync `skills/{skill_name}/SKILL.md` as block label `skills/{skill_name}`
- ignore all other markdown files under `skills/`

Optional opt-in filter:
- If the env var `LETTA_MEMFS_BLOCK_PATH_PREFIXES` is set (comma-separated
  list of path prefixes, e.g. `system/` or `system/,users/`), only paths
  starting with one of those prefixes are mapped to a block label.
  `skills/**/SKILL.md` is always allowed through so existing skill
  behavior is preserved regardless of the filter.
- Default (unset / empty): upstream behavior — every `.md` path outside
  `skills/` maps to a block label.
"""

from __future__ import annotations

import os


def _configured_prefixes() -> tuple[str, ...]:
    raw = os.environ.get("LETTA_MEMFS_BLOCK_PATH_PREFIXES", "").strip()
    if not raw:
        return ()
    return tuple(p.strip() for p in raw.split(",") if p.strip())


def memory_block_label_from_markdown_path(path: str) -> str | None:
    """Return block label for a syncable markdown path, else None.

    Rules:
    - Non-`.md` files are ignored.
    - `skills/{skill_name}/SKILL.md` -> `skills/{skill_name}`
    - Other `skills/**` markdown files are ignored.
    - All other markdown files map to `path[:-3]`.
    - If `LETTA_MEMFS_BLOCK_PATH_PREFIXES` is set, non-skill paths must
      start with one of those prefixes to produce a label.
    """
    if not path.endswith(".md"):
        return None

    if path.startswith("skills/"):
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "skills" and parts[1] and parts[2] == "SKILL.md":
            return f"skills/{parts[1]}"
        return None

    prefixes = _configured_prefixes()
    if prefixes and not path.startswith(prefixes):
        return None

    return path[:-3]
