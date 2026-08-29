"""
Runs at the start of every scheduled pipeline run, BEFORE upload_tiktok.py.

TikTok access tokens expire every 24h, but refresh tokens last 365 days and
get rotated (a new one is issued) on every refresh. This script:

  1. Uses the stored refresh token to get a brand new access token.
  2. Writes that access token into $GITHUB_ENV so upload_tiktok.py (running
     later in the same job) can read it as a normal environment variable —
     no need to store the access token itself as a secret.
  3. Overwrites the TIKTOK_REFRESH_TOKEN repo secret with the NEW refresh
     token TikTok just issued, using the GitHub API, so next run has a
     valid one. This requires a GitHub Personal Access Token (classic or
     fine-grained, with "Secrets: write" / repo access) stored as GH_PAT.

Required secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET,
TIKTOK_REFRESH_TOKEN, GH_PAT.
"""

import os
import base64
import requests
from nacl import encoding, public

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["TIKTOK_REFRESH_TOKEN"]
GH_PAT = os.environ["GH_PAT"]
REPO = os.environ["GITHUB_REPOSITORY"]  # auto-provided by GitHub Actions, e.g. "user/repo"


def refresh_access_token() -> dict:
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }
    resp = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def write_to_github_env(name: str, value: str):
    env_file = os.environ["GITHUB_ENV"]
    with open(env_file, "a") as f:
        f.write(f"{name}={value}\n")


def update_github_secret(secret_name: str, secret_value: str):
    headers = {
        "Authorization": f"Bearer {GH_PAT}",
        "Accept": "application/vnd.github+json",
    }

    # 1. Get the repo's public key used to encrypt secrets.
    key_resp = requests.get(
        f"https://api.github.com/repos/{REPO}/actions/secrets/public-key",
        headers=headers,
        timeout=30,
    )
    key_resp.raise_for_status()
    key_data = key_resp.json()

    public_key = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")

    # 2. Push the encrypted value.
    put_resp = requests.put(
        f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}",
        headers=headers,
        json={"encrypted_value": encrypted_b64, "key_id": key_data["key_id"]},
        timeout=30,
    )
    put_resp.raise_for_status()


def main():
    tokens = refresh_access_token()

    new_access_token = tokens["access_token"]
    new_refresh_token = tokens["refresh_token"]

    write_to_github_env("TIKTOK_ACCESS_TOKEN", new_access_token)
    update_github_secret("TIKTOK_REFRESH_TOKEN", new_refresh_token)

    print("Refreshed access token for this run and rotated the stored refresh token.")


if __name__ == "__main__":
    main()
