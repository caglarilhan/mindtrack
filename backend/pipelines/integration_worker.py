"""Integration worker: poll queued integration events and trigger automations.
Usage:
  python backend/pipelines/integration_worker.py --clinic demo-clinic
"""

import argparse
import json
import os
import sys
from typing import Optional

try:
  import requests  # type: ignore
except ImportError as exc:  # pragma: no cover
  raise SystemExit("requests modülü gerekli: pip install requests") from exc

DEFAULT_URL = os.environ.get(
  "INTEGRATION_PROCESS_URL",
  "http://localhost:3000/api/integrations/events/process",
)


def run_worker(url: str, clinic: Optional[str], limit: int) -> None:
  payload = {"limit": limit}
  if clinic:
    payload["clinicId"] = clinic
  response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=30)
  if response.status_code >= 400:
    print("Process failed", response.status_code, response.text)
    sys.exit(1)
  print("Integration worker result:", response.json())


def main() -> None:
  parser = argparse.ArgumentParser(description="Integration automation worker")
  parser.add_argument("--clinic", help="Clinic ID", default=os.environ.get("WORKER_CLINIC_ID"))
  parser.add_argument("--limit", type=int, default=10, help="Kaç event işlenecek")
  parser.add_argument("--url", default=DEFAULT_URL, help="Process API URL")
  args = parser.parse_args()

  if not args.url:
    raise SystemExit("Process API URL belirtilmeli")

  run_worker(args.url, args.clinic, args.limit)


if __name__ == "__main__":
  main()
