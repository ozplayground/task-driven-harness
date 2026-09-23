---
name: git-workflow
description: run과 task의 산출물을 git으로 다루는 방법. task마다 자기 워크트리와 브랜치를 갖고, 리더가 run 브랜치로 모아 develop에 PR로 머지한다. run을 시작할 때, task를 던질 때, task가 끝났을 때, run이 끝났을 때, 릴리스·핫픽스·롤백을 할 때 쓴다. 리더와 산출물을 만드는 에이전트가 모두 따른다. "rebase와 merge 차이가 뭐야" 같은 git 개념 설명 질문에는 사용하지 않는다.
---

# git-workflow

표준 GitFlow(main / develop / feature / release / hotfix)에 **task마다 자기 워크트리와 브랜치**를 더한 것이다. `git switch`는 워킹트리 전체에 걸리므로 에이전트 여럿이 한 워킹트리를 쓰면 task별 브랜치가 불가능하고, 커밋과 리뷰가 서로 섞인다. 그래서 산출물을 만드는 에이전트는 각자의 워크트리에서만 일한다. 리뷰어와 critic은 워크트리를 읽기만 한다.

## 브랜치 모델

| 브랜치 | 분기 원본 | 병합 대상 | 누가 |
|---|---|---|---|
| `main` | — | — | 배포된 상태만. 직접 커밋하지 않는다 |
| `develop` | `main` | — | 통합 기준선. PR 머지로만 바뀐다 (원격이 없으면 리더의 `--no-ff` 로컬 머지) |
| `feature/<run>` | `develop` | `develop` (PR, 머지 커밋) | 리더 |
| `feature/<run>/<task>` | `feature/<run>` | `feature/<run>` (`--no-ff`) | 만드는 에이전트가 커밋, 리더가 머지 |
| `release/<version>` | `develop` | `main`과 `develop` | 리더 |
| `hotfix/<run>` | `main` | `main`과 `develop` | 리더 |

`<run>`은 run 이름(kebab-case), `<task>`는 산출물 task의 ID(소문자), `<version>`은 SemVer다. 재작업은 새 브랜치를 만들지 않고 대상 task의 브랜치와 워크트리를 그대로 쓴다. 워크트리 경로는 `.worktrees/<task>`이고 `.gitignore`에 `.worktrees/`를 넣는다.

## 만드는 에이전트의 규칙

1. **자기 워크트리 밖으로 나가지 않는다.** 그 안에서 `add`와 `commit`은 자유다. `switch`, `checkout`, `merge`, `rebase`, `reset --hard`, `push`는 하지 않는다. 다른 task의 산출물이 필요하면 리더에게 요청한다.
2. **자기 소유 경로만 쓴다.** 커밋 뒤 `git show --name-only`로 소유 경로 밖 파일이 없는지 확인한다.
3. **다른 task의 산출물은 `feature/<run>`을 통해 받는다.** 리더가 머지해서 내려 준다.
4. **커밋 단위는 산출물 하나.** 문서 갱신과 코드는 커밋을 가른다. 중간 커밋은 자유이고, 마지막 커밋이 보고서와 같은 상태여야 한다.
5. **이력을 다시 쓰지 않는다.** `rebase`, `--amend`, `push --force`를 하지 않는다. 잘못된 커밋은 `fix:`로 고치고, 되돌리려면 `revert`.
6. **`main`과 `develop`에서 작업하지 않는다.**
7. **비밀값을 커밋하지 않는다.** 스테이징에 있으면 빼고 리더에게 알린다.
8. 보고서에 마지막 커밋 해시를 적는다. 중단되거나 실패해도 만든 것은 `wip:` 커밋으로 남긴다.

## 커밋 메시지

```
<type>: <한 줄 요약>

<본문 — 왜 (선택)>

Task: <run>/<task>
```

type은 `feat` `fix` `docs` `test` `ci` `build` `refactor` `chore` `merge`(머지 커밋) `sync`(내려 주기 머지 커밋). 재작업 커밋은 본문에 `Rework: T2-F1, T2-F3`처럼 고친 지적 번호를 적는다. `git log --grep="Task: order-page"`로 그 run의 커밋을 찾는다.

한 줄 요약은 50자 안이고 무엇이 바뀌었는지만 말한다. "주문 조회 API 추가", "결제 재시도 설계". 작업 경위, 라운드, 지적 번호 목록, 괄호 안 나열, "사람이 읽게 다시 씀" 같은 말은 넣지 않는다. 경위가 필요하면 본문에 한두 문장. ID는 `Task:`와 `Rework:` 꼬리표에만 있다.

## 리더 작업

### run 시작

```bash
# develop이 없으면 만든다. 커밋이 하나도 없는 저장소면 main에 초기 커밋부터
git switch -c develop main && git push -u origin develop        # push는 원격이 있을 때만
git switch develop && git pull --ff-only origin develop
git switch -c feature/<run>
```

### task 투입

산출물 task마다 워크트리를 만들고 그 경로를 브리프의 작업 위치로 준다. 재작업 task는 대상 task의 워크트리를 그대로 쓰고, 그 사이 `feature/<run>`이 바뀌었으면 내려 준다. 리뷰·비평 task는 워크트리를 만들지 않는다.

```bash
git worktree add -b feature/<run>/<task> .worktrees/<task> feature/<run>
git -C .worktrees/<task> merge --no-ff feature/<run> -m "sync: <무엇을> 내려받음

Task: <run>/<task>"
```

### task 완료 — 검사와 머지

리뷰어는 3-dot diff로 그 task의 기여만 본다. 리더는 리뷰 task가 confirmed로 끝나고(문서면 critic 무이의까지) open finding이 없을 때 머지한다.

```bash
git diff --name-only feature/<run>...feature/<run>/<task>     # 소유 경로 밖 파일이 있으면 머지하지 않는다
git diff feature/<run>...feature/<run>/<task>                 # 리뷰어가 보는 내용
git merge --no-ff feature/<run>/<task> -m "merge: <task> — <요약>

Task: <run>/<task>"
```

머지 충돌은 소유 경로가 겹쳤다는 신호다. 풀지 말고 원장의 경로 검사로 돌아간다.

### run 끝 — 통합

모든 task가 done이고 전체 테스트가 통과한 뒤. 이 run의 유일한 push다.

```bash
git push -u origin feature/<run>
gh pr create --base develop --head feature/<run> --title "<run>" --body "<run 보고서 요약>"
gh pr checks --watch                                          # CI가 있으면 통과를 기다린다. 실패하면 머지하지 않는다
gh pr merge --merge
git switch develop && git pull --ff-only origin develop
#   원격이 없으면: git switch develop && git merge --no-ff feature/<run> -m "merge: <run>"
```

PR 본문은 run 보고서의 요구 대비 결과, 자동 결정, 문제가 있는 것, 미검증을 옮긴다. 저장소에 CI 워크플로가 없으면 PR 체크가 없으므로 리더가 run 브랜치에서 돌린 전체 테스트·린트 결과를 근거로 머지한다. 머지 커밋 해시와 PR 주소를 run 보고서 변경 이력에 덧붙인다.

### 정리

머지된 뒤에만, `-d`로 한다(머지되지 않은 브랜치는 git이 거부한다). `-D`는 쓰지 않는다.

```bash
git worktree remove .worktrees/<task> && git worktree prune
git branch -d feature/<run>/<task>
git branch -d feature/<run>
```

### 릴리스 — 사용자가 요구할 때

`main`과 `develop`으로 가는 머지는 전부 PR이다. 릴리스 브랜치에는 커밋을 싣지 않고 버전은 태그가 기록한다.

```bash
git branch release/<version> develop
git push -u origin release/<version>
gh pr create --base main --head release/<version> --title "release <version>"
gh pr merge --merge
git switch main && git pull --ff-only origin main
git tag -a v<version> -m "release <version>" && git push origin v<version>
gh pr create --base develop --head main --title "sync: release <version>"
gh pr merge --merge
git switch develop && git pull --ff-only origin develop
git branch -d release/<version>
```

### 핫픽스 — 사용자가 요구할 때

통합 지점은 `hotfix/<run>`, task 브랜치는 `hotfix/<run>/<task>`, 리뷰 기준선은 `main...hotfix/<run>`이다. task 워크트리·검사·머지는 feature와 같다.

```bash
git switch main && git pull --ff-only origin main
git switch -c hotfix/<run>
# … task 워크트리·검사·머지 (feature/<run> → hotfix/<run>)
git push -u origin hotfix/<run>
gh pr create --base main --head hotfix/<run> && gh pr merge --merge
git switch main && git pull --ff-only origin main
git tag -a v<patch-version> -m "hotfix <run>" && git push origin v<patch-version>
gh pr create --base develop --head main --title "sync: hotfix <run>" && gh pr merge --merge
git switch develop && git pull --ff-only origin develop
```

### 롤백

```bash
git revert -m 1 <머지 커밋>     # run 하나 또는 task 하나를 통째로 되돌린다
```

## CI 트리거

CI를 만드는 task가 있으면 이 표를 따른다.

| 트리거 | 실행 |
|---|---|
| `feature/**`, `hotfix/**` push, `develop`으로의 PR | lint → typecheck(빌드와 분리되는 스택만) → test → build |
| `develop` push | 위 전체 + 스테이징 배포(있으면) |
| `v*` 태그 | 프로덕션 배포 |
| `main` 직접 push | 차단 |

브랜치 보호(직접 push 금지, PR 필수, CI 필수)는 코드로 강제할 수 없으므로 배포 문서에 "적용해야 할 설정"으로 적는다.
