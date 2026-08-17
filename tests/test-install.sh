#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
test_root="$(mktemp -d)"
skill_names=(generate-html-report serve-web-over-ssh scientific-figure-making)

cleanup() {
  case "${test_root}" in
    /tmp/*) rm -rf -- "${test_root}" ;;
    *) printf 'Refusing to remove unexpected test path: %s\n' "${test_root}" >&2 ;;
  esac
}
trap cleanup EXIT

skill_source() {
  case "$1" in
    generate-html-report|serve-web-over-ssh) printf '%s/skills/%s\n' "${repo_root}" "$1" ;;
    scientific-figure-making) printf '%s/external/figures4papers/scientific-figure-making\n' "${repo_root}" ;;
    *) return 1 ;;
  esac
}

assert_skill_link() {
  local platform_root="$1"
  local skill_name="$2"
  local target_path="${platform_root}/skills/${skill_name}"

  [[ -L "${target_path}" ]]
  [[ "${target_path}" -ef "$(skill_source "${skill_name}")" ]]
}

codex_home="${test_root}/codex"
claude_home="${test_root}/claude"
CODEX_HOME="${codex_home}" CLAUDE_CONFIG_DIR="${claude_home}" "${repo_root}/install.sh" all >/dev/null
for skill_name in "${skill_names[@]}"; do
  assert_skill_link "${codex_home}" "${skill_name}"
  assert_skill_link "${claude_home}" "${skill_name}"
done

first_target="$(readlink -- "${codex_home}/skills/generate-html-report")"
CODEX_HOME="${codex_home}" CLAUDE_CONFIG_DIR="${claude_home}" "${repo_root}/install.sh" >/dev/null
[[ "$(readlink -- "${codex_home}/skills/generate-html-report")" == "${first_target}" ]]
for skill_name in "${skill_names[@]}"; do
  assert_skill_link "${codex_home}" "${skill_name}"
  assert_skill_link "${claude_home}" "${skill_name}"
done

codex_only_home="${test_root}/codex-only"
unused_claude_home="${test_root}/unused-claude"
CODEX_HOME="${codex_only_home}" CLAUDE_CONFIG_DIR="${unused_claude_home}" \
  "${repo_root}/install.sh" codex >/dev/null
for skill_name in "${skill_names[@]}"; do
  assert_skill_link "${codex_only_home}" "${skill_name}"
done
[[ ! -e "${unused_claude_home}" ]]

claude_only_home="${test_root}/claude-only"
unused_codex_home="${test_root}/unused-codex"
CODEX_HOME="${unused_codex_home}" CLAUDE_CONFIG_DIR="${claude_only_home}" \
  "${repo_root}/install.sh" claude >/dev/null
for skill_name in "${skill_names[@]}"; do
  assert_skill_link "${claude_only_home}" "${skill_name}"
done
[[ ! -e "${unused_codex_home}" ]]

legacy_home="${test_root}/legacy"
mkdir -p -- "${legacy_home}/skills"
ln -s -- "${repo_root}/generate-html-report" "${legacy_home}/skills/generate-html-report"
CODEX_HOME="${legacy_home}" "${repo_root}/install.sh" codex >/dev/null
assert_skill_link "${legacy_home}" generate-html-report

if missing_home_output="$(env -u CODEX_HOME -u CLAUDE_CONFIG_DIR -u HOME "${repo_root}/install.sh" all 2>&1)"; then
  printf 'Expected installation to fail when Agent homes are unavailable.\n' >&2
  exit 1
fi
[[ "${missing_home_output}" == *'CODEX_HOME or HOME'* ]]

file_conflict_codex="${test_root}/file-conflict-codex"
file_conflict_claude="${test_root}/file-conflict-claude"
mkdir -p -- "${file_conflict_claude}/skills/generate-html-report"
if CODEX_HOME="${file_conflict_codex}" CLAUDE_CONFIG_DIR="${file_conflict_claude}" \
  "${repo_root}/install.sh" all >/dev/null 2>&1; then
  printf 'Expected installation to fail for an existing non-symlink path.\n' >&2
  exit 1
fi
[[ -d "${file_conflict_claude}/skills/generate-html-report" ]]
[[ ! -e "${file_conflict_codex}/skills/generate-html-report" ]]

link_conflict_home="${test_root}/link-conflict"
mkdir -p -- "${link_conflict_home}/skills" "${test_root}/different-skill"
ln -s -- "${test_root}/different-skill" "${link_conflict_home}/skills/generate-html-report"
if CODEX_HOME="${link_conflict_home}" "${repo_root}/install.sh" codex >/dev/null 2>&1; then
  printf 'Expected installation to fail for a symlink with a different target.\n' >&2
  exit 1
fi
[[ "$(readlink -- "${link_conflict_home}/skills/generate-html-report")" == "${test_root}/different-skill" ]]
[[ ! -e "${link_conflict_home}/skills/serve-web-over-ssh" ]]

"${repo_root}/install.sh" --help >/dev/null
if "${repo_root}/install.sh" unknown-platform >/dev/null 2>&1; then
  printf 'Expected installation to reject an unknown platform.\n' >&2
  exit 1
fi

printf 'install.sh tests passed\n'
