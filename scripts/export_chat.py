"""Export the relevant part of a Claude Code session log (JSONL) to Markdown.

Keeps: the user's prompts, the assistant's visible replies, the user's answers to clarifying questions,
and a one-line list of the actions (tool calls) per turn. Drops: hidden reasoning, raw tool output,
system/skill text, and screenshots.

Usage: py scripts/export_chat.py <session.jsonl> <out.md>
"""
import json, sys, re

src, out = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(src, encoding="utf-8")]

TOOL_LABEL = {
    "Bash": "shell", "PowerShell": "shell", "Read": "read file", "Write": "write file", "Edit": "edit file",
    "Grep": "search", "Glob": "find files", "WebFetch": "fetch web page", "Skill": "load skill",
    "ToolSearch": None, "AskUserQuestion": None, "ExitPlanMode": "submit plan",
}


def describe(name, inp):
    if name.startswith("mcp__claude-in-chrome__"):
        short = name.split("__")[-1]
        if short in ("tabs_context_mcp", "tabs_create_mcp"):
            return None
        detail = inp.get("action_summary") or inp.get("url") or inp.get("action") or ""
        return f"browser {short.replace('_', ' ')}" + (f": {detail}" if detail else "")
    label = TOOL_LABEL.get(name, name)
    if label is None:
        return None
    detail = inp.get("description") or inp.get("skill") or inp.get("url") or ""
    if not detail and inp.get("file_path"):
        detail = inp["file_path"].split("\\")[-1].split("/")[-1]
    return f"{label}: {detail}" if detail else label


lines = ["# AI chat log — NT6094 midterm (UTS) 2026-1",
         "",
         "Tool: **Claude Code** (model **Claude Opus 5.5**, Anthropic), CLI session on 14 October 2026.  ",
         "User: Pradigta Hisyam Ramadhan (NIM 28726019).",
         "",
         "This export keeps only what is relevant to the assignment: the user's prompts, the assistant's visible "
         "replies, the user's answers to clarifying questions, and a short list of the actions the assistant "
         "performed in each turn. Hidden reasoning, raw tool output, screenshots and system text are omitted. "
         "Replies are in Indonesian, as in the original chat.",
         ""]

turn = 0
actions, pending_q = [], {}


def flush_actions():
    global actions
    if actions:
        lines.append("<details><summary>Actions performed (" + str(len(actions)) + ")</summary>\n")
        lines.extend(f"- {a}" for a in actions)
        lines.append("\n</details>\n")
    actions = []


for o in rows:
    t, m = o.get("type"), o.get("message") or {}
    content = m.get("content")
    if t == "user" and isinstance(content, str) and not o.get("isMeta"):
        if content.startswith("<") or content.startswith("[Image"):
            continue
        flush_actions()
        turn += 1
        lines += [f"## Prompt {turn}", "", "> " + content.strip().replace("\n", "\n> "), ""]
    elif t == "user" and isinstance(content, list):
        for c in content:
            if c.get("type") == "tool_result" and c.get("tool_use_id") in pending_q:
                txt = c.get("content")
                if isinstance(txt, list):
                    txt = " ".join(x.get("text", "") for x in txt if isinstance(x, dict))
                txt = txt or ""
                lines.append("**Clarifying question answered by the user:**\n")
                for q in pending_q[c["tool_use_id"]]:
                    key = '"' + q + '"="'
                    i = txt.find(key)
                    a = txt[i + len(key):txt.find('"', i + len(key))] if i >= 0 else "(no answer)"
                    lines.append(f"- {q} → **{a}**")
                lines.append("")
    elif t == "assistant" and isinstance(content, list):
        for c in content:
            if c.get("type") == "text" and c.get("text", "").strip():
                flush_actions()
                lines += ["**Claude:**", "", c["text"].strip(), ""]
            elif c.get("type") == "tool_use":
                if c["name"] == "AskUserQuestion":
                    pending_q[c["id"]] = [q["question"] for q in c.get("input", {}).get("questions", [])]
                    continue
                d = describe(c["name"], c.get("input", {}))
                if d:
                    actions.append(d)
flush_actions()
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(out, "prompts:", turn)
