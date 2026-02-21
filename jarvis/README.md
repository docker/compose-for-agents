# J.A.R.V.I.S — Advanced Personal AI Assistant

> **J**ust **A** **R**ather **V**ery **I**ntelligent **S**ystem

An advanced conversational AI assistant in the spirit of Tony Stark's iconic JARVIS, powered by **Claude Opus 4.6** with adaptive thinking, streaming responses, and a rich set of built-in tools.

## Features

- **Adaptive Thinking** — Claude reasons through complex problems before responding
- **Streaming responses** — Answers appear in real-time, token by token
- **Multi-turn memory** — Remembers full conversation context
- **Persistent notes** — Save, list, and retrieve notes across sessions
- **9 built-in tools** (no MCP servers required):

| Tool | Description |
|------|-------------|
| `get_current_datetime` | Date/time in any IANA timezone |
| `calculate` | Math & scientific calculations |
| `get_weather` | Live weather worldwide (via wttr.in) |
| `search_web` | DuckDuckGo instant answers |
| `get_wikipedia_summary` | Encyclopedia summaries |
| `save_note` | Persist notes to disk |
| `list_notes` | List all saved notes |
| `read_note` | Read a saved note by title |
| `run_python` | Execute Python snippets |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.43.0+ or Docker Engine with Compose
- An [Anthropic API key](https://console.anthropic.com/)

## Quick Start

### Option A — Secret file (recommended)

```sh
cd jarvis

# Put your API key in a secret file (never committed to git)
echo "sk-ant-..." > secret.anthropic-api-key

# Build and run interactively
docker compose run --rm jarvis
```

### Option B — Environment variable

```sh
cd jarvis
export ANTHROPIC_API_KEY=sk-ant-...

docker compose -f compose.yaml -f compose.env.yaml run --rm jarvis
```

## Example Interactions

```
You: What's the weather like in Tokyo right now?

JARVIS: [weather tool] ✓
JARVIS: Currently in Tokyo, Japan it is 22°C (72°F) with partly cloudy skies.
        Humidity sits at 65%, winds from the northeast at 15 km/h.
        Today's range: 18°C–25°C, with sunrise at 5:12 AM and sunset at 6:48 PM.

You: What is the 10,000th prime number?

JARVIS: [thinking] [run_python] ✓
JARVIS: The 10,000th prime number is 104,729. I computed it using the
        Sieve of Eratosthenes in Python.

You: Save a note — "Prime facts" — The 10,000th prime is 104,729.

JARVIS: [save_note] ✓
JARVIS: Done, sir. Note "Prime facts" has been saved and will persist
        across sessions.

You: Who was Alan Turing and why does he matter?

JARVIS: [get_wikipedia_summary] ✓
JARVIS: Alan Turing (1912–1954) was a British mathematician and computer scientist
        widely regarded as the father of theoretical computer science and AI...
```

## Architecture

```
agent.py          ← Single-file agent: Claude API client, tool loop, terminal UI
requirements.txt  ← anthropic SDK only
Dockerfile        ← python:3.12-slim + tzdata + anthropic
compose.yaml      ← Interactive service, secret mounting, notes volume
```

The agentic loop:

1. User types a message
2. Claude (with adaptive thinking) streams a response
3. If Claude calls a tool, it is executed locally and results are fed back
4. Claude continues streaming until it reaches `end_turn`
5. Repeat

## Notes Persistence

Notes are stored in a Docker named volume (`jarvis-notes`) mounted at `/data/notes`.
They persist across container restarts and rebuilds unless you explicitly remove the volume:

```sh
docker volume rm jarvis_jarvis-notes
```

## License

Apache-2.0 OR MIT — see repo root for details.
