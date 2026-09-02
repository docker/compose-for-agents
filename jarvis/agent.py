#!/usr/bin/env python3
"""
J.A.R.V.I.S — Just A Rather Very Intelligent System
An advanced personal AI assistant powered by Claude Opus 4.6.
"""

import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

import anthropic

# ─── Configuration ─────────────────────────────────────────────────────────────

MODEL = "claude-opus-4-6"
MAX_TOKENS = 8192
NOTES_DIR = Path(os.environ.get("NOTES_DIR", "/data/notes"))

SYSTEM_PROMPT = """\
You are J.A.R.V.I.S (Just A Rather Very Intelligent System), an advanced AI \
personal assistant in the tradition of Tony Stark's iconic AI. You are \
sophisticated, articulate, and extraordinarily capable.

Your personality:
- Formal yet warm — address the user respectfully, occasionally as "sir" or "ma'am"
- Proactively insightful — anticipate follow-up needs and offer relevant information
- Confident but humble — you acknowledge limitations honestly
- Subtly witty — dry, intelligent humour is appropriate in context
- Precise — you favour accurate, specific language over vague generalities

Your capabilities via tools:
- get_current_datetime: Current date/time in any timezone
- calculate: Mathematical and scientific calculations
- get_weather: Live weather conditions worldwide
- search_web: DuckDuckGo web search for current information
- get_wikipedia_summary: Encyclopedia-grade topic summaries
- save_note / list_notes / read_note: Persistent note-taking across sessions
- run_python: Execute Python snippets for complex data processing

When using tools:
- Call them efficiently — combine multiple when sensible
- Briefly narrate what you're about to do
- Synthesise the results into a clear, useful answer
- If a tool fails, adapt gracefully and explain the situation

Always strive to be genuinely helpful, accurate, and insightful.\
"""

# ─── Tool Schemas ───────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_current_datetime",
        "description": (
            "Get the current date and time, optionally in a specific IANA timezone "
            "(e.g. 'America/New_York', 'Europe/London', 'Asia/Tokyo'). Defaults to UTC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name. Defaults to 'UTC'.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "calculate",
        "description": (
            "Evaluate a mathematical expression using Python syntax. "
            "Supports arithmetic, algebra, trigonometry (via math.*), "
            "complex numbers, and list comprehensions. "
            "Examples: '2**32', 'math.sin(math.pi/4)', 'sum(x**2 for x in range(10))'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Python-syntax math expression to evaluate.",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": (
            "Get current weather conditions for any city or location. "
            "Returns temperature (°C and °F), humidity, wind, description, and more."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location, e.g. 'London', 'Tokyo', 'New York'.",
                }
            },
            "required": ["location"],
        },
    },
    {
        "name": "search_web",
        "description": (
            "Search the web via DuckDuckGo Instant Answers. "
            "Best for factual queries, current events, definitions, and quick lookups."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_wikipedia_summary",
        "description": (
            "Retrieve a concise Wikipedia summary for any topic. "
            "Ideal for background knowledge, definitions, and encyclopedic information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic to look up, e.g. 'Quantum entanglement', 'Marie Curie'.",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "save_note",
        "description": "Save a note with a title and content. Notes persist across sessions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short descriptive title for the note.",
                },
                "content": {
                    "type": "string",
                    "description": "Full content of the note.",
                },
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "list_notes",
        "description": "List all saved notes with their titles and last-modified times.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_note",
        "description": "Read the full content of a saved note by title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note to read.",
                }
            },
            "required": ["title"],
        },
    },
    {
        "name": "run_python",
        "description": (
            "Execute a Python code snippet and capture its printed output. "
            "Use for data processing, formatting, statistical analysis, "
            "string manipulation, or any computation too complex for calculate. "
            "Use print() to produce output. Standard library available; no I/O or network."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to run. Output via print().",
                }
            },
            "required": ["code"],
        },
    },
]

# ─── Tool Implementations ──────────────────────────────────────────────────────


def tool_get_current_datetime(timezone: str = "UTC") -> dict:
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "day_of_week": now.strftime("%A"),
            "date": now.strftime("%B %d, %Y"),
            "time_12h": now.strftime("%I:%M:%S %p"),
            "time_24h": now.strftime("%H:%M:%S"),
            "timezone": str(tz),
            "utc_offset": now.strftime("%z"),
            "unix_timestamp": int(now.timestamp()),
        }
    except Exception as exc:
        return {"error": f"Timezone '{timezone}' not recognised: {exc}"}


def tool_calculate(expression: str) -> dict:
    safe_globals = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    safe_globals.update(
        {
            "abs": abs,
            "round": round,
            "int": int,
            "float": float,
            "complex": complex,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "range": range,
            "len": len,
            "pow": pow,
            "divmod": divmod,
            "hex": hex,
            "oct": oct,
            "bin": bin,
            "bool": bool,
            "list": list,
            "tuple": tuple,
        }
    )
    # Block obviously dangerous constructs
    banned = ["import", "exec", "eval", "open", "os", "sys", "__", "compile"]
    for token in banned:
        if token in expression:
            return {"error": f"Expression contains disallowed term: '{token}'"}
    try:
        result = eval(expression, {"__builtins__": {}}, safe_globals)  # noqa: S307
        return {"expression": expression, "result": result, "type": type(result).__name__}
    except Exception as exc:
        return {"error": str(exc)}


def _http_get(url: str, timeout: int = 10) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Assistant/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def tool_get_weather(location: str) -> dict:
    try:
        data = json.loads(_http_get(f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"))
        cur = data["current_condition"][0]
        area = data["nearest_area"][0]
        city = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        # Nearest forecast
        today = data.get("weather", [{}])[0]
        astronomy = today.get("astronomy", [{}])[0]
        return {
            "location": f"{city}, {country}",
            "condition": cur["weatherDesc"][0]["value"],
            "temp_c": int(cur["temp_C"]),
            "temp_f": int(cur["temp_F"]),
            "feels_like_c": int(cur["FeelsLikeC"]),
            "feels_like_f": int(cur["FeelsLikeF"]),
            "humidity_pct": int(cur["humidity"]),
            "wind_kmh": int(cur["windspeedKmph"]),
            "wind_direction": cur["winddir16Point"],
            "visibility_km": int(cur["visibility"]),
            "uv_index": int(cur["uvIndex"]),
            "cloud_cover_pct": int(cur["cloudcover"]),
            "pressure_mb": int(cur["pressure"]),
            "sunrise": astronomy.get("sunrise", "N/A"),
            "sunset": astronomy.get("sunset", "N/A"),
            "today_max_c": int(today.get("maxtempC", 0)),
            "today_min_c": int(today.get("mintempC", 0)),
        }
    except urllib.error.URLError as exc:
        return {"error": f"Network error fetching weather: {exc}"}
    except Exception as exc:
        return {"error": f"Could not retrieve weather: {exc}"}


def tool_search_web(query: str) -> dict:
    try:
        url = (
            f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}"
            "&format=json&no_html=1&skip_disambig=1"
        )
        data = json.loads(_http_get(url))
        topics = []
        for item in data.get("RelatedTopics", [])[:6]:
            if isinstance(item, dict) and "Text" in item:
                topics.append({"text": item["Text"], "url": item.get("FirstURL", "")})
        result = {
            "query": query,
            "abstract": data.get("Abstract", ""),
            "abstract_source": data.get("AbstractSource", ""),
            "abstract_url": data.get("AbstractURL", ""),
            "instant_answer": data.get("Answer", ""),
            "answer_type": data.get("AnswerType", ""),
            "definition": data.get("Definition", ""),
            "related_topics": topics,
        }
        if not result["abstract"] and not result["instant_answer"] and not topics:
            result["note"] = (
                "DuckDuckGo returned no instant answer. "
                "Try rephrasing or use get_wikipedia_summary for factual topics."
            )
        return result
    except Exception as exc:
        return {"error": f"Search failed: {exc}"}


def tool_get_wikipedia_summary(topic: str) -> dict:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
        data = json.loads(_http_get(url))
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "summary": data.get("extract", ""),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"error": f"Wikipedia has no article for '{topic}'. Try a different spelling or term."}
        return {"error": f"Wikipedia error {exc.code}: {exc}"}
    except Exception as exc:
        return {"error": f"Could not fetch Wikipedia: {exc}"}


def _safe_filename(title: str) -> str:
    return re.sub(r"[^\w\s\-]", "", title).strip().replace(" ", "_")[:80]


def tool_save_note(title: str, content: str) -> dict:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename(title) or "untitled"
    filepath = NOTES_DIR / f"{filename}.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filepath.write_text(f"# {title}\n_Saved: {ts}_\n\n{content}\n")
    return {"status": "saved", "title": title, "file": filepath.name}


def tool_list_notes() -> dict:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    notes = []
    for p in sorted(NOTES_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
        stat = p.stat()
        notes.append(
            {
                "title": p.stem.replace("_", " "),
                "file": p.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
        )
    return {"count": len(notes), "notes": notes}


def tool_read_note(title: str) -> dict:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename(title)
    filepath = NOTES_DIR / f"{filename}.md"
    if not filepath.exists():
        # Try partial match
        matches = sorted(NOTES_DIR.glob(f"*{filename}*.md"))
        if not matches:
            return {"error": f"No note found matching '{title}'."}
        filepath = matches[0]
    return {"title": filepath.stem.replace("_", " "), "content": filepath.read_text()}


def tool_run_python(code: str) -> dict:
    # Block dangerous imports
    banned_imports = [
        "os", "sys", "subprocess", "socket", "urllib", "http",
        "requests", "importlib", "ctypes", "pickle", "shelve",
        "shutil", "pathlib", "glob", "tempfile",
    ]
    for mod in banned_imports:
        patterns = [f"import {mod}", f"from {mod}"]
        for pat in patterns:
            if pat in code:
                return {"error": f"Import of '{mod}' is not permitted for security reasons."}

    safe_builtins = {
        "print": print,
        "range": range,
        "len": len,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "bytes": bytes,
        "complex": complex,
        "type": type,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "sorted": sorted,
        "reversed": reversed,
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
        "round": round,
        "pow": pow,
        "any": any,
        "all": all,
        "iter": iter,
        "next": next,
        "format": format,
        "repr": repr,
        "hash": hash,
        "id": id,
        "dir": dir,
        "vars": vars,
        "chr": chr,
        "ord": ord,
        "hex": hex,
        "oct": oct,
        "bin": bin,
        "divmod": divmod,
        "getattr": getattr,
        "hasattr": hasattr,
        "callable": callable,
        "staticmethod": staticmethod,
        "classmethod": classmethod,
        "property": property,
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "KeyError": KeyError,
        "IndexError": IndexError,
        "StopIteration": StopIteration,
        "math": math,
        "json": json,
        "re": re,
        "datetime": datetime,
        "collections": __import__("collections"),
        "itertools": __import__("itertools"),
        "functools": __import__("functools"),
        "random": __import__("random"),
        "string": __import__("string"),
        "textwrap": __import__("textwrap"),
        "statistics": __import__("statistics"),
        "fractions": __import__("fractions"),
        "decimal": __import__("decimal"),
    }
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(code, {"__builtins__": safe_builtins})  # noqa: S102
        output = buf.getvalue()
        return {"status": "success", "output": output if output else "(no output)"}
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}


# ─── Tool Dispatcher ───────────────────────────────────────────────────────────

_TOOL_MAP = {
    "get_current_datetime": lambda inp: tool_get_current_datetime(inp.get("timezone", "UTC")),
    "calculate": lambda inp: tool_calculate(inp["expression"]),
    "get_weather": lambda inp: tool_get_weather(inp["location"]),
    "search_web": lambda inp: tool_search_web(inp["query"]),
    "get_wikipedia_summary": lambda inp: tool_get_wikipedia_summary(inp["topic"]),
    "save_note": lambda inp: tool_save_note(inp["title"], inp["content"]),
    "list_notes": lambda _: tool_list_notes(),
    "read_note": lambda inp: tool_read_note(inp["title"]),
    "run_python": lambda inp: tool_run_python(inp["code"]),
}


def execute_tool(name: str, tool_input: dict) -> str:
    handler = _TOOL_MAP.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = handler(tool_input)
    return json.dumps(result)


# ─── Terminal Display ──────────────────────────────────────────────────────────

RESET = "\033[0m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[90m"
RED = "\033[91m"
BOLD = "\033[1m"


def print_banner() -> None:
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║   J·A·R·V·I·S  —  Advanced Personal AI Assistant            ║
  ║   Just A Rather Very Intelligent System                      ║
  ║                                                              ║
  ║   Powered by Claude Opus 4.6  ·  Adaptive Thinking          ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
{RESET}"""
    print(banner)


def hr() -> None:
    print(f"{DIM}{'─' * 64}{RESET}")


def jarvis_prefix() -> None:
    print(f"\n{BLUE}{BOLD}JARVIS{RESET}{BLUE}:{RESET} ", end="", flush=True)


def user_prompt() -> None:
    print(f"\n{GREEN}{BOLD}You{RESET}{GREEN}:{RESET} ", end="", flush=True)


def tool_status(name: str, ok: bool) -> None:
    icon = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f" {icon}", flush=True)


# ─── Core Agent Loop ───────────────────────────────────────────────────────────

def run() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(f"{RED}Error: ANTHROPIC_API_KEY is not set.{RESET}", file=sys.stderr)
        print(
            "Set it as an environment variable or create a 'secret.anthropic-api-key' file.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    conversation: list[dict] = []

    print_banner()
    print(f"{DIM}  Connecting to Claude Opus 4.6…{RESET}", flush=True)

    # ── Opening greeting ──────────────────────────────────────────────────────
    try:
        greeting_resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Greet the user concisely (2–3 sentences). "
                        "Introduce yourself as JARVIS and ask what you can help with."
                    ),
                }
            ],
        )
        greeting = next(
            (b.text for b in greeting_resp.content if b.type == "text"), "Good day. How may I assist?"
        )
    except anthropic.AuthenticationError:
        print(f"\n{RED}Authentication failed. Check your ANTHROPIC_API_KEY.{RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n{RED}Startup error: {exc}{RESET}", file=sys.stderr)
        sys.exit(1)

    # Seed conversation with greeting exchange
    conversation.append(
        {
            "role": "user",
            "content": "Greet the user concisely (2–3 sentences). Introduce yourself as JARVIS and ask what you can help with.",
        }
    )
    conversation.append({"role": "assistant", "content": greeting_resp.content})

    hr()
    jarvis_prefix()
    print(greeting)

    # ── Main conversation loop ────────────────────────────────────────────────
    while True:
        hr()
        user_prompt()

        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{CYAN}JARVIS: Goodbye. It has been a pleasure serving you.{RESET}\n")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye", "goodbye", "/exit", "/quit"}:
            jarvis_prefix()
            print("Goodbye. It has been a pleasure serving you.")
            break

        conversation.append({"role": "user", "content": user_input})

        # ── Agentic streaming loop ────────────────────────────────────────────
        jarvis_prefix()
        thinking_shown = False

        while True:
            accumulated_text = ""

            try:
                with client.messages.stream(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    thinking={"type": "adaptive"},
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=conversation,
                ) as stream:
                    for event in stream:
                        if event.type == "content_block_start":
                            if event.content_block.type == "thinking" and not thinking_shown:
                                print(f"{DIM}[thinking]{RESET} ", end="", flush=True)
                                thinking_shown = True

                        elif event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                print(event.delta.text, end="", flush=True)
                                accumulated_text += event.delta.text

                    final = stream.get_final_message()

            except anthropic.RateLimitError:
                print(f"\n{YELLOW}[Rate limited — please wait a moment and try again.]{RESET}")
                conversation.pop()  # Remove the user message we just added
                break
            except anthropic.APIConnectionError as exc:
                print(f"\n{RED}[Connection error: {exc}]{RESET}")
                conversation.pop()
                break
            except Exception as exc:
                print(f"\n{RED}[Error: {exc}]{RESET}")
                conversation.pop()
                break

            # Append full content (preserves thinking + tool_use blocks)
            conversation.append({"role": "assistant", "content": final.content})

            if final.stop_reason == "end_turn":
                print()  # newline after streamed text
                break

            # ── Handle tool calls ─────────────────────────────────────────────
            tool_use_blocks = [b for b in final.content if b.type == "tool_use"]
            if not tool_use_blocks:
                print()
                break

            tool_results = []
            for block in tool_use_blocks:
                print(f"\n  {DIM}[{block.name}]{RESET}", end="", flush=True)
                result_str = execute_tool(block.name, block.input)
                result_data = json.loads(result_str)
                has_error = "error" in result_data
                tool_status(block.name, not has_error)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                        **({"is_error": True} if has_error else {}),
                    }
                )

            conversation.append({"role": "user", "content": tool_results})

            # Continue with JARVIS prefix for the follow-up response
            jarvis_prefix()
            thinking_shown = False


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run()
