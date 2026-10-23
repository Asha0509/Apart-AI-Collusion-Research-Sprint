#!/usr/bin/env bash
# PreToolUse: refuse any tool call that names compute.env or .env (compute.env.example allowed).
input=$(cat)
s=$(jq -r '[.tool_input.command, .tool_input.file_path, .tool_input.path, .tool_input.pattern, .tool_input.glob]
           | map(select(. != null)) | join(" ")' <<<"$input")
if grep -Eq '(compute\.env|(^|[[:space:]/"'"'"'=])\.env)($|[^.[:alnum:]_])' <<<"$s"; then
  echo "Blocked: compute.env/.env hold API keys. Do not read, print, grep or edit them; the harness loads them itself." >&2
  exit 2
fi
exit 0
