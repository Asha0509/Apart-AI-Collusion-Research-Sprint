#!/usr/bin/env bash
# =====================================================================================
# One-shot setup for "Swap the Model, Keep the Cartel" (Apart AI Collusion Sprint 2026)
#
#   bash setup.sh                 # full setup
#   SKIP_GSTACK=1 bash setup.sh   # skip gstack
#   SKIP_PLUGINS=1 bash setup.sh  # skip Claude Code plugins / MCP
#
# Safe to re-run (idempotent). Needs: git, curl. macOS / Linux / WSL.
# =====================================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

STARTER_URL="https://github.com/poseidon-research/collusion_hackathon"
GSTACK_URL="https://github.com/garrytan/gstack.git"

g=$'\033[32m'; r=$'\033[31m'; y=$'\033[33m'; b=$'\033[1m'; n=$'\033[0m'
ok()   { echo "  ${g}✔${n} $*"; }
warn() { echo "  ${y}!${n} $*"; }
bad()  { echo "  ${r}✘${n} $*"; }
step() { echo; echo "${b}== $* ==${n}"; }
have() { command -v "$1" >/dev/null 2>&1; }
TODO=()

# ---------------------------------------------------------------------------------- 1
step "1. Prerequisites"
for t in git curl; do have "$t" && ok "$t" || { bad "$t missing — install it first"; exit 1; }; done
if ! have jq; then
  warn "jq missing (hooks need it). Installing…"
  if have brew; then brew install jq
  elif have apt-get; then sudo apt-get install -y jq
  else TODO+=("Install jq (https://jqlang.org/download/) — the Claude hooks need it"); fi
fi
have jq && ok "jq"
if ! have uv; then
  warn "uv missing. Installing…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
have uv && ok "uv $(uv --version | awk '{print $2}')" || { bad "uv install failed"; exit 1; }
have claude && ok "Claude Code CLI" || TODO+=("Install Claude Code: https://code.claude.com (then re-run setup.sh for plugins)")
have node && ok "node $(node --version)" || warn "node/npm not found — pyright-lsp plugin will be skipped (optional)"

# ---------------------------------------------------------------------------------- 2
step "2. Starter repo (vendored as PRE-EXISTING code)"
if [ ! -d starter ]; then
  git clone --depth 1 "$STARTER_URL" starter || { bad "clone failed"; exit 1; }
  STARTER_SHA=$(git -C starter rev-parse HEAD)
  rm -rf starter/.git
  cat > PREEXISTING.md <<EOF
# Pre-existing code (disclosure required by sprint rules)

Everything under \`starter/\` was copied from ${STARTER_URL}
at commit \`${STARTER_SHA}\` on $(date '+%Y-%m-%d %H:%M %Z'). It is NOT sprint work.

Sprint work = everything else in this repo, plus every change to \`starter/\` after the first git
commit ("PRE-EXISTING: starter repo"). Patched functions carry \`# SPRINT-PATCH:\` comments.
See \`git diff <first-commit>..HEAD -- starter/\` for the exact sprint changes.
EOF
  ok "cloned starter @ ${STARTER_SHA:0:7} (provenance in PREEXISTING.md)"
else
  ok "starter/ already present"
fi

# ---------------------------------------------------------------------------------- 3
step "3. Starter environments (algorithmic-pricing-llms + llm-cartel)"
( cd starter && bash ./setup.sh algorithmic-pricing-llms llm-cartel ) && ok "starter envs installed" \
  || warn "starter setup.sh reported problems — read output above"

# ---------------------------------------------------------------------------------- 4
step "4. API key file (starter/compute.env)"
ENVF=starter/compute.env
[ -f "$ENVF" ] || cp starter/compute.env.example "$ENVF"
# Neutralise the variables that would force ONE model on every firm (kills the swap).
for v in LLM_MODEL MODEL_NAME NEBIUS_API_KEY LLM_BASE_URL; do
  if grep -Eq "^${v}=.+" "$ENVF"; then
    sed -i.bak -E "s|^(${v}=.*)|# \1   # disabled by setup.sh (would break the swap)|" "$ENVF" && rm -f "$ENVF.bak"
    warn "commented out ${v} in compute.env"
  fi
done
if grep -Eq '^OPENROUTER_API_KEY=.{10,}' "$ENVF"; then ok "OPENROUTER_API_KEY present"
else TODO+=("Put your key in starter/compute.env:   OPENROUTER_API_KEY=sk-or-...   (top up \$25 at openrouter.ai)"); fi

# ---------------------------------------------------------------------------------- 5
step "5. Project Python env (analysis + tests)"
uv sync -q && ok "uv sync (numpy, pandas, scipy, matplotlib, scienceplots, ruff, pytest, pyright)" \
  || bad "uv sync failed"
chmod +x .claude/hooks/*.sh scripts/*.sh 2>/dev/null
uv run -q pytest -q -m "not slow" && ok "kit self-tests pass" || warn "kit self-tests failed — see above"

# ---------------------------------------------------------------------------------- 6
step "6. Git (first commit = pre-existing code, for clean disclosure)"
if [ ! -d .git ]; then
  git init -q
  git add -A
  git commit -qm "PRE-EXISTING: starter repo + sprint kit scaffolding (no experiment code yet)"
  ok "repo initialised; first commit $(git rev-parse --short HEAD)"
  TODO+=("Create a PRIVATE GitHub repo and push:  gh repo create collusion-sprint --private --source=. --push")
else ok "git repo exists"; fi

# ---------------------------------------------------------------------------------- 7
step "7. gstack (selective use)"
if [ "${SKIP_GSTACK:-0}" = "1" ]; then warn "skipped (SKIP_GSTACK=1)"
else
  if ! have bun; then
    warn "bun missing. Installing…"
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
  fi
  if [ ! -d "$HOME/.claude/skills/gstack" ]; then
    git clone --single-branch --depth 1 "$GSTACK_URL" "$HOME/.claude/skills/gstack"
  fi
  ( cd "$HOME/.claude/skills/gstack" && ./setup --no-browser --no-timeline-stop-hook ) \
    && ok "gstack installed (no browser, no timeline hook; NOT team mode)" \
    || warn "gstack setup failed — project still works without it"
  echo "    Answer 'no' to telemetry if asked. Do NOT add gstack's 'never use claude-in-chrome' line."
fi

# ---------------------------------------------------------------------------------- 8
step "8. Claude Code plugins + MCP"
if [ "${SKIP_PLUGINS:-0}" = "1" ] || ! have claude; then
  warn "skipped — paste the slash commands below inside Claude Code instead"
else
  if have npm; then npm i -g pyright >/dev/null 2>&1 && ok "pyright (global, for pyright-lsp)"; fi
  claude plugin install pyright-lsp@claude-plugins-official >/dev/null 2>&1 \
    && ok "plugin pyright-lsp" || TODO+=("In Claude Code: /plugin install pyright-lsp@claude-plugins-official")
  { claude plugin marketplace add openai/codex-plugin-cc && claude plugin install codex@openai-codex; } >/dev/null 2>&1 \
    && ok "plugin codex (run /codex:setup inside Claude Code; keep review gate OFF)" \
    || TODO+=("In Claude Code: /plugin marketplace add openai/codex-plugin-cc  then  /plugin install codex@openai-codex  then /codex:setup (optional)")
  claude mcp add --transport stdio --scope user arxiv -- uvx arxiv-mcp-server >/dev/null 2>&1 \
    && ok "arXiv MCP (citation checks)" || warn "arXiv MCP already added or failed (optional)"
fi
TODO+=("In Claude Code: /statusline  → show context %, model, session cost")

# ---------------------------------------------------------------------------------- 9
step "9. Modal (optional — parallel runs)"
if have modal; then ok "modal CLI present"
else TODO+=("(optional) uv tool install modal && modal setup   then ask sprint Slack/Discord for the \$50 credit"); fi

# ---------------------------------------------------------------------------------- done
step "DONE — remaining manual steps"
if [ ${#TODO[@]} -eq 0 ]; then ok "nothing left"; else i=1; for t in "${TODO[@]}"; do echo "  $i. $t"; i=$((i+1)); done; fi
cat <<EOF

${b}Next:${n}
  1) bash scripts/smoke.sh          # 5-round test, ~\$0.01 — proves key + model ids work
  2) bash scripts/pilot.sh          # 8 pilot cartels in background (~\$1-2) for the Sat 08:00 IST gate
  3) cd $(pwd) && claude            # open Claude Code here, paste prompt 1 from KICKOFF.md
EOF
