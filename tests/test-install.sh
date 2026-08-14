#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
test_root="$(mktemp -d)"

cleanup() {
  case "${test_root}" in
    /tmp/*) rm -rf -- "${test_root}" ;;
    *) printf 'Refusing to remove unexpected test path: %s\n' "${test_root}" >&2 ;;
  esac
}
trap cleanup EXIT

assert_skill_link() {
  local codex_home="$1"
  local skill_name="$2"
  local target_path="${codex_home}/skills/${skill_name}"

  [[ -L "${target_path}" ]]
  [[ "${target_path}" -ef "${repo_root}/${skill_name}" ]]
}

codex_home="${test_root}/codex"
CODEX_HOME="${codex_home}" "${repo_root}/install.sh" >/dev/null
assert_skill_link "${codex_home}" generate-html-report
assert_skill_link "${codex_home}" serve-web-over-ssh

if missing_home_output="$(env -u CODEX_HOME -u HOME "${repo_root}/install.sh" 2>&1)"; then
  printf 'Expected installation to fail when CODEX_HOME and HOME are unavailable.\n' >&2
  exit 1
fi
[[ "${missing_home_output}" == *'Set CODEX_HOME'* ]]

first_target="$(readlink -- "${codex_home}/skills/generate-html-report")"
CODEX_HOME="${codex_home}" "${repo_root}/install.sh" >/dev/null
[[ "$(readlink -- "${codex_home}/skills/generate-html-report")" == "${first_target}" ]]
assert_skill_link "${codex_home}" generate-html-report
assert_skill_link "${codex_home}" serve-web-over-ssh

file_conflict_home="${test_root}/file-conflict"
mkdir -p -- "${file_conflict_home}/skills/generate-html-report"
if CODEX_HOME="${file_conflict_home}" "${repo_root}/install.sh" >/dev/null 2>&1; then
  printf 'Expected installation to fail for an existing non-symlink path.\n' >&2
  exit 1
fi
[[ -d "${file_conflict_home}/skills/generate-html-report" ]]
[[ ! -e "${file_conflict_home}/skills/serve-web-over-ssh" ]]

link_conflict_home="${test_root}/link-conflict"
mkdir -p -- "${link_conflict_home}/skills" "${test_root}/different-skill"
ln -s -- "${test_root}/different-skill" "${link_conflict_home}/skills/generate-html-report"
if CODEX_HOME="${link_conflict_home}" "${repo_root}/install.sh" >/dev/null 2>&1; then
  printf 'Expected installation to fail for a symlink with a different target.\n' >&2
  exit 1
fi
[[ "$(readlink -- "${link_conflict_home}/skills/generate-html-report")" == "${test_root}/different-skill" ]]
[[ ! -e "${link_conflict_home}/skills/serve-web-over-ssh" ]]

printf 'install.sh tests passed\n'
