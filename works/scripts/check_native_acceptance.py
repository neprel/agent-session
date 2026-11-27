"""Report incomplete native release gates without substituting passing versions."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.support.acceptance import CLIENTS, acceptance_nodes  # noqa: E402


def main():
    missing = []
    for client in CLIENTS:
        try:
            acceptance_nodes(client)
        except ValueError as exc:
            missing.append(str(exc))
    print(json.dumps({"complete": not missing, "requirements": missing}))
    return 4 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
