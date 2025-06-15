"""
Generates a JWT for Github Automation

This code is not my finest hour.
"""

import os
import jwt
import time
import requests

app_id = os.environ['DASHABOT_APPID']
installation_id = os.environ['DASHABOT_IID']

with open("private-key.pem", "r") as f:
    private_key = f.read()

now = int(time.time())
payload = {
    'iat': now - 60,
    'exp': now + (10 * 60),
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
