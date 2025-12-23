"""Caregiver token yönetim CLI'si.
Kullanım örnekleri:
  python3 backend/pipelines/caregiver_token_tool.py list
  python3 backend/pipelines/caregiver_token_tool.py create --label "Berlin Municipality" --regions us eu --expires 2025-12-31T23:59:00Z
  python3 backend/pipelines/caregiver_token_tool.py deactivate --token-id <uuid>
"""

import argparse
import hashlib
import os
import secrets
from datetime import datetime
from typing import List

try:
  from supabase import create_client, Client  # type: ignore
except ImportError:  # pragma: no cover
  raise SystemExit("supabase-py kurulmalı: pip install supabase")


def get_client() -> Client:
  url = os.environ.get("SUPABASE_URL")
  key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
  if not url or not key:
    raise SystemExit("SUPABASE_URL ve SUPABASE_SERVICE_ROLE_KEY gerekir")
  return create_client(url, key)


def hash_token(token: str) -> str:
  return hashlib.sha256(token.encode("utf-8")).hexdigest()


def list_tokens(client: Client):
  data = client.table("caregiver_tokens").select(
    "id,label,allowed_regions,active,expires_at,last_used_at,created_at"
  ).execute()
  rows = data.data or []
  for row in rows:
    print(f"{row['id']} | {row['label']} | regions={row['allowed_regions']} | active={row['active']} | expires={row['expires_at']}")


def create_token(client: Client, label: str, regions: List[str], expires: str | None):
  token = secrets.token_urlsafe(32)
  hashed = hash_token(token)
  allowed = [r for r in regions if r in {"us", "eu"}] or ["us", "eu"]
  payload = {
    "label": label,
    "token_hash": hashed,
    "allowed_regions": allowed,
    "expires_at": expires,
  }
  client.table("caregiver_tokens").insert(payload).execute()
  print("Yeni token oluşturuldu. Yalnızca bu çıktıdan kopyalayın:\n")
  print(token)


def deactivate_token(client: Client, token_id: str):
  client.table("caregiver_tokens").update({"active": False}).eq("id", token_id).execute()
  print(f"{token_id} pasifleştirildi")


def build_parser():
  parser = argparse.ArgumentParser(description="Caregiver token CLI")
  sub = parser.add_subparsers(dest="command", required=True)

  sub.add_parser("list", help="Tokenları listele")

  create_cmd = sub.add_parser("create", help="Yeni token oluştur")
  create_cmd.add_argument("--label", required=True)
  create_cmd.add_argument("--regions", nargs="*", default=["us", "eu"])
  create_cmd.add_argument("--expires", help="ISO8601 formatında tarih", default=None)

  deactivate_cmd = sub.add_parser("deactivate", help="Token pasifleştir")
  deactivate_cmd.add_argument("--token-id", required=True)

  return parser


def main():
  parser = build_parser()
  args = parser.parse_args()
  client = get_client()

  if args.command == "list":
    list_tokens(client)
  elif args.command == "create":
    expires = args.expires
    if expires:
      try:
        datetime.fromisoformat(expires.replace("Z", "+00:00"))
      except ValueError:
        raise SystemExit("--expires ISO8601 formatında olmalı")
    create_token(client, args.label, args.regions, expires)
  elif args.command == "deactivate":
    deactivate_token(client, args.token_id)


-if __name__ == "__main__":
-  main()
+if __name__ == "__main__":
+  main()
