#!/usr/bin/env python3
"""Classify loglm decoded logs and extract repo-improvement candidates.

Expects input already decoded by `loglm-decode`.  Raw ANSI stripping is
no longer performed here — use `loglm-decode` first.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

BOILERPLATE_PATTERNS = [
    re.compile(r"^\s*$"),
    re.compile(r"^[─━═╭╮╰╯│┌┐└┘├┤┬┴┼\-\s]+$"),
    re.compile(r"^\s*(Working|Thinking|Exploring|Running)(\(|$)"),
    re.compile(r"^\s*gpt-[\w.-]+ .* ~/"),
    re.compile(r"^\s*Token usage:"),
]

INSIGHT_NOISE_PATTERNS = [
    re.compile(r"^Would you like to run the following command\?"),
    re.compile(r"^Reason: command failed; retry without sandbox\?"),
    re.compile(r"^Press enter to confirm or esc to cancel$"),
    re.compile(r"^› \d+\. "),
    re.compile(r"^\d+\. Yes,"),
    re.compile(r"^\d+\. No,"),
    re.compile(r"^\$ "),
]

CATEGORY_PATTERNS = {
    "ops_cdp_auth": [
        r"\bCDP\b",
        r"Chrome",
        r"LaunchAgent|launchd",
        r"unauthenticated|signin\.aws\.amazon\.com",
        r"AWS_BILLING_CHROME_CDP_URL",
        r"manual_navigation_timeout",
        r"profile",
        r"922[0-9]",
    ],
    "state_model": [
        r"\bfailed\b",
        r"\bnot_found\b",
        r"\breview_needed\b",
        r"\bdry_run_ready\b",
        r"\bfailed_only\b",
        r"\bpending\b",
        r"\bposted\b",
        r"\bmanual_completed\b",
        r"\bstate_status\b",
        r"\bthread_state\b",
    ],
    "docs_runbook": [
        r"README",
        r"runbook",
        r"docs/",
        r"TODO",
        r"明文化",
        r"次に",
        r"結論",
        r"方針",
    ],
    "tests_guardrails": [
        r"pytest",
        r"\btests?/",
        r"\btest\b",
        r"guardrail",
        r"RuntimeError",
        r"selector",
        r"hardening",
        r"verification",
    ],
    "slack_voucher_flow": [
        r"Slack",
        r"UPSIDER",
        r"証憑",
        r"upload",
        r"thread",
        r"permalink",
        r"settlement",
    ],
    "service_collectors": [
        r"\bAWS\b",
        r"ekinet|eki-net",
        r"freee",
        r"amazon",
        r"openai",
        r"times_car|TIMES CAR",
        r"collector",
        r"portal",
    ],
    "tooling_errors": [
        r"ConnectError",
        r"invalid_grant",
        r"MCP startup",
        r"WARNING",
        r"timeout|Timeout",
        r"Exception|Traceback|ERROR|Error",
    ],
}

COMPILED_CATEGORIES = {
    name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for name, patterns in CATEGORY_PATTERNS.items()
}


@dataclass(frozen=True)
class CleanedLog:
    source: Path
    output: Path | None
    line_count: int
    kept_line_count: int
    text: str


def expand_inputs(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            # Prefer .decoded.txt produced by loglm-decode
            decoded = sorted(path.glob("*.decoded.txt"))
            if decoded:
                paths.extend(decoded)
            else:
                paths.extend(sorted(path.glob("loglm-codex-log-*.txt")))
                paths.extend(sorted(p for p in path.glob("*.txt") if p not in paths))
        else:
            paths.append(path)
    return paths


def is_boilerplate(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) <= 1:
        return True
    return any(pattern.search(stripped) for pattern in BOILERPLATE_PATTERNS)


def is_insight_noise(line: str) -> bool:
    stripped = line.strip()
    return any(pattern.search(stripped) for pattern in INSIGHT_NOISE_PATTERNS)


def clean_text(text: str, *, semantic_only: bool = False) -> str:
    """Normalize already-decoded text: deduplicate, strip boilerplate."""
    lines: list[str] = []
    previous = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        line = re.sub(r"\s+", " ", line)
        if is_boilerplate(line):
            continue
        if semantic_only and not _line_matches_any_category(line):
            continue
        if line == previous:
            continue
        lines.append(line)
        previous = line

    return "\n".join(lines).strip() + ("\n" if lines else "")


def _line_matches_any_category(line: str) -> bool:
    return any(p.search(line) for ps in COMPILED_CATEGORIES.values() for p in ps)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def clean_file(path: Path, output_dir: Path | None, *, semantic_only: bool) -> CleanedLog:
    raw = read_text(path)
    cleaned = clean_text(raw, semantic_only=semantic_only)
    output_path = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".semantic.txt" if semantic_only else ".clean.txt"
        output_path = output_dir / f"{path.stem}{suffix}"
        output_path.write_text(cleaned, encoding="utf-8")
    return CleanedLog(
        source=path,
        output=output_path,
        line_count=len(raw.splitlines()),
        kept_line_count=len(cleaned.splitlines()),
        text=cleaned,
    )


def classify_lines(logs: list[CleanedLog], *, max_per_category: int, context: int) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()

    for log in logs:
        lines = log.text.splitlines()
        for index, line in enumerate(lines):
            for category, patterns in COMPILED_CATEGORIES.items():
                if len(grouped[category]) >= max_per_category or is_insight_noise(line):
                    continue
                if not any(pattern.search(line) for pattern in patterns):
                    continue
                normalized = re.sub(r"\s+", " ", line).lower()
                key = (category, normalized[:220])
                if key in seen:
                    continue
                seen.add(key)
                start = max(0, index - context)
                end = min(len(lines), index + context + 1)
                excerpt = "\n".join(f"    {item}" for item in lines[start:end])
                grouped[category].append(f"- `{log.source}` line~{index + 1}\n{excerpt}")
    return grouped


def write_summary(logs: list[CleanedLog], path: Path) -> None:
    total_raw = sum(log.line_count for log in logs)
    total_kept = sum(log.kept_line_count for log in logs)
    lines = [
        "# loglm Clean Summary",
        "",
        f"- files: {len(logs)}",
        f"- raw_lines: {total_raw}",
        f"- kept_lines: {total_kept}",
        "",
        "## Files",
    ]
    for log in logs:
        output = str(log.output) if log.output else "(stdout only)"
        lines.append(f"- `{log.source}` -> `{output}` ({log.line_count} raw, {log.kept_line_count} kept)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_insights(logs: list[CleanedLog], path: Path, *, max_per_category: int, context: int) -> None:
    grouped = classify_lines(logs, max_per_category=max_per_category, context=context)
    lines = [
        "# loglm Repo Insight Candidates",
        "",
        "This file is a local evidence index, not a final recommendation.",
        "Review each excerpt before turning it into a repo change.",
        "",
    ]
    for category in CATEGORY_PATTERNS:
        lines.append(f"## {category}")
        items = grouped.get(category, [])
        if not items:
            lines.append("- No candidate lines found.")
        else:
            lines.extend(items)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="loglm .txt files or directories")
    parser.add_argument("--output-dir", type=Path, help="write per-file cleaned logs here")
    parser.add_argument("--combined-output", type=Path, help="write all cleaned logs into one text file")
    parser.add_argument("--summary-output", type=Path, help="write a Markdown clean summary")
    parser.add_argument("--insights-output", type=Path, help="write category-based repo insight candidates")
    parser.add_argument("--semantic-only", action="store_true", help="keep only lines matching insight patterns")
    parser.add_argument("--max-per-category", type=int, default=20)
    parser.add_argument("--context", type=int, default=0, help="context lines around each insight candidate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = expand_inputs(args.inputs)
    missing = [path for path in paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing input: {path}", file=sys.stderr)
        return 2

    logs = [clean_file(path, args.output_dir, semantic_only=args.semantic_only) for path in paths]
    if args.combined_output:
        args.combined_output.parent.mkdir(parents=True, exist_ok=True)
        combined = []
        for log in logs:
            combined.append(f"===== {log.source} =====\n{log.text}")
        args.combined_output.write_text("\n".join(combined), encoding="utf-8")
    if args.summary_output:
        write_summary(logs, args.summary_output)
    if args.insights_output:
        write_insights(logs, args.insights_output, max_per_category=args.max_per_category, context=args.context)
    if not any([args.output_dir, args.combined_output, args.summary_output, args.insights_output]):
        for log in logs:
            print(f"===== {log.source} =====")
            print(log.text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
