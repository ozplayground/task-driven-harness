#!/usr/bin/env python3
"""docs/ 경계 검사와 코드 주석 검사. 표준 라이브러리만 사용한다.

`docs/`는 사용자가 받는 최종 산출물이다. 작업 기록은 `_tasks/`에만 있다.
이 스크립트는 그 경계를 기계적으로 검사한다. 리더가 문서 task를 done으로
옮길 때(ledger.py가 자동 호출), 머지 전, run 종료 시에 돌린다.

사용법:
  docs-lint.py docs [경로...]     # 기본 docs/. 위반이 있으면 종료 코드 1
  docs-lint.py code [경로...]     # 코드 파일의 주석 검사. 참조만 있는 주석은 위반

docs 검사 — 위반(종료 1):
  - YAML 머리말, 작성자·작성일·버전·검토자 표
  - task ID(T1, T1-W1), finding 번호(T1-F1, T1-S1), 비판 번호(P-C1)
  - `_tasks/` 경로, 에이전트 이름, "라운드"·"재작업"·"리뷰 반영"·"finding" 같은 진행 기록 어휘
  - 템플릿 안내문 잔재("작성 예:", "각 절 아래의 설명은 …")
docs 검사 — 경고(종료 코드에 영향 없음):
  - 깨진 상대 링크
제외: docs/mandate.md(사용자가 쓴다), docs/runs/(run 보고서는 ID·어휘 검사 제외)

code 검사 — 위반(종료 1):
  - 문서 참조(§3.2, BR-04, REQ-01, docs/… 링크)만 있고 설명이 없는 주석.
    바로 위 줄이 설명 주석이면 참조 줄은 허용한다.
"""
from __future__ import annotations

import glob
import os
import re
import sys

# ---------- docs ----------

AGENT_WORDS = [
    "researcher", "architect", "spec-writer", "ux-designer", "contract-designer",
    "backend-developer", "frontend-developer", "devops", "verifier",
    "critic", "doc-reviewer", "code-reviewer", "investigator",
]
PROGRESS_WORDS = ["라운드", "재작업", "리뷰 반영", "비평 반영", "지적 반영", "finding", "이번 회차", "재검토 결과"]
TEMPLATE_REMNANTS = ["작성 예:", "각 절 아래의 설명은", "문서를 완성할 때 지운다"]
META_ROWS = re.compile(r"^\|\s*(작성자|작성일|버전|검토자|리뷰어|run|task|라운드)\s*\|", re.M)
TASK_ID = re.compile(r"(?<![\w/-])T\d{1,3}(?:-[A-Z]{1,2}\d{1,3})?(?![\w-])")
FINDING_ID = re.compile(r"(?<![\w/-])[A-Z]{1,3}\d{1,3}-[FS]\d{1,3}(?![\w-])")
CRITIQUE_ID = re.compile(r"(?<![\w/-])P-C\d{1,3}(?![\w-])")
ROUND_EN = re.compile(r"\bround\s*\d+\b", re.I)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(#[^)]*)?\)")


def _lines_with(pattern: re.Pattern, text: str):
    for m in pattern.finditer(text):
        yield text.count("\n", 0, m.start()) + 1, m.group(0)


def check_doc(path: str, root: str) -> tuple[list[str], list[str]]:
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    viol, warn = [], []
    if rel.endswith("docs/mandate.md") or rel == "docs/mandate.md":
        return viol, warn
    is_run_report = "/runs/" in f"/{rel}"

    if text.startswith("---"):
        viol.append(f"{rel}:1 YAML 머리말. docs/ 문서는 제목과 참고 문서로 시작한다")
    for m in META_ROWS.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        viol.append(f"{rel}:{ln} 작업 정보 표 행 `{m.group(1)}`. 누가 언제 만들었는지는 git과 원장이 안다")
    for word in TEMPLATE_REMNANTS:
        for ln, line in enumerate(text.splitlines(), 1):
            if word in line:
                viol.append(f"{rel}:{ln} 템플릿 안내문 잔재 `{word}`")
    for ln, line in enumerate(text.splitlines(), 1):
        if "_tasks/" in line:
            viol.append(f"{rel}:{ln} `_tasks/` 참조. 작업 기록은 docs/에서 가리키지 않는다")

    if not is_run_report:
        for ln, s in _lines_with(TASK_ID, text):
            if not FINDING_ID.fullmatch(s):
                viol.append(f"{rel}:{ln} task ID `{s}`")
        for ln, s in _lines_with(FINDING_ID, text):
            viol.append(f"{rel}:{ln} finding 번호 `{s}`")
        for ln, s in _lines_with(CRITIQUE_ID, text):
            viol.append(f"{rel}:{ln} 비판 번호 `{s}`")
        for ln, s in _lines_with(ROUND_EN, text):
            viol.append(f"{rel}:{ln} 라운드 표기 `{s}`")
        for ln, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            for w in PROGRESS_WORDS:
                if w.lower() in low:
                    viol.append(f"{rel}:{ln} 진행 기록 어휘 `{w}`")
            for a in AGENT_WORDS:
                if re.search(rf"(?<![\w-]){re.escape(a)}(?![\w-])", low):
                    viol.append(f"{rel}:{ln} 에이전트 이름 `{a}`")

    base = os.path.dirname(path)
    for m in LINK.finditer(text):
        target = m.group(1)
        if re.match(r"^[a-z]+:", target):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            ln = text.count("\n", 0, m.start()) + 1
            warn.append(f"{rel}:{ln} 깨진 링크 `{target}`")
    key = lambda x: int(x.split(":", 2)[1]) if x.split(":", 2)[1].isdigit() else 0
    return sorted(viol, key=key), warn


def collect(paths: list[str], exts: tuple[str, ...], root: str) -> list[str]:
    out = []
    for p in paths:
        p = p if os.path.isabs(p) else os.path.join(root, p)
        if os.path.isdir(p):
            for dp, dns, fns in os.walk(p):
                dns[:] = [d for d in dns if d not in ("node_modules", ".git", ".worktrees", "_tasks", "dist", "build", ".venv", "venv", "__pycache__")]
                out += [os.path.join(dp, f) for f in fns if f.endswith(exts)]
        else:
            out += [q for q in glob.glob(p, recursive=True) if q.endswith(exts) and os.path.isfile(q)]
    return sorted(set(out))


def cmd_docs(paths: list[str], root: str) -> int:
    files = collect(paths or ["docs"], (".md",), root)
    viol, warn = [], []
    for f in files:
        v, w = check_doc(f, root)
        viol += v
        warn += w
    for w in warn:
        print("! " + w)
    for v in viol:
        print("✗ " + v)
    if viol:
        print(f"\ndocs/ 경계 위반 {len(viol)}건. 만든 에이전트에게 이 출력을 그대로 넘겨 지우게 한다. 판정 task를 만들 일이 아니다.")
        return 1
    print(f"✓ docs 경계 검사 통과 ({len(files)} 파일" + (f", 경고 {len(warn)}" if warn else "") + ")")
    return 0


# ---------- code ----------

CODE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".kts", ".swift", ".rs",
             ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".rb", ".php", ".sh", ".bash", ".zsh", ".sql", ".dart", ".scala", ".vue", ".svelte")
COMMENT_START = re.compile(r"(?:^|\s)(#(?!!)|//|/\*+|\*(?!/)|<!--|--(?!-))\s?(.*)$")
PRAGMA = re.compile(r"^\s*(noqa|type:|pylint|eslint|prettier|ts-ignore|ts-expect-error|@ts-|nolint|pragma|fmt:|TODO|FIXME|-\*-|coding[:=])", re.I)
REF_TOKENS = re.compile(
    r"§\s*[\d.]+|\b(?:REQ|NFR|FN|SCR|BR|MSG|ADR|TC|E)-[\w.\-]+|\b[SC]-\d+\b|docs/[^\s)\]]+|\[[^\]]*\]\([^)]*\)"
    r"|\b(?:see|ref|refs|cf)\b\.?|참고|참조|문서|명세|계약|설계|기능 명세서|요구사항 정의서|결정 기록|:|：|→|->|\(|\)|\[|\]|,|\.|;|/|\*",
    re.I,
)
WORD = re.compile(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9_']{2,}")


STRING_LIT = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")
INLINE_START = re.compile(r"\s(#(?!!)|//|/\*+|--(?!-))\s?(.*)$")


def comment_text(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None
    m = COMMENT_START.match(" " + s) if s[:1] in "#/*<-" else None
    if not m:
        m = INLINE_START.search(STRING_LIT.sub('""', s))
        if not m:
            return None
    body = m.group(2).strip()
    body = re.sub(r"\*/\s*$|-->\s*$", "", body).strip()
    if PRAGMA.match(body):
        return None
    return body


def check_code(path: str, root: str) -> list[str]:
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    viol = []
    prev_substantive = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            body = comment_text(line)
            if body is None:
                prev_substantive = False
                continue
            has_ref = bool(REF_TOKENS.search(body)) and bool(re.search(r"§|-\d|docs/|\]\(", body))
            words = WORD.findall(REF_TOKENS.sub(" ", body))
            substantive = len(words) >= 3
            if has_ref and not substantive and not prev_substantive:
                viol.append(f"{rel}:{ln} 참조만 있는 주석 `{body[:60]}`. 무엇을 왜 하는지 문장으로 적고, 링크는 그 뒤에 참고로 둔다")
            prev_substantive = substantive
    return viol


def cmd_code(paths: list[str], root: str) -> int:
    files = collect(paths or ["src"], CODE_EXTS, root)
    viol = []
    for f in files:
        viol += check_code(f, root)
    for v in viol:
        print("✗ " + v)
    if viol:
        print(f"\n참조만 있는 주석 {len(viol)}건. 주석은 그 자리에서 이해되게 쓴다. 문서 링크는 더 자세히 볼 때 찾아가는 참고일 뿐이다.")
        return 1
    print(f"✓ 코드 주석 검사 통과 ({len(files)} 파일)")
    return 0


def main(argv: list[str]) -> int:
    root = os.environ.get("ORCHESTRATION_ROOT", os.getcwd())
    if len(argv) < 1 or argv[0] not in ("docs", "code"):
        print(__doc__)
        return 2
    return (cmd_docs if argv[0] == "docs" else cmd_code)(argv[1:], root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
