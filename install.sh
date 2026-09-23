#!/usr/bin/env bash
# 하네스를 대상 프로젝트에 설치하거나 갱신한다.
#   ./install.sh <대상 프로젝트 경로>
# 복사는 덮어쓰고, 설정은 합친다. 다시 돌리면 갱신이다.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DST="${1:-}"
if [ -z "$DST" ]; then
  echo "사용법: $0 <대상 프로젝트 경로>" >&2
  exit 1
fi
if [ ! -d "$DST" ]; then
  echo "대상 경로가 없다: $DST" >&2
  exit 1
fi
DST="$(cd "$DST" && pwd)"
if [ "$DST" = "$SRC" ]; then
  echo "하네스 소스 자신에는 설치하지 않는다" >&2
  exit 1
fi

echo "설치: $SRC → $DST"

# 1. 에이전트·스킬 복사 (덮어쓰기)
mkdir -p "$DST/.claude"
rm -rf "$DST/.claude/agents" "$DST/.claude/skills"
cp -R "$SRC/.claude/agents" "$DST/.claude/agents"
cp -R "$SRC/.claude/skills" "$DST/.claude/skills"
echo "  .claude/agents, .claude/skills 복사"

# 2. CLAUDE.md — 없으면 템플릿 복사, 있으면 하네스 절만 덧붙이거나 갱신
MARK_BEGIN="<!-- task-driven-harness begin -->"
MARK_END="<!-- task-driven-harness end -->"
if [ ! -f "$DST/CLAUDE.md" ]; then
  { echo "$MARK_BEGIN"; cat "$SRC/CLAUDE.template.md"; echo "$MARK_END"; } > "$DST/CLAUDE.md"
  echo "  CLAUDE.md 생성"
elif grep -q "$MARK_BEGIN" "$DST/CLAUDE.md"; then
  python3 - "$DST/CLAUDE.md" "$SRC/CLAUDE.template.md" "$MARK_BEGIN" "$MARK_END" <<'EOF'
import sys
p, t, b, e = sys.argv[1:5]
s = open(p, encoding="utf-8").read()
new = b + "\n" + open(t, encoding="utf-8").read() + e
i, j = s.index(b), s.index(e) + len(e)
open(p, "w", encoding="utf-8").write(s[:i] + new + s[j:])
EOF
  echo "  CLAUDE.md 하네스 절 갱신"
else
  { echo; echo "$MARK_BEGIN"; cat "$SRC/CLAUDE.template.md"; echo "$MARK_END"; } >> "$DST/CLAUDE.md"
  echo "  CLAUDE.md에 하네스 절 덧붙임"
fi

# 3. settings.json — 하네스의 settings.json(마켓플레이스·플러그인)을 대상 설정과 합친다
python3 - "$DST/.claude/settings.json" "$SRC/.claude/settings.json" <<'EOF'
import json, os, sys
p, src = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
with open(src, encoding="utf-8") as f:
    mine = json.load(f)
for key in ("extraKnownMarketplaces", "enabledPlugins"):
    data.setdefault(key, {}).update(mine.get(key, {}))
with open(p, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
EOF
echo "  .claude/settings.json 합침 (마켓플레이스·플러그인)"

# 4. .mcp.json — context7 MCP 서버 (기존 서버와 합친다)
python3 - "$DST/.mcp.json" "$SRC/.mcp.json" <<'EOF'
import json, os, sys
p, src = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
with open(src, encoding="utf-8") as f:
    servers = json.load(f)["mcpServers"]
data.setdefault("mcpServers", {}).update(servers)
with open(p, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
EOF
echo "  .mcp.json에 context7 서버 등록"

# 5. .gitignore
touch "$DST/.gitignore"
for line in "_tasks/" ".worktrees/"; do
  grep -qxF "$line" "$DST/.gitignore" || echo "$line" >> "$DST/.gitignore"
done
echo "  .gitignore에 _tasks/, .worktrees/"

# 6. git 확인
if git -C "$DST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "  git 저장소 확인"
else
  echo "  주의: git 저장소가 아니다. git-workflow를 쓰려면 git init이 필요하다"
fi

echo "완료. 대상 프로젝트에서 새 세션을 열어야 하네스가 로드된다. 첫 세션에서 context7 MCP 서버 승인이 한 번 뜬다."
