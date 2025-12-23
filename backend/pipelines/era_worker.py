"""ERA CSV ingest script.
Usage:
  python backend/pipelines/era_worker.py --csv data/era_sample.csv --url https://app.mindtrack.dev/api/billing/era/ingest

CSV Columns:
  claim_number,status,code,description,amount,region
"""

import argparse
import csv
import json
import os
import sys
from typing import List, Dict

try:
  import requests  # type: ignore
except ImportError as exc:  # pragma: no cover
  raise SystemExit("requests kitabı gerekli: pip install requests") from exc


def load_events(csv_path: str) -> List[Dict[str, str]]:
  events: List[Dict[str, str]] = []
  with open(csv_path, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not row.get("claim_number"):
        continue
      events.append({
        "claimNumber": row.get("claim_number"),
        "status": (row.get("status") or "").lower() or None,
        "code": row.get("code") or "ERA",
        "description": row.get("description") or "",
        "amount": float(row.get("amount") or 0),
        "region": (row.get("region") or "us").lower(),
      })
  return events


def main():
  parser = argparse.ArgumentParser(description="ERA ingest worker")
  parser.add_argument("--csv", required=True, help="ERA CSV dosyası")
  parser.add_argument("--url", default=os.environ.get("ERA_INGEST_URL", "http://localhost:3000/api/billing/era/ingest"))
  parser.add_argument("--secret", default=os.environ.get("ERA_WEBHOOK_SECRET"), help="x-era-secret header değeri")
  args = parser.parse_args()

  if not args.secret:
    raise SystemExit("ERA_WEBHOOK_SECRET tanımlı olmalı veya --secret ile geçilmeli")

  events = load_events(args.csv)
  if not events:
    raise SystemExit("CSV'den geçerli event okunamadı")

  payload = {"events": events}
  response = requests.post(
    args.url,
    headers={"Content-Type": "application/json", "x-era-secret": args.secret},
    data=json.dumps(payload),
    timeout=30,
  )
  if response.status_code >= 400:
    print("Ingest başarısız", response.status_code, response.text)
    sys.exit(1)
  print("ERA ingest sonucu:", response.json())


if __name__ == "__main__":
  main()
