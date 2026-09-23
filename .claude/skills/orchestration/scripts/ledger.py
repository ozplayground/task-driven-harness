#!/usr/bin/env python3
"""task 원장(ledger) 도구. 표준 라이브러리만 사용한다.

원장은 `_tasks/<run>/tasks.json` 하나다. 이 스크립트는 그 파일을
읽고 쓰는 유일한 경로이며, 상태 전이·의존 해소·경로 겹침을 기계적으로 판정한다.

사용법:
  ledger.py init     <run> --request "요청 한 줄"
  ledger.py add      <run> <id> --agent <에이전트> --title T --paths a/**,b.md
                     [--depends T1,T2] [--accept "기준1" --accept "기준2"] [--because "근거"]
                     [--target T1] [--fixes T1-F1,T1-F2]
                       target: 리뷰·비평·재작업·보안 검토가 대상으로 삼는 task
                       fixes : 재작업이 고칠 finding ID (대상 task에 기록된 것)
  ledger.py validate <run>          # 스키마·의존 사이클·동시 실행 가능 task 간 경로 겹침 검사
  ledger.py ready    <run>          # 의존이 모두 done인 task 목록 (투입 대상). 승인 전에는 조사·구조·비평·문서 리뷰만
  ledger.py set      <run> <id> <status> [--note "..."] [--because "근거"]
  ledger.py finding  <run> <id> add <fid> <severity> "내용"      # id = 산출물을 만든 task
  ledger.py finding  <run> <id> resolve|waive <fid> [--note "..."]
  ledger.py brief    <run> <id>     # 브리프에 옮길 것: task 필드와 의존 task의 산출물·보고서 경로
  ledger.py show     <run> [--paths]
  ledger.py approve  <run>          # planning → approved (승인 뒤 리더가 호출)

상태: pending → ready → running → done
                        running → failed → ready (재투입)
                        running → ready (생성 거부 시 큐로 되돌림)

리뷰·비평·재작업은 상태가 아니라 task다. 리더가 add로 만들고 --target으로 대상을 가리킨다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

ROOT = os.environ.get("ORCHESTRATION_ROOT", os.getcwd())
STATUSES = ["pending", "ready", "running", "done", "failed"]
TRANSITIONS = {
    "pending": {"ready"},
    "ready": {"running", "pending"},
    "running": {"done", "failed", "ready"},
    "failed": {"ready"},
    "done": set(),
}
AGENTS = [
    "researcher", "architect", "spec-writer", "ux-designer", "contract-designer", "security",
    "backend-developer", "frontend-developer", "devops", "verifier",
    "critic", "doc-reviewer", "code-reviewer",
]
JUDGES = {"critic", "doc-reviewer", "code-reviewer"}   # 산출물을 고치지 않는다. target이 있어야 한다 (critic의 계획 비판은 예외)
PLANNING_AGENTS = {"researcher", "architect", "critic", "doc-reviewer"}   # 승인 전에도 돌 수 있다
SEVERITIES = ["blocker", "major", "minor"]
RUN_STATUSES = ["planning", "approved", "running", "done"]


def now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def path_of(run: str) -> str:
    return os.path.join(ROOT, "_tasks", run, "tasks.json")


def load(run: str) -> dict:
    p = path_of(run)
    if not os.path.exists(p):
        sys.exit(f"원장이 없다: {p}  (ledger.py init {run} 먼저)")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(run: str, data: dict) -> None:
    p = path_of(run)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def log(data: dict, event: str, because: str | None = None) -> None:
    entry = {"at": now(), "event": event}
    if because:
        entry["because"] = because
    data.setdefault("log", []).append(entry)


def task_of(data: dict, tid: str) -> dict:
    for t in data["tasks"]:
        if t["id"] == tid:
            return t
    sys.exit(f"task 없음: {tid}")


def find(data: dict, tid: str) -> dict | None:
    return next((t for t in data["tasks"] if t["id"] == tid), None)


# ---------- 경로 겹침 ----------

def _prefix(pattern: str) -> str:
    """glob 문자가 나오기 전까지의 리터럴 접두어. 'src/api/orders/**' → 'src/api/orders/'"""
    out = []
    for ch in pattern:
        if ch in "*?[":
            break
        out.append(ch)
    return "".join(out)


def overlaps(a: str, b: str) -> bool:
    pa, pb = _prefix(a), _prefix(b)
    if not pa or not pb:
        return True
    return pa.startswith(pb) or pb.startswith(pa)


def ancestors(data: dict, tid: str) -> set:
    seen, stack = set(), [tid]
    while stack:
        cur = stack.pop()
        t = find(data, cur)
        if not t:
            continue
        for d in t.get("depends_on", []):
            if d not in seen:
                seen.add(d)
                stack.append(d)
    return seen


def concurrent_pairs(data: dict):
    """의존 관계로 순서가 정해지지 않은 task 쌍 = 동시에 돌 수 있는 쌍."""
    ids = [t["id"] for t in data["tasks"]]
    anc = {i: ancestors(data, i) for i in ids}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if b in anc[a] or a in anc[b]:
                continue
            yield a, b


# ---------- 명령 ----------

def cmd_init(args):
    p = path_of(args.run)
    if os.path.exists(p):
        sys.exit(f"이미 있다: {p}")
    data = {
        "run": args.run,
        "request": args.request,
        "created": now(),
        "status": "planning",
        "given": [],
        "wanted": [],
        "gaps": [],
        "tasks": [],
        "log": [],
    }
    log(data, "init")
    save(args.run, data)
    for sub in ("reports", "reviews", "critique"):
        os.makedirs(os.path.join(os.path.dirname(p), sub), exist_ok=True)
    notes = os.path.join(os.path.dirname(p), "notes.md")
    if not os.path.exists(notes):
        with open(notes, "w", encoding="utf-8") as f:
            f.write(f"# {args.run} — 결정·질문·가정 기록 (덧붙이기만 한다)\n\n")
    print(f"생성: {p}")


def cmd_add(args):
    data = load(args.run)
    if find(data, args.id):
        sys.exit(f"중복 id: {args.id}")
    if args.agent not in AGENTS:
        sys.exit(f"agent는 {', '.join(AGENTS)} 중 하나")
    target = args.target
    fixes = [s for s in (args.fixes or "").split(",") if s]
    if target:
        tt = task_of(data, target)
        if fixes:
            if args.agent != tt["agent"]:
                sys.exit(f"재작업은 대상 task와 같은 에이전트가 한다: {target}는 {tt['agent']}")
            known = {f["id"] for f in tt["findings"]}
            missing = [f for f in fixes if f not in known]
            if missing:
                sys.exit(f"{target}에 없는 finding: {', '.join(missing)}")
    elif fixes:
        sys.exit("--fixes는 --target과 함께 쓴다")
    depends = [s for s in (args.depends or "").split(",") if s]
    if target and target not in depends:
        depends.append(target)
    same = [t for t in data["tasks"] if t.get("target") == target and t["agent"] == args.agent] if target else []
    rnd = len(same) + 1 if target else 0
    t = {
        "id": args.id,
        "title": args.title,
        "agent": args.agent,
        "paths": [s for s in args.paths.split(",") if s],
        "depends_on": depends,
        "acceptance": args.accept or [],
        "status": "pending",
        "round": rnd,
        "attempts": 0,
        "findings": [],
        "report": f"_tasks/{args.run}/reports/{args.id}.md",
    }
    if target:
        t["target"] = target
    if fixes:
        t["fixes"] = fixes
    data["tasks"].append(t)
    log(data, f"add {args.id} ({args.agent}" + (f" → {target}" if target else "") + ")", args.because)
    save(args.run, data)
    print(f"추가: {args.id} [{args.agent}]" + (f" target={target} round={rnd}" if target else ""))


def validate(data: dict) -> list:
    errs = []
    ids = {t["id"] for t in data["tasks"]}
    for t in data["tasks"]:
        if t["status"] not in STATUSES:
            errs.append(f"{t['id']}: 알 수 없는 상태 {t['status']}")
        if t.get("agent") not in AGENTS:
            errs.append(f"{t['id']}: 알 수 없는 에이전트 {t.get('agent')}")
        if not t.get("paths"):
            errs.append(f"{t['id']}: 소유 경로가 없다")
        if not t.get("acceptance"):
            errs.append(f"{t['id']}: 완료 기준(acceptance)이 없다")
        if t.get("agent") in JUDGES - {"critic"} and not t.get("target"):
            errs.append(f"{t['id']}: 리뷰 task는 --target이 있어야 한다")
        if t.get("target") and t["target"] not in ids:
            errs.append(f"{t['id']}: 없는 대상 {t['target']}")
        if t.get("target") and t["target"] not in t.get("depends_on", []):
            errs.append(f"{t['id']}: 대상 {t['target']}에 의존해야 한다")
        for d in t.get("depends_on", []):
            if d not in ids:
                errs.append(f"{t['id']}: 없는 의존 {d}")
            if d == t["id"]:
                errs.append(f"{t['id']}: 자기 의존")
    state = {}

    def dfs(tid):
        state[tid] = 1
        for d in task_of(data, tid).get("depends_on", []):
            if d not in ids:
                continue
            if state.get(d) == 1:
                errs.append(f"의존 사이클: {tid} ↔ {d}")
            elif state.get(d) is None:
                dfs(d)
        state[tid] = 2

    for tid in ids:
        if state.get(tid) is None:
            dfs(tid)
    for a, b in concurrent_pairs(data):
        ta, tb = task_of(data, a), task_of(data, b)
        for pa in ta["paths"]:
            for pb in tb["paths"]:
                if overlaps(pa, pb):
                    errs.append(f"경로 겹침: {a}({pa}) ↔ {b}({pb}) — 의존을 걸거나 경로를 가르라")
    return errs


def cmd_validate(args):
    data = load(args.run)
    errs = validate(data)
    if errs:
        print("\n".join("✗ " + e for e in errs))
        sys.exit(1)
    print("✓ 원장 유효")


def cmd_ready(args):
    data = load(args.run)
    planning = data["status"] == "planning"
    done = {t["id"] for t in data["tasks"] if t["status"] == "done"}
    out = []
    for t in data["tasks"]:
        if planning and t["agent"] not in PLANNING_AGENTS:
            continue
        if t["status"] in ("pending", "ready") and all(d in done for d in t.get("depends_on", [])):
            if t["status"] == "pending":
                t["status"] = "ready"
                log(data, f"{t['id']} pending→ready")
            out.append(t)
    save(args.run, data)
    if not out:
        remaining = [t["id"] for t in data["tasks"] if t["status"] != "done"]
        hint = " (승인 전: 조사·구조·비평·문서 리뷰 외는 approve 뒤에)" if planning else ""
        print("투입 가능한 task 없음." + (f" 미완료: {', '.join(remaining)}" if remaining else " 전부 완료.") + hint)
        return
    for t in out:
        extra = f"\ttarget={t['target']} r{t['round']}" if t.get("target") else ""
        print(f"{t['id']}\t{t['agent']}\t{t['title']}{extra}")


def cmd_set(args):
    data = load(args.run)
    t = task_of(data, args.id)
    cur, new = t["status"], args.status
    if new not in STATUSES:
        sys.exit(f"알 수 없는 상태: {new}")
    if new not in TRANSITIONS[cur]:
        sys.exit(f"허용되지 않는 전이: {cur} → {new}")
    if new == "running":
        t["attempts"] += 1
    if new == "done" and t.get("fixes"):
        tt = task_of(data, t["target"])
        still = [f["id"] for f in tt["findings"] if f["id"] in t["fixes"] and f["status"] == "open"]
        if still:
            sys.exit(f"고치기로 한 finding이 아직 open이라 done 불가: {', '.join(still)}  (finding resolve 먼저)")
    t["status"] = new
    log(data, f"{args.id} {cur}→{new}" + (f": {args.note}" if args.note else ""), args.because)
    if all(x["status"] == "done" for x in data["tasks"]):
        data["status"] = "done"
        log(data, "run done")
    elif data["status"] == "done":
        data["status"] = "approved"
    save(args.run, data)
    print(f"{args.id}: {cur} → {new}")


def cmd_finding(args):
    data = load(args.run)
    t = task_of(data, args.id)
    if args.op == "add":
        if args.severity not in SEVERITIES:
            sys.exit(f"severity는 {SEVERITIES} 중 하나")
        if any(f["id"] == args.fid for f in t["findings"]):
            sys.exit(f"중복 finding: {args.fid}")
        t["findings"].append({
            "id": args.fid, "severity": args.severity, "text": args.text or "",
            "status": "open",
        })
        log(data, f"{args.id} finding {args.fid} ({args.severity})")
    else:
        for f in t["findings"]:
            if f["id"] == args.fid:
                f["status"] = "resolved" if args.op == "resolve" else "waived"
                if args.note:
                    f["note"] = args.note
                log(data, f"{args.id} {args.fid} {f['status']}")
                break
        else:
            sys.exit(f"finding 없음: {args.fid}")
    save(args.run, data)
    print("ok")


def cmd_brief(args):
    """브리프에 옮길 것만 뽑는다. 리더가 원장을 손으로 뒤지지 않게."""
    data = load(args.run)
    t = task_of(data, args.id)
    out = {k: t[k] for k in ("id", "agent", "title", "paths", "acceptance", "round") if k in t}
    for k in ("target", "fixes"):
        if k in t:
            out[k] = t[k]
    out["depends"] = [
        {"id": d, "title": task_of(data, d)["title"], "paths": task_of(data, d)["paths"], "report": task_of(data, d)["report"]}
        for d in t.get("depends_on", [])
    ]
    if t.get("target"):
        tt = task_of(data, t["target"])
        out["target_task"] = {"agent": tt["agent"], "paths": tt["paths"], "report": tt["report"],
                              "open_findings": [f for f in tt["findings"] if f["status"] == "open"]}
    out["worktree"] = f".worktrees/{(t.get('target') or t['id']).lower()}"
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_approve(args):
    data = load(args.run)
    errs = validate(data)
    if errs:
        print("\n".join("✗ " + e for e in errs))
        sys.exit("유효하지 않은 원장은 승인할 수 없다")
    if not data["tasks"]:
        sys.exit("task가 없다")
    data["status"] = "approved"
    log(data, "approved")
    save(args.run, data)
    print("승인 기록됨")


def cmd_show(args):
    data = load(args.run)
    print(f"run: {data['run']}  status: {data['status']}  request: {data['request']}")
    if data.get("gaps"):
        print("gaps:")
        for g in data["gaps"]:
            print(f"  {g.get('id','?')} [{g.get('kind','?')}] {g.get('item','')} → {g.get('resolution','미결')}")
    print(f"{'id':<8}{'status':<9}{'agent':<19}{'target':<10}{'deps':<14}{'findings':<12}title")
    for t in data["tasks"]:
        open_f = sum(1 for f in t["findings"] if f["status"] == "open")
        fs = f"{open_f} open/{len(t['findings'])}" if t["findings"] else "-"
        tg = f"{t['target']} r{t['round']}" if t.get("target") else "-"
        print(f"{t['id']:<8}{t['status']:<9}{t['agent']:<19}{tg:<10}{','.join(t['depends_on']) or '-':<14}{fs:<12}{t['title']}")
        if args.paths:
            for p in t["paths"]:
                print(f"{'':<8}  paths: {p}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init"); p.add_argument("run"); p.add_argument("--request", required=True); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("add"); p.add_argument("run"); p.add_argument("id"); p.add_argument("--agent", required=True)
    p.add_argument("--title", required=True); p.add_argument("--paths", required=True); p.add_argument("--depends")
    p.add_argument("--accept", action="append"); p.add_argument("--because")
    p.add_argument("--target"); p.add_argument("--fixes"); p.set_defaults(fn=cmd_add)
    p = sp.add_parser("validate"); p.add_argument("run"); p.set_defaults(fn=cmd_validate)
    p = sp.add_parser("ready"); p.add_argument("run"); p.set_defaults(fn=cmd_ready)
    p = sp.add_parser("set"); p.add_argument("run"); p.add_argument("id"); p.add_argument("status"); p.add_argument("--note"); p.add_argument("--because"); p.set_defaults(fn=cmd_set)
    p = sp.add_parser("finding"); p.add_argument("run"); p.add_argument("id"); p.add_argument("op", choices=["add", "resolve", "waive"])
    p.add_argument("fid"); p.add_argument("severity", nargs="?"); p.add_argument("text", nargs="?"); p.add_argument("--note"); p.set_defaults(fn=cmd_finding)
    p = sp.add_parser("brief"); p.add_argument("run"); p.add_argument("id"); p.set_defaults(fn=cmd_brief)
    p = sp.add_parser("approve"); p.add_argument("run"); p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("show"); p.add_argument("run"); p.add_argument("--paths", action="store_true"); p.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
