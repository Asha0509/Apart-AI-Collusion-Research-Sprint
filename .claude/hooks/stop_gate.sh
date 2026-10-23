#!/usr/bin/env bash
# Stop: block on failing fast tests; nudge for a BUILD_LOG entry. Loop-guarded.
input=$(cat)
[[ "$(jq -r '.stop_hook_active // false' <<<"$input")" == "true" ]] && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
log=logs/BUILD_LOG.md
git status --porcelain 2>/dev/null | grep -q '\.py$' || exit 0
out=$(timeout 150 uv run -q pytest -x -q -m "not slow" 2>&1); rc=$?
if [[ $rc -ne 0 && $rc -ne 5 ]]; then
  jq -n --arg r "Fast tests fail (pytest exit $rc). Fix or explain before finishing:
$(tail -n 25 <<<"$out")" '{decision:"block", reason:$r}'
  exit 0
fi
if [[ ! -f $log ]] || [[ -n $(find src scripts starter/algorithmic-pricing-llms/src starter/algorithmic-pricing-llms/experiments_synthetic -name '*.py' -newer "$log" -print -quit 2>/dev/null) ]]; then
  jq -n '{hookSpecificOutput:{hookEventName:"Stop",additionalContext:"Append a dated IST entry to logs/BUILD_LOG.md (template in its header): what changed, file:lines, tests, run_ids, OpenRouter spend, open issues. Errors go to logs/ERROR_LOG.md. Then finish."}}'
fi
exit 0
