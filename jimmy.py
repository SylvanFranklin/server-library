"""chatjimmy - CLI for chatjimmy.ai"""

import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.request

API_URL = "https://chatjimmy.ai/api/chat"

MODELS = [
    "llama3.1-8B",
    "llama3.1-70B",
    "llama3.2-3B",
    "mixtral-8x7B",
]

DEFAULT_MODEL = MODELS[1]
DEFAULT_TOP_K = 8

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Origin": "https://chatjimmy.ai",
    "Referer": "https://chatjimmy.ai/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

STATS_RE = re.compile(r"<\|stats\|>.*?<\|/stats\|>", re.DOTALL)


# --- API ---


def post(messages, model, system_prompt, top_k):
    payload = json.dumps(
        {
            "messages": messages,
            "chatOptions": {
                "selectedModel": model,
                "systemPrompt": system_prompt,
                "topK": top_k,
            },
            "attachment": None,
        }
    ).encode()

    req = urllib.request.Request(API_URL, data=payload, headers=HEADERS, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if resp.getheader("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode()
    except urllib.error.HTTPError as e:
        body = e.read()
        if e.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
        print(f"[http {e.code}] {body.decode()}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"[network error] {e.reason}", file=sys.stderr)

    return None


def parse(raw):
    """Extract clean text from a streamed response."""
    parts = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("0:"):
            try:
                parts.append(json.loads(line[2:]))
            except json.JSONDecodeError:
                pass

    text = "".join(parts) if parts else raw
    return STATS_RE.sub("", text).strip()


# --- Commands ---

HELP = """\
commands:
  /model            list models
  /model <name>     switch model
  /system           show system prompt
  /system <text>    set system prompt
  /clear            clear conversation history
  /help             show this help
  /quit             exit\
"""


def handle_command(line, state):
    cmd, _, arg = line[1:].partition(" ")
    cmd = cmd.lower()
    arg = arg.strip()

    if cmd in ("quit", "exit", "q"):
        print("bye")
        sys.exit(0)

    elif cmd in ("clear", "reset"):
        state["messages"].clear()
        print("[history cleared]")

    elif cmd == "model":
        if arg:
            if arg not in MODELS:
                print(f"[unknown model '{arg}'. available: {', '.join(MODELS)}]")
            else:
                state["model"] = arg
                print(f"[model: {arg}]")
        else:
            for m in MODELS:
                marker = " *" if m == state["model"] else ""
                print(f"  {m}{marker}")

    elif cmd == "system":
        if arg:
            state["system"] = arg
            print("[system prompt updated]")
        else:
            print(f"[system: {state['system'] or '(none)'}]")

    elif cmd == "help":
        print(HELP)

    else:
        print(f"[unknown command /{cmd} - try /help]")


# --- Modes ---


def interactive(model, system_prompt, top_k):
    state = {
        "model": model,
        "system": system_prompt,
        "messages": [],
    }

    print(f"chatjimmy  |  model: {state['model']}  |  /help for commands")
    print()

    while True:
        try:
            line = input("you: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)

        if not line:
            continue

        if line.startswith("/"):
            handle_command(line, state)
            continue

        state["messages"].append({"role": "user", "content": line})

        raw = post(state["messages"], state["model"], state["system"], top_k)
        if raw is None:
            state["messages"].pop()
            continue

        reply = parse(raw)
        print(f"jimmy: {reply}\n")
        state["messages"].append({"role": "assistant", "content": reply})


def oneshot(message, model, system_prompt, top_k, raw_output):
    raw = post([{"role": "user", "content": message}], model, system_prompt, top_k)
    if raw is None:
        sys.exit(1)
    print(raw if raw_output else parse(raw))


# --- Entry point ---


def main():
    parser = argparse.ArgumentParser(
        prog="chatjimmy",
        description="CLI for chatjimmy.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  chatjimmy.py\n"
            "  chatjimmy.py -m 'hello'\n"
            "  chatjimmy.py --model llama3.1-70B\n"
            "  chatjimmy.py -s 'reply only in haiku'\n"
        ),
    )
    parser.add_argument("-m", "--message", help="send a single message and exit")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODELS,
        help=f"model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "-s", "--system", default="", metavar="PROMPT", help="system prompt"
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        metavar="N",
        help=f"top-k value (default: {DEFAULT_TOP_K})",
    )
    parser.add_argument("--raw", action="store_true", help="print raw API response")

    args = parser.parse_args()

    if args.message:
        oneshot(args.message, args.model, args.system, args.top_k, args.raw)
    else:
        interactive(args.model, args.system, args.top_k)


if __name__ == "__main__":
    main()
