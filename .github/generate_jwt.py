"""
Generates a JWT for GitHub Automation

Requirements:
    pip install .[cicd]
"""

import os
import sys
import time

import jwt
import requests

app_id = os.getenv("DASHABOT_APPID", None)
installation_id = os.getenv("DASHABOT_IID", None)

if not app_id:
    raise ValueError("DASHABOT_APPID has not been set")
if not installation_id:
    raise ValueError("DASHABOT_IID has not been set")

private_key = sys.stdin.read().strip()

now = int(time.time())
payload = {"iat": now - 60, "exp": now + (3 * 60), "iss": app_id}
ENCODED_JWT = jwt.encode(payload, private_key, algorithm="RS256")

headers = {
    "Authorization": f"Bearer {ENCODED_JWT}",
    "Accept": "application/vnd.github+json",
}

try:
    resp = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
        timeout=10.0,
    )
except (requests.Timeout, requests.ConnectionError) as err:
    raise requests.RequestException(
        f"Unable to get access token. Job failed. Error: {err}"
    )

resp.raise_for_status()
token = resp.json()["token"]
print(f"::add-mask::{token}")
with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as env_file:
    env_file.write(f"GH_TOKEN={token}\n")
    env_file.write(f"GITHUB_TOKEN={token}\n")
