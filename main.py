import json, os, urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

def call_llm(messages, system=""):
    body = {
        "model": "claude-sonnet-5",
        "max_tokens": 4096,
        "system": system,
        "messages": messages,
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as error:
        return json.loads(error.read())

llm = call_llm([{"role": "user", "content": "What does HTTP 418 mean?"},
                {"role": "assistant", "content": "It means the server is a teapot. ..."},
                {"role": "user", "content": "Is it ever used seriously?"}])
print(json.dumps(llm, sort_keys=True, indent=4))
