#!/usr/bin/env bash
# UserPromptSubmit: inject a gstack checkpoint reminder when the prompt matches.
p=$(jq -r '.prompt // empty' | tr '[:upper:]' '[:lower:]')
if grep -Eq '\b(batch|sweep|full run|main run|launch|all models|all seeds|branches|base runs)\b' <<<"$p"; then
  echo "Checkpoint: paid OpenRouter batch ahead. If PREREG.md has no /eval-plan pilot entry for this config, run /eval-plan first, and call cartel.registry.guard_batch before launching."
fi
if grep -Eq '\b(error|traceback|exception|nan|wrong|weird|broken|fails?|failing|crash(ed)?|bug)\b' <<<"$p"; then
  echo "Checkpoint: run /investigate and state the root cause before proposing any fix. Log it in logs/ERROR_LOG.md."
fi
exit 0
