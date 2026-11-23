#!/usr/bin/env python3
"""서브에이전트 진행 점검.

원장의 running task와 서브에이전트 기록 파일(subagents/agent-<id>.jsonl)을 대조해
에이전트마다 마지막 기록 시각, 마지막 도구 호출, 상태를 한 줄씩 출력한다.

상태:
  일하는 중  마지막 도구 호출이 보고(SubagentHandback)가 아니고 기록이 STALE분 안
  멈춤?      마지막 도구 호출이 보고가 아닌데 STALE분 넘게 기록이 없음
  보고함     마지막 도구 호출이 보고. 리더가 확인·머지한 뒤 종료해야 한다
원장에 running인데 그 task 번호를 받은 살아 있는 에이전트가 없으면 "에이전트 없음"을 출력한다.

사용: agent-check.py <run> [--session-dir DIR] [--stale 20] [--hours 12]
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 리더 메시지가 붙이는 머리. 이것을 떼고 본문 첫머리만 본다
RELAY_PREFIX = "The coordinator sent a message while you were working:"
# 브리프·이어 맡긴 메시지는 형식이 여럿이다("## TASK ... task: FL", "run X, task V5",
# "새 task B7(", "B2 재작업(B2-W1)"). "task <번호>"가 있으면 그것을, 없으면 첫머리에 나온
# 원장 task 번호를 쓴다. 번호만 찾을 때 첫머리로 좁히는 것은 본문 뒤쪽에 지난 task 번호를
# 인용한 메시지가 지금 맡은 task를 덮어쓰지 않게 하려는 것이다.
HEAD = 200
TASK_RE = re.compile(r"\btask:?\s+([A-Z][A-Za-z0-9-]*)")


def default_session_dir() -> Path:
    # 이 저장소의 프로젝트 기록 디렉터리 가운데 가장 최근에 바뀐 세션의 subagents
    slug = "-" + str(Path.cwd().resolve()).replace("/", "-").lstrip("-")
    base = Path.home() / ".claude" / "projects" / slug
    dirs = [d for d in base.glob("*/subagents") if d.is_dir()]
    return max(dirs, key=lambda d: d.stat().st_mtime)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def message_tasks(text: str, known: re.Pattern) -> set[str]:
    text = text.strip().removeprefix(RELAY_PREFIX).strip()
    if not text or text.startswith(("<", "[Image")):
        return set()  # 스킬 본문, 시스템 알림, 그림은 맡김이 아니다
    # "task <번호>"는 맡김을 밝히는 말이라 본문 어디에 있어도 쓴다. 첫 것만 쓴다
    explicit = next((t for t in TASK_RE.findall(text) if known.fullmatch(t)), None)
    return {explicit} if explicit else set(known.findall(text[:HEAD]))


def read_agent(path: Path, known: re.Pattern) -> dict:
    last_ts = None
    last_tool = ""
    tasks: set[str] = set()
    for line in path.open(encoding="utf-8"):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ts := entry.get("timestamp"):
            last_ts = parse_ts(ts)
        content = (entry.get("message") or {}).get("content")
        # 브리프와 이어 맡긴 메시지의 "task <번호>"가 그 에이전트가 지금 맡은 task다
        if entry.get("type") == "user":
            # 쉬던 에이전트를 깨운 메시지는 문자열이 아니라 글 조각 목록으로 온다
            texts = [content] if isinstance(content, str) else [
                i.get("text", "") for i in content or [] if isinstance(i, dict) and i.get("type") == "text"]
            for text in texts:
                if found := message_tasks(text, known):
                    tasks = found
        if entry.get("type") == "assistant" and isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    brief = json.dumps(item.get("input", {}), ensure_ascii=False)
                    last_tool = f"{item.get('name')} {brief[:90]}"
    meta = path.with_suffix("").with_suffix(".meta.json")
    description = ""
    if meta.exists():
        description = json.loads(meta.read_text(encoding="utf-8")).get("description", "")
    return {"id": path.stem.removeprefix("agent-"), "last": last_ts, "tool": last_tool,
            "tasks": tasks, "description": description}


def run_task_status(run: str) -> dict[str, str]:
    path = HERE.parents[3] / "_tasks" / run / "tasks.json"
    return {t["id"]: t["status"] for t in json.loads(path.read_text(encoding="utf-8"))["tasks"]}


def running_tasks(run: str) -> list[str]:
    out = subprocess.run([sys.executable, str(HERE / "ledger.py"), "show", run],
                         capture_output=True, text=True, check=False).stdout
    return [line.split()[0] for line in out.splitlines() if re.search(r"\brunning\b", line)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--session-dir", type=Path)
    ap.add_argument("--stale", type=int, default=20, help="이 분 넘게 기록이 없으면 멈춤?")
    ap.add_argument("--hours", type=int, default=12, help="이 시간 안에 바뀐 기록만 본다")
    args = ap.parse_args()

    now = datetime.now(UTC)
    session_dir = args.session_dir or default_session_dir()
    cutoff = (now - timedelta(hours=args.hours)).timestamp()
    status = run_task_status(args.run)
    # 긴 번호부터 맞춰 "DA4-W1"이 "DA4"로 잘리지 않게 한다
    ids = sorted(status, key=len, reverse=True)
    known = re.compile(r"(?<![A-Za-z0-9-])(" + "|".join(map(re.escape, ids)) + r")(?![A-Za-z0-9-])")
    agents = [read_agent(p, known) for p in session_dir.glob("agent-*.jsonl") if p.stat().st_mtime >= cutoff]
    # 다른 run의 task를 맡았던 에이전트는 이 run의 점검 대상이 아니다
    for a in agents:
        a["tasks"] &= status.keys()
    agents = [a for a in agents if a["tasks"]]
    stamp = datetime.now().strftime("%H:%M")

    alive_tasks = set()
    for a in sorted(agents, key=lambda a: a["last"] or now):
        if a["last"] is None:
            continue
        idle = int((now - a["last"]).total_seconds() // 60)
        if a["tool"].startswith("SubagentHandback"):
            state = "보고함"
        elif idle > args.stale:
            state = "멈춤?"
        else:
            state = "일하는 중"
            alive_tasks |= a["tasks"]
        # 리더가 이미 닫았거나(done) 막힘으로 기록한(failed) task의 보고는 다시 알리지 않는다
        closed = all(status[t] in ("done", "failed") for t in a["tasks"])
        if state == "보고함" and (closed or idle > args.stale):
            continue  # 리더가 이미 닫은 task나 오래전에 끝난 보고는 출력하지 않는다
        if state == "멈춤?" and closed:
            continue  # 리더가 닫고 멈춘 에이전트는 멈춘 것이 맞다
        if state == "일하는 중":
            continue  # 정상은 알리지 않는다. 알림은 리더가 손댈 일만
        tool = "" if state == "보고함" else f" | {a['tool']}"
        print(f"[{stamp}] {state} {','.join(sorted(a['tasks']))} {a['description']} ({a['id'][:7]}) "
              f"마지막 기록 {idle}분 전{tool}")

    tasks = json.loads((HERE.parents[3] / "_tasks" / args.run / "tasks.json").read_text(encoding="utf-8"))["tasks"]
    # 재작업 task는 2차 판정이 도는 동안 running으로 남는다. 그 판정이 일하고 있으면 정상이다
    judged = {t.get("target") for t in tasks if t.get("target") and t["id"] in alive_tasks}
    rework = {t["id"] for t in tasks if t.get("target") in judged and t.get("fixes")}
    for task in running_tasks(args.run):
        if task not in alive_tasks and task not in rework:
            print(f"[{stamp}] 에이전트 없음 {task}: 원장은 running인데 일하는 에이전트가 없다")
    # 자리가 비었는데 던질 수 있는 task가 남아 있으면 리더가 멈춘 것이다
    ready = subprocess.run([sys.executable, str(HERE / "ledger.py"), "ready", args.run],
                           capture_output=True, text=True, check=False).stdout
    ready_ids = [line.split("\t")[0] for line in ready.splitlines() if "\t" in line]
    # 의존이 풀렸어도 리더가 일부러 붙잡아 둔 task는 대기가 아니다. 원장의 ready가 pending을
    # 다시 올리므로 붙잡은 번호는 _tasks/<run>/hold 파일에 한 줄에 하나씩 둔다
    hold_file = HERE.parents[3] / "_tasks" / args.run / "hold"
    held = set(hold_file.read_text(encoding="utf-8").split()) if hold_file.exists() else set()
    ready_ids = [t for t in ready_ids if t not in held]
    if ready_ids and len(alive_tasks) < 5:
        print(f"[{stamp}] 투입 대기 {', '.join(ready_ids)}: 일하는 에이전트 {len(alive_tasks)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
