"""
Generates a JWT for Github Automation

This code is not my finest hour.
"""

import os
import sys
import time

import jwt
import requests

app_id = os.environ['DASHABOT_APPID']
installation_id = os.environ['DASHABOT_IID']

private_key = sys.stdin.read().strip()

if not app_id:
    raise ValueError("DASHABOT_APPID has not been set")
if not installation_id:
    raise ValueError("DASHABOT_IID has not been set")

now = int(time.time())
payload = {
    'iat': now - 60,
    'exp': now + (3 * 60),
    'iss': app_id
}
encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')

headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github+json"
}

resp = requests.post(
    f"https://api.github.com/app/installations/{installation_id}/access_tokens",
    headers=headers
)
resp.raise_for_status()
token = resp.json()["token"]
print(f"::add-mask::{token}")
with open(os.environ["GITHUB_ENV"], "a") as env_file:
    env_file.write(f"GH_TOKEN={token}\n")
    env_file.write(f"GITHUB_TOKEN={token}\n")
