import json, os, urllib.request
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-5"
SYSTEM = "You are a concise assistant."


def call_llm(messages):
    body = {"model": MODEL, "max_tokens": 4096, "system": SYSTEM, "messages": messages, "tools": TOOLS}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 "x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


TOOLS = [  # NEW: the menu
    {"name": "read_file",
     "description": "Read a text file and return its contents.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "run_command",
     "description": "Run a shell command and return stdout+stderr.",
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
]


def execute_tool(name, args):  # NEW: the dispatch
    """Map the model's JSON request to a real function call."""
    try:
        if name == "read_file":
            return open(args["path"]).read()
        if name == "run_command":
            out = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=60)
            return out.stdout + out.stderr
        return f"ERROR: unknown tool {name}"
    except Exception as e:
        return f"ERROR: {e}"  # errors go BACK to the model


def main():
    messages = []  # the entire "session"
    while True:
        user_text = input("\nyou> ").strip()
        if user_text in ("/quit", ""):
            break
        if user_text == "/clear":
            messages = []  # "new conversation"
            continue
        messages.append({"role": "user", "content": user_text})
        reply = call_llm(messages)  # resend EVERYTHING
        print(f"this is the raw reply from the model: {reply}\n")
        for b in reply["content"]:
            if b["type"] == "tool_use":
                print(f"tool_use full content: {b}")

            elif b["type"] == "text":
                text = "".join(b["text"] for b in reply["content"] if b["type"] == "text")
                messages.append({"role": "assistant", "content": reply["content"]})
                print(f"\nassistant> {text}")


if __name__ == "__main__":
    main()
